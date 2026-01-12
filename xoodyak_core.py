"""
xoodyak_core.py
Core implementation of Xoodyak AEAD (NIST Lightweight Cryptography)
Contains: Xoodoo[12] Permutation, Cyclist Mode, XoodyakAEAD
"""

class Xoodoo:
    """Xoodoo[12] permutation - 384-bit state"""
    
    ROUNDS = 12
    RC = [
        0x00000058, 0x00000038, 0x000003C0, 0x000000D0,
        0x00000120, 0x00000014, 0x00000060, 0x0000002C,
        0x00000380, 0x000000F0, 0x000001A0, 0x00000012
    ]
    
    @staticmethod
    def rotl32(x, n):
        """Rotate left 32-bit integer"""
        x &= 0xFFFFFFFF
        return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF
    
    def get_plane(self, state, y):
        """Get a plane from the state"""
        return state[y*4:(y+1)*4]
    
    def set_plane(self, state, y, plane):
        """Set a plane in the state"""
        for i in range(4):
            state[y*4 + i] = plane[i]
    
    def plane_shift(self, plane, t, v):
        """Shift and rotate a plane"""
        result = [0] * 4
        for x in range(4):
            shifted = self.rotl32(plane[x], v)
            new_x = (x + t) % 4
            result[new_x] = shifted
        return result
    
    def theta(self, state):
        """Theta step - column parity mixing"""
        A0 = self.get_plane(state, 0)
        A1 = self.get_plane(state, 1)
        A2 = self.get_plane(state, 2)
        
        P = [A0[i] ^ A1[i] ^ A2[i] for i in range(4)]
        
        P_1_5 = self.plane_shift(P, 1, 5)
        P_1_14 = self.plane_shift(P, 1, 14)
        E = [P_1_5[i] ^ P_1_14[i] for i in range(4)]
        
        A0 = [A0[i] ^ E[i] for i in range(4)]
        A1 = [A1[i] ^ E[i] for i in range(4)]
        A2 = [A2[i] ^ E[i] for i in range(4)]
        
        self.set_plane(state, 0, A0)
        self.set_plane(state, 1, A1)
        self.set_plane(state, 2, A2)
    
    def rho_west(self, state):
        """Rho-west step - plane shift west"""
        A0 = self.get_plane(state, 0)
        A1 = self.get_plane(state, 1)
        A2 = self.get_plane(state, 2)
        
        A1 = [A1[(i-1) % 4] for i in range(4)]
        A2 = [self.rotl32(A2[i], 11) for i in range(4)]
        
        self.set_plane(state, 0, A0)
        self.set_plane(state, 1, A1)
        self.set_plane(state, 2, A2)
    
    def iota(self, state, round_idx):
        """Iota step - add round constant"""
        state[0] ^= self.RC[round_idx]
    
    def chi(self, state):
        """Chi step - non-linear layer"""
        A0 = self.get_plane(state, 0)
        A1 = self.get_plane(state, 1)
        A2 = self.get_plane(state, 2)
        
        B0 = [A1[i] & A2[i] for i in range(4)]
        B1 = [A2[i] & A0[i] for i in range(4)]
        B2 = [A0[i] & A1[i] for i in range(4)]
        
        A0 = [A0[i] ^ B0[i] for i in range(4)]
        A1 = [A1[i] ^ B1[i] for i in range(4)]
        A2 = [A2[i] ^ B2[i] for i in range(4)]
        
        self.set_plane(state, 0, A0)
        self.set_plane(state, 1, A1)
        self.set_plane(state, 2, A2)
    
    def rho_east(self, state):
        """Rho-east step - plane shift east"""
        A0 = self.get_plane(state, 0)
        A1 = self.get_plane(state, 1)
        A2 = self.get_plane(state, 2)
        
        A1 = [self.rotl32(A1[i], 1) for i in range(4)]
        A2_temp = [A2[(i-2) % 4] for i in range(4)]
        A2 = [self.rotl32(A2_temp[i], 8) for i in range(4)]
        
        self.set_plane(state, 0, A0)
        self.set_plane(state, 1, A1)
        self.set_plane(state, 2, A2)
    
    def permute(self, state):
        """Execute full Xoodoo[12] permutation"""
        for round_idx in range(self.ROUNDS):
            self.theta(state)
            self.rho_west(state)
            self.iota(state, round_idx)
            self.chi(state)
            self.rho_east(state)


