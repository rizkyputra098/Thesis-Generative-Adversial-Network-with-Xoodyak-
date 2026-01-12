#!/usr/bin/env python3
"""
Xoodyak AEAD Brute Force Tool - Streamlit Version
streamlit run app.py
"""

import streamlit as st
import time
from typing import Tuple, Optional

# Import dari aplikasi Anda
try:
    from xoodyak_core import XoodyakAEAD
    from xoodyak_utils import derive_key
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False


def hex_to_bytes(hex_string: str) -> bytes:
    """Convert hex string ke bytes"""
    hex_clean = hex_string.replace(" ", "").replace(":", "").replace("-", "")
    return bytes.fromhex(hex_clean)


def try_decrypt(encrypted_data: bytes, password: str) -> Tuple[bool, Optional[bytes], str]:
    """
    Coba dekripsi dengan password
    Returns: (success, plaintext, message)
    """
    try:
        if len(encrypted_data) < 33:
            return (False, None, f"Data terlalu pendek: {len(encrypted_data)} bytes")
        
        version = encrypted_data[0:1]
        nonce = encrypted_data[1:17]
        tag = encrypted_data[17:33]
        ciphertext = encrypted_data[33:]
        
        key = derive_key(password.strip())
        aead = XoodyakAEAD(key, nonce, b'')
        plaintext, is_verified = aead.decrypt(ciphertext, tag)
        
        if is_verified:
            return (True, plaintext, "✓ Verified")
        elif len(plaintext) > 0:
            return (True, plaintext, "⚠ Not verified but decoded")
        else:
            return (False, None, "Decryption failed")
            
    except Exception as e:
        return (False, None, f"Error: {str(e)[:50]}")


