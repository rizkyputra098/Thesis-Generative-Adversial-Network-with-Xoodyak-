"""
stego_models_pytorch.py
Steganography with PyTorch Models (.pth) - FIXED dengan Size Header
Support untuk enhanced_encoder.pth dan enhanced_decoder.pth
"""

import streamlit as st
import torch
import torch.nn as nn
import numpy as np
from PIL import Image
import io
import os
import struct
from typing import Tuple, Dict


# ============================================================================
# MODEL ARCHITECTURES
# ============================================================================

class ConvBlock(nn.Module):
    """Standard conv block: Conv -> LeakyReLU -> BatchNorm"""
    def __init__(self, in_channels, out_channels, kernel_size=3, padding=1):
        super(ConvBlock, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, padding=padding)
        self.activation = nn.LeakyReLU(0.2, inplace=True)
        self.bn = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        x = self.conv(x)
        x = self.activation(x)
        x = self.bn(x)
        return x


class OutputBlock(nn.Module):
    """Output block: Conv -> Tanh"""
    def __init__(self, in_channels, out_channels=3):
        super(OutputBlock, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, 3, padding=1)

    def forward(self, x):
        return torch.tanh(self.conv(x))


class DenseEncoder(nn.Module):
    """Dense Encoder dengan skip connections"""
    def __init__(self, data_depth=1, hidden_size=32):
        super(DenseEncoder, self).__init__()
        self.data_depth = data_depth
        self.hidden_size = hidden_size
        self.name = "DenseEncoder"

        self.conv1 = ConvBlock(3, hidden_size)
        self.conv2 = ConvBlock(hidden_size + data_depth, hidden_size)
        self.conv3 = ConvBlock(hidden_size * 2 + data_depth, hidden_size)
        self.conv4 = OutputBlock(hidden_size * 3 + data_depth, out_channels=3)

    def forward(self, image, payload):
        x = self.conv1(image)
        x_list = [x]

        x_cat = torch.cat(x_list + [payload], dim=1)
        x = self.conv2(x_cat)
        x_list.append(x)

        x_cat = torch.cat(x_list + [payload], dim=1)
        x = self.conv3(x_cat)
        x_list.append(x)

        x_cat = torch.cat(x_list + [payload], dim=1)
        delta = self.conv4(x_cat)

        stego = image + delta
        stego = torch.clamp(stego, 0.0, 1.0)
        return stego


class DenseDecoder(nn.Module):
    """Dense Decoder dengan skip connections"""
    def __init__(self, data_depth=1, hidden_size=32):
        super(DenseDecoder, self).__init__()
        self.data_depth = data_depth
        self.hidden_size = hidden_size
        self.name = "DenseDecoder"

        self.conv1 = ConvBlock(3, hidden_size)
        self.conv2 = ConvBlock(hidden_size, hidden_size)
        self.conv3 = ConvBlock(hidden_size * 2, hidden_size)
        self.conv4 = nn.Conv2d(hidden_size * 3, data_depth, 3, padding=1)

    def forward(self, stego):
        x = self.conv1(stego)
        x_list = [x]

        x_cat = torch.cat(x_list, dim=1)
        x = self.conv2(x_cat)
        x_list.append(x)

        x_cat = torch.cat(x_list, dim=1)
        x = self.conv3(x_cat)
        x_list.append(x)

        x_cat = torch.cat(x_list, dim=1)
        x = self.conv4(x_cat)
        return x


# ============================================================================
# STEGANOGRAPHY ENGINE
# ============================================================================