class Cyclist:
    """Cyclist mode - Xoodyak duplex construction"""
    
    R = 16  # Rate (bytes)
    C = 32  # Capacity (bytes)
    
    def __init__(self):
        self.xoodoo = Xoodoo()
        self.state = [0] * 12  # 12 words of 32-bit = 384 bits
    
    def _bytes_to_words(self, data):
        """Convert bytes to 32-bit words (little-endian)"""
        words = []
        for i in range(0, len(data), 4):
            word = 0
            for j in range(min(4, len(data) - i)):
                word |= (data[i + j] << (8 * j))
            words.append(word)
        return words
    
    def _words_to_bytes(self, words, length):
        """Convert 32-bit words to bytes (little-endian)"""
        result = bytearray()
        for word in words:
            for i in range(4):
                result.append((word >> (8 * i)) & 0xFF)
        return bytes(result[:length])
    
    def absorb(self, data, domain=0x03):
        """Absorb data into the state"""
        if len(data) == 0:
            self.state[3] ^= (domain << 24)
            self.xoodoo.permute(self.state)
            return
        
        for i in range(0, len(data), self.R):
            block_size = min(self.R, len(data) - i)
            block = data[i:i + block_size]
            
            # XOR block into state
            words = self._bytes_to_words(block)
            for j, word in enumerate(words):
                self.state[j] ^= word
            
            # Padding and domain separation
            if block_size < self.R:
                pad_word_idx = block_size // 4
                pad_byte_idx = block_size % 4
                self.state[pad_word_idx] ^= (0x01 << (8 * pad_byte_idx))
                self.state[3] ^= (domain << 24)
            else:
                self.state[3] ^= (domain << 24)
            
            # Apply permutation
            self.xoodoo.permute(self.state)
    
    def squeeze(self, length, domain=0x01):
        """Squeeze data from the state"""
        output = bytearray()
        
        while len(output) < length:
            # Extract rate bytes
            rate_bytes = self._words_to_bytes(self.state[:4], self.R)
            bytes_needed = length - len(output)
            output.extend(rate_bytes[:bytes_needed])
            
            # If need more bytes, apply permutation
            if len(output) < length:
                self.state[3] ^= (domain << 24)
                self.xoodoo.permute(self.state)
        
        return bytes(output[:length])


class XoodyakAEAD:
    """Xoodyak AEAD - Authenticated Encryption with Associated Data"""
    
    TAG_LENGTH = 16  # 128-bit tag
    
    def __init__(self, key, nonce, ad=b''):
        """
        Initialize Xoodyak AEAD
        
        Args:
            key: 128-bit key (16 bytes)
            nonce: 128-bit nonce (16 bytes)
            ad: Associated data (optional)
        """
        self.cyclist = Cyclist()
        
        # Key setup: absorb key || nonce
        combined = key + nonce
        self.cyclist.absorb(combined, domain=0x03)
        
        # Absorb associated data
        if ad:
            self.cyclist.absorb(ad, domain=0x03)
    
    def encrypt(self, plaintext):
        """
        Encrypt plaintext
        
        Args:
            plaintext: Data to encrypt (bytes)
            
        Returns:
            (ciphertext, tag): Tuple of ciphertext and authentication tag
        """
        ciphertext = bytearray()
        
        # Encrypt each block
        for i in range(0, len(plaintext), self.cyclist.R):
            block_size = min(self.cyclist.R, len(plaintext) - i)
            plaintext_block = plaintext[i:i + block_size]
            
            # Generate keystream and XOR with plaintext
            keystream = self.cyclist.squeeze(block_size, domain=0x01)
            ciphertext_block = bytes([p ^ k for p, k in zip(plaintext_block, keystream)])
            ciphertext.extend(ciphertext_block)
            
            # Absorb plaintext (NOT ciphertext)
            self.cyclist.absorb(plaintext_block, domain=0x03)
        
        # Generate authentication tag
        tag = self.cyclist.squeeze(self.TAG_LENGTH, domain=0x01)
        
        return bytes(ciphertext), tag
    
    def decrypt(self, ciphertext, tag):
        """
        Decrypt ciphertext and verify tag
        
        Args:
            ciphertext: Data to decrypt (bytes)
            tag: Authentication tag (16 bytes)
            
        Returns:
            (plaintext, is_verified): Tuple of plaintext and verification status
        """
        plaintext = bytearray()
        
        # Decrypt each block
        for i in range(0, len(ciphertext), self.cyclist.R):
            block_size = min(self.cyclist.R, len(ciphertext) - i)
            ciphertext_block = ciphertext[i:i + block_size]
            
            # Generate keystream and XOR with ciphertext
            keystream = self.cyclist.squeeze(block_size, domain=0x01)
            plaintext_block = bytes([c ^ k for c, k in zip(ciphertext_block, keystream)])
            plaintext.extend(plaintext_block)
            
            # Absorb plaintext (NOT ciphertext)
            self.cyclist.absorb(plaintext_block, domain=0x03)
        
        # Verify authentication tag
        computed_tag = self.cyclist.squeeze(self.TAG_LENGTH, domain=0x01)
        is_verified = (computed_tag == tag)
        
        return bytes(plaintext), is_verified