# Page config
st.set_page_config(
    page_title="Xoodyak AEAD Brute Force",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔐 Xoodyak AEAD Brute Force Tool")
st.markdown("Dekripsi data Xoodyak dengan password brute force")

if not MODULES_AVAILABLE:
    st.error("❌ Module xoodyak_core dan xoodyak_utils tidak ditemukan!")
    st.info("Pastikan file ada di directory yang sama dengan aplikasi ini")
    st.stop()

# Initialize session state
if 'attack_result' not in st.session_state:
    st.session_state.attack_result = None
if 'attack_running' not in st.session_state:
    st.session_state.attack_running = False

st.divider()

# Main content area
st.subheader("1️⃣ Input Data Terenkripsi")

col1, col2 = st.columns([2, 1])

with col1:
    hex_input_method = st.radio(
        "Pilih cara input:",
        ["Paste Hex Data", "Contoh Data", "Upload File"],
        horizontal=True
    )

hex_data = ""

if hex_input_method == "Paste Hex Data":
    hex_data = st.text_area(
        "Masukkan hex data (pisahkan dengan spasi atau colon opsional):",
        height=120,
        placeholder="01B82BAD21D6CDADDB6B0122944CB489..."
    )
elif hex_input_method == "Contoh Data":
    hex_data = "01B82BAD21D6CDADDB6B0122944CB489AF9A639A9A8859D8CF2EA7E960F0EC931A59AAA247740D05CD62"
    st.info("ℹ️ Menggunakan data contoh")
else:  # Upload File
    hex_file = st.file_uploader("Upload file hex:", type=["txt", "hex"])
    if hex_file:
        hex_data = hex_file.read().decode('utf-8', errors='ignore').strip()

# Preview hex data
if hex_data:
    try:
        bytes_data = hex_to_bytes(hex_data)
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.metric("Total Bytes", len(bytes_data))
        with col_p2:
            st.metric("Hex Preview", bytes_data[:8].hex().upper()[:16] + "...")
        with col_p3:
            if len(bytes_data) >= 33:
                st.metric("Status", "✅ Valid")
            else:
                st.metric("Status", "❌ Invalid")
    except Exception as e:
        st.error(f"❌ Error parsing hex: {e}")
        hex_data = ""

st.divider()

st.subheader("2️⃣ Input Wordlist (Daftar Password)")

wordlist_method = st.radio(
    "Pilih sumber wordlist:",
    ["Ketik Manual", "Upload File", "Gunakan Preset"],
    horizontal=True
)

wordlist = []

if wordlist_method == "Ketik Manual":
    wordlist_text = st.text_area(
        "Masukkan passwords (satu per baris):",
        height=120,
        placeholder="password\nadmin123\n12345678\nqwerty"
    )
    wordlist = [pwd.strip() for pwd in wordlist_text.split('\n') if pwd.strip()]

elif wordlist_method == "Upload File":
    wordlist_file = st.file_uploader("Upload file wordlist (.txt):", type=["txt"])
    if wordlist_file:
        wordlist = [line.strip() for line in wordlist_file.getvalue().decode('utf-8', errors='ignore').split('\n') if line.strip()]

else:  # Preset
    preset_wordlist = [
        "password", "admin123", "12345678", "qwerty",
        "secret", "dekripsi", "rahasia", "stego",
        "xoodyak", "password123", "admin", "root"
    ]
    wordlist = preset_wordlist.copy()
    
    additional = st.text_area(
        "Tambah password tambahan (opsional, satu per baris):",
        height=80,
        placeholder="custom_password\nanother_one"
    )
    if additional.strip():
        wordlist.extend([pwd.strip() for pwd in additional.split('\n') if pwd.strip()])

# Display wordlist info
if wordlist:
    st.info(f"📝 Total password: **{len(wordlist)}** | Preview: {', '.join(wordlist[:3])}{'...' if len(wordlist) > 3 else ''}")
else:
    st.warning("⚠️ Wordlist masih kosong")

st.divider()

st.subheader("3️⃣ Jalankan Brute Force Attack")

col_start, col_info = st.columns([2, 1])

with col_start:
    start_button = st.button(
        "🚀 MULAI SERANGAN",
        type="primary",
        use_container_width=True,
        disabled=(not hex_data or not wordlist)
    )

with col_info:
    if not hex_data or not wordlist:
        st.caption("⚠️ Lengkapi data terlebih dahulu")
    else:
        st.caption("✅ Siap untuk dijalankan")

# Attack execution
if start_button:
    try:
        encrypted_data = hex_to_bytes(hex_data)
        
        if len(encrypted_data) < 33:
            st.error(f"❌ Data terlalu pendek: {len(encrypted_data)} bytes (minimum 33)")
            st.stop()
        
        st.session_state.attack_running = True
        
        # Create containers for progress and results
        progress_container = st.container()
        results_container = st.container()
        
        with progress_container:
            st.markdown("### 📊 Progress Serangan")
            progress_bar = st.progress(0)
            status_text = st.empty()
            metrics_cols = st.columns(4)
        
        start_time = time.time()
        found = False
        found_password = None
        found_plaintext = None
        found_msg = None
        
        # Loop through wordlist - cari password yang VERIFIED saja
        for i, password in enumerate(wordlist, 1):
            # Update progress
            progress = min(i / len(wordlist), 1.0)
            progress_bar.progress(progress)
            
            elapsed = time.time() - start_time
            speed = i / elapsed if elapsed > 0 else 0
            
            status_text.markdown(f"""
            **Attempt:** {i}/{len(wordlist)} | **Speed:** {speed:.1f} pwd/s | **Elapsed:** {elapsed:.2f}s  
            Current: `{password[:50]}`
            """)
            
            # Try decrypt
            success, plaintext, msg = try_decrypt(encrypted_data, password)
            
            # Hanya perhatikan yang VERIFIED
            if success and "Verified" in msg:
                elapsed = time.time() - start_time
                found = True
                found_password = password
                found_plaintext = plaintext
                found_msg = msg
                
                # Update metrics
                with metrics_cols[0]:
                    st.metric("Status", "✅ DITEMUKAN")
                with metrics_cols[1]:
                    st.metric("Attempt", f"{i}/{len(wordlist)}")
                with metrics_cols[2]:
                    st.metric("Time", f"{elapsed:.2f}s")
                with metrics_cols[3]:
                    st.metric("Speed", f"{speed:.1f} pwd/s")
                
                break
            
            # Update metrics during search
            # if i == 1:
            #     with metrics_cols[0]:
            #         st.metric("Status", "🔍 Mencari...")
            #     with metrics_cols[1]:
            #         st.metric("Attempt", f"{i}/{len(wordlist)}")
            #     with metrics_cols[2]:
            #         st.metric("Time", f"{elapsed:.2f}s")
            #     with metrics_cols[3]:
            #         st.metric("Speed", f"{speed:.1f} pwd/s")
        
        elapsed = time.time() - start_time
        
        # Display results
        results_container.markdown("---")
        
        if found:
            st.success("🎉 PASSWORD DITEMUKAN!", icon="✅")
            
            results_col1, results_col2, results_col3, results_col4 = st.columns(4)
            
            with results_col1:
                st.metric("Password", found_password)
            with results_col2:
                st.metric("Total Attempt", f"{i}/{len(wordlist)}")
            with results_col3:
                st.metric("Total Time", f"{elapsed:.2f}s")
            with results_col4:
                st.metric("Status Dekripsi", found_msg)
            
            st.divider()
            
            # Display decrypted content
            st.subheader("📄 Hasil Dekripsi")
            
            tab_text, tab_hex = st.tabs(["📖 Text View", "🔐 Hex View"])
            
            with tab_text:
                try:
                    text_preview = found_plaintext[:1000].decode('utf-8', errors='ignore')
                    st.text_area(
                        "Plaintext Preview:",
                        value=text_preview,
                        height=300,
                        disabled=True,
                        label_visibility="collapsed"
                    )
                    if len(found_plaintext) > 1000:
                        st.caption(f"... ({len(found_plaintext)} bytes total)")
                except Exception as e:
                    st.info(f"[Binary data - {len(found_plaintext)} bytes]")
            
            with tab_hex:
                hex_preview = found_plaintext[:200].hex().upper()
                st.text_area(
                    "Hex View:",
                    value=hex_preview,
                    height=300,
                    disabled=True,
                    label_visibility="collapsed"
                )
                if len(found_plaintext) > 200:
                    st.caption(f"... ({len(found_plaintext)} bytes total)")
            
            st.divider()
            
            # Determine file type
            try:
                found_plaintext.decode('utf-8')
                detected_ext = "txt"
                detected_mime = "text/plain"
            except:
                detected_ext = "bin"
                detected_mime = "application/octet-stream"
            
            # Download button
            st.download_button(
                label=f"💾 Download File Hasil (.{detected_ext})",
                data=found_plaintext,
                file_name=f"decrypted_data.{detected_ext}",
                mime=detected_mime,
                use_container_width=True
            )
        
        else:
            st.error("❌ Password VERIFIED Tidak Ditemukan", icon="❌")
            
            error_col1, error_col2, error_col3 = st.columns(3)
            
            with error_col1:
                st.metric("Total Attempt", len(wordlist))
            with error_col2:
                st.metric("Total Time", f"{elapsed:.2f}s")
            with error_col3:
                avg_speed = len(wordlist) / elapsed if elapsed > 0 else 0
                st.metric("Avg Speed", f"{avg_speed:.1f} pwd/s")
            
            st.warning(f"⚠️ Dicoba {len(wordlist)} password tapi tidak ada yang VERIFIED dalam waktu {elapsed:.2f} detik")
            st.info("💡 Coba gunakan wordlist yang berbeda atau periksa kembali data terenkripsi Anda")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

st.divider()
st.caption("🔐 Xoodyak AEAD Brute Force Tool | Untuk keperluan pendidikan dan penelitian")