class SteganographyEngine:
    """Main class untuk load dan gunakan model PyTorch"""
    
    def __init__(self):
        self.device = torch.device("cpu")
        self.encoder = None
        self.decoder = None
        self.models_loaded = False
        self.data_depth = 1
        self.hidden_size = 32
        
    def load_models(self) -> bool:
        """Load model PyTorch dari file .pth"""
        try:
            model_dir = "models"
            encoder_path = os.path.join(model_dir, "enhanced_encoder.pth")
            decoder_path = os.path.join(model_dir, "enhanced_decoder.pth")
            
            if not os.path.exists(encoder_path):
                print(f"❌ Encoder tidak ditemukan: {encoder_path}")
                return False
            
            if not os.path.exists(decoder_path):
                print(f"❌ Decoder tidak ditemukan: {decoder_path}")
                return False
            
            print(f"📂 Model directory: {os.path.abspath(model_dir)}")
            
            print(f"\n🔨 Instantiating encoder architecture...")
            self.encoder = DenseEncoder(
                data_depth=self.data_depth,
                hidden_size=self.hidden_size
            ).to(self.device)
            
            print(f"🔨 Instantiating decoder architecture...")
            self.decoder = DenseDecoder(
                data_depth=self.data_depth,
                hidden_size=self.hidden_size
            ).to(self.device)
            
            print(f"📥 Loading encoder weights...")
            encoder_state = torch.load(encoder_path, map_location=self.device)
            self.encoder.load_state_dict(encoder_state)
            self.encoder.eval()
            print("✅ Encoder loaded successfully!")
            
            print(f"📥 Loading decoder weights...")
            decoder_state = torch.load(decoder_path, map_location=self.device)
            self.decoder.load_state_dict(decoder_state)
            self.decoder.eval()
            print("✅ Decoder loaded successfully!")
            
            self.models_loaded = True
            print("\n✅ All models loaded!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading models: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _pad_to_multiple(self, size: int, multiple: int = 32) -> int:
        """Pad size ke multiple terdekat"""
        return ((size + multiple - 1) // multiple) * multiple

    def preprocess_image(self, image_data: bytes, target_size: int = None) -> Tuple[torch.Tensor, Tuple[int, int], Tuple[int, int]]:
        """Convert image bytes ke tensor dengan padding"""
        try:
            img = Image.open(io.BytesIO(image_data)).convert('RGB')
            original_size = img.size
            
            if target_size is not None:
                img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
            
            width, height = img.size
            
            padded_width = self._pad_to_multiple(width, multiple=32)
            padded_height = self._pad_to_multiple(height, multiple=32)
            
            if padded_width != width or padded_height != height:
                padded_img = Image.new('RGB', (padded_width, padded_height), (255, 255, 255))
                padded_img.paste(img, (0, 0))
                img = padded_img
            
            img_array = np.array(img, dtype=np.float32)
            img_array = img_array / 255.0
            
            img_tensor = torch.from_numpy(img_array).permute(2, 0, 1)
            img_tensor = img_tensor.unsqueeze(0).to(self.device)
            
            actual_size = (padded_width, padded_height)
            
            return img_tensor, original_size, actual_size
        
        except Exception as e:
            raise RuntimeError(f"Error preprocessing image: {str(e)}")
    
    def preprocess_secret(self, secret_data: bytes, image_height: int, image_width: int) -> Tuple[torch.Tensor, int]:
        """Convert secret data ke tensor"""
        try:
            binary_str = ''.join(format(byte, '08b') for byte in secret_data)
            
            total_available_bits = image_height * image_width * 1
            
            if len(binary_str) < total_available_bits:
                binary_str = binary_str + '0' * (total_available_bits - len(binary_str))
            else:
                binary_str = binary_str[:total_available_bits]
            
            secret_array = np.array([float(bit) for bit in binary_str], dtype=np.float32)
            secret_array = secret_array.reshape(1, 1, image_height, image_width)
            
            secret_tensor = torch.from_numpy(secret_array).to(self.device)
            
            return secret_tensor, len(binary_str)
        
        except Exception as e:
            raise RuntimeError(f"Error preprocessing secret: {str(e)}")
    
    def postprocess_image(self, output_tensor: torch.Tensor) -> bytes:
        """Convert output tensor kembali ke image bytes"""
        try:
            output_tensor = output_tensor.detach().cpu()
            output_tensor = output_tensor.squeeze(0)
            
            output_array = (output_tensor.permute(1, 2, 0).numpy() * 255.0)
            output_array = np.clip(output_array, 0, 255).astype(np.uint8)
            
            output_image = Image.fromarray(output_array, 'RGB')
            
            output_bytes = io.BytesIO()
            output_image.save(output_bytes, format='PNG')
            output_bytes.seek(0)
            
            return output_bytes.getvalue()
        
        except Exception as e:
            raise RuntimeError(f"Error postprocessing image: {str(e)}")
    
    def postprocess_secret(self, output_tensor: torch.Tensor, bit_length: int) -> bytes:
        """Convert output tensor kembali ke bytes"""
        try:
            output_array = output_tensor.detach().cpu().numpy().flatten()
            binary_array = (output_array > 0.5).astype(int)
            
            recovered_bytes = bytearray()
            for i in range(0, min(bit_length, len(binary_array)), 8):
                byte_bits = ''.join(str(int(b)) for b in binary_array[i:i+8])
                if len(byte_bits) == 8:
                    recovered_bytes.append(int(byte_bits, 2))
            
            return bytes(recovered_bytes)
        
        except Exception as e:
            raise RuntimeError(f"Error postprocessing secret: {str(e)}")
    
    def calculate_psnr(self, original: torch.Tensor, stego: torch.Tensor) -> float:
        """Hitung PSNR antara original dan stego image"""
        try:
            with torch.no_grad():
                original = torch.clamp(original, 0, 1)
                stego = torch.clamp(stego, 0, 1)
                
                mse = torch.mean((original - stego) ** 2)
                
                if mse == 0:
                    return float('inf')
                
                psnr = 10.0 * torch.log10(1.0 / mse)
                
                return psnr.item()
        
        except Exception as e:
            print(f"⚠️ Error calculating PSNR: {e}")
            return 0.0
    
    def hide_encrypted_data(self, cover_image_data: bytes, 
                           encrypted_data: bytes, 
                           max_resolution: int = None) -> Tuple[bytes, Dict]:
        """
        Sembunyikan data dengan SIZE HEADER (FIX)
        Format: [4 bytes: SIZE] [N bytes: DATA]
        """
        if not self.models_loaded:
            raise RuntimeError("❌ Models belum di-load!")
        
        try:
            with torch.no_grad():
                # ===== NEW: Buat SIZE HEADER =====
                data_size = len(encrypted_data)
                size_header = struct.pack('>I', data_size)
                payload = size_header + encrypted_data
                
                print(f"📝 Original data: {data_size} bytes")
                print(f"📦 Payload (with header): {len(payload)} bytes")
                
                cover_tensor, original_size, actual_size = self.preprocess_image(
                    cover_image_data, 
                    target_size=max_resolution
                )
                
                batch_size, channels, height, width = cover_tensor.shape
                
                print(f"📐 Original input: {original_size[0]}x{original_size[1]}")
                print(f"🔧 Padded to: {width}x{height}")
                print(f"📦 Payload size: {len(payload)} bytes")
                print(f"💾 Capacity: {(width * height) // 8} bytes")
                
                secret_tensor, bit_length = self.preprocess_secret(
                    payload,
                    image_height=height,
                    image_width=width
                )
                
                stego_tensor = self.encoder(cover_tensor, secret_tensor)
                
                psnr = self.calculate_psnr(cover_tensor, stego_tensor)
                mse = torch.mean((cover_tensor - stego_tensor) ** 2).item()
                
                stego_image_bytes = self.postprocess_image(stego_tensor)
                
                metrics = {
                    'psnr': float(psnr),
                    'mse': float(mse),
                    'quality': 'Excellent' if psnr > 40 else 'Good' if psnr > 30 else 'Fair',
                    'image_size': len(stego_image_bytes),
                    'data_size': len(encrypted_data),
                    'payload_size': len(payload),
                    'resolution': f'{width}x{height}',
                    'has_size_header': True,
                }
                
                return stego_image_bytes, metrics
        
        except Exception as e:
            print(f"❌ Error saat embedding: {str(e)}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"❌ Error: {str(e)}")
    
    def reveal_encrypted_data(self, stego_image_data: bytes) -> bytes:
        """
        Ekstrak data dengan membaca SIZE HEADER (FIX)
        """
        if not self.models_loaded:
            raise RuntimeError("❌ Models belum di-load!")
        
        try:
            with torch.no_grad():
                stego_tensor, original_size, actual_size = self.preprocess_image(stego_image_data)
                
                batch_size, channels, height, width = stego_tensor.shape
                
                print(f"📐 Extracted from: {width}x{height}")
                
                secret_tensor = self.decoder(stego_tensor)
                
                full_bit_length = width * height
                
                full_extracted = self.postprocess_secret(
                    secret_tensor.squeeze(), 
                    full_bit_length
                )
                
                print(f"📥 Full extraction: {len(full_extracted)} bytes")
                
                # ===== NEW: Baca SIZE HEADER =====
                if len(full_extracted) < 4:
                    print("⚠️ Data terlalu pendek!")
                    return full_extracted
                
                size_bytes = full_extracted[0:4]
                try:
                    data_size = struct.unpack('>I', size_bytes)[0]
                    print(f"📋 Size header: {data_size} bytes")
                except:
                    print("⚠️ Gagal membaca size header")
                    return full_extracted
                
                if data_size < 1 or data_size > 1000000:
                    print(f"⚠️ Size invalid: {data_size}")
                    return full_extracted
                
                encrypted_data = full_extracted[4:4+data_size]
                
                if len(encrypted_data) != data_size:
                    print(f"⚠️ Incomplete: expected {data_size}, got {len(encrypted_data)}")
                else:
                    print(f"✅ Extracted: {len(encrypted_data)} bytes (sesuai size header)")
                
                return encrypted_data
        
        except Exception as e:
            print(f"❌ Error saat extraction: {str(e)}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"❌ Error: {str(e)}")


# ============================================================================
# STREAMLIT FUNCTIONS
# ============================================================================

@st.cache_resource(show_spinner=False)
def load_stego_models() -> Tuple[SteganographyEngine, bool]:
    """Load dan cache model steganography"""
    st.write("🔄 Loading steganography models...")
    engine = SteganographyEngine()
    success = engine.load_models()
    return engine, success


def hide_encrypted_data(cover_image_data: bytes, encrypted_data: bytes, max_resolution: int = None) -> Tuple[bytes, Dict]:
    """Public function untuk sembunyikan data"""
    if 'stego_engine' not in st.session_state:
        raise RuntimeError("❌ Steganography engine tidak tersedia")
    
    engine = st.session_state.stego_engine
    return engine.hide_encrypted_data(cover_image_data, encrypted_data, max_resolution=max_resolution)


def reveal_encrypted_data(stego_image_data: bytes) -> bytes:
    """Public function untuk ekstrak data"""
    if 'stego_engine' not in st.session_state:
        raise RuntimeError("❌ Steganography engine tidak tersedia")
    
    engine = st.session_state.stego_engine

    return engine.reveal_encrypted_data(stego_image_data)
