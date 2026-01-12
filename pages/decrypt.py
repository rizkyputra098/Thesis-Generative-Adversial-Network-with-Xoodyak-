"""
pages/decrypt.py - Sequential Two-Stage Process with Visual Comparisons
Stage 1: Upload Image → Extract → Show Comparison
Stage 2: Decrypt with Password → Show Result with Hash
"""

import streamlit as st
from PIL import Image
import io
import time
from xoodyak_utils import decrypt_file, calculate_hash
from stego_models_pytorch import reveal_encrypted_data


def get_mime_type(extension: str) -> str:
    """Get MIME type berdasarkan extension"""
    mime_types = {
        'txt': 'text/plain',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'jpg': 'image/jpeg',
        'png': 'image/png',
    }
    return mime_types.get(extension.lower(), 'application/octet-stream')


def decode_file_extension(data: bytes, offset: int):
    if len(data) < offset + 1:
        return 'txt', offset
    
    ext_len = data[offset]
    
    # Validasi: extension MAX 10 karakter (safety)
    if ext_len == 0 or ext_len > 10:
        return 'txt', offset
    
    ext = data[offset+1:offset+1+ext_len].decode('ascii', errors='ignore')
    
    # Validasi: hanya alphanumeric (txt, jpg, png, docx, etc)
    if not all(c.isalnum() for c in ext):
        return 'txt', offset
    
    return ext.lower(), offset + 1 + ext_len


def format_bytes(bytes_size):
    """Format bytes to readable format"""
    for unit in ['B', 'KB', 'MB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} GB"


def render():
    # Initialize state
    if 'decrypt_stage' not in st.session_state:
        st.session_state.decrypt_stage = 1  # 1, 1.5, 2, 2.5
    
    if st.button("← Kembali ke Home"):
        st.session_state.page = 'home'
        st.session_state.decrypt_stage = 1
        keys_to_clear = ['decrypt_result', 'decrypt_filename', 'is_verified', 'post_hash', 'stego_preview', 
                        'file_extension', 'perf_metrics', 'extracted_data', 'temp_stego_image', 'temp_stego_name']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1 style="font-size: 2.5rem; font-weight: 800; 
                   background: linear-gradient(135deg, #64b5f6 0%, #81c784 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;">
            🔓 DEKRIPSI
        </h1>
        <p style="color: #b0bec5; margin-top: 0.5rem;">
            Ekstrak dan dekripsi data dari gambar steganografi
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===================== STAGE 1: INPUT & EXTRACTION =====================
    if st.session_state.decrypt_stage == 1:
        st.markdown("## 📥 STAGE 1: UPLOAD GAMBAR & EKSTRAKSI DATA")
        st.markdown("---")
        
        col_left, col_right = st.columns([1.2, 1], gap="large")
        
        with col_left:
            st.markdown("### INPUT GAMBAR STEGANOGRAFI")
            
            st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Upload gambar dengan data tersembunyi", 
                label_visibility="collapsed",
                type=['png', 'jpg', 'jpeg', 'bmp']
            )
            
            stego_image_data = None
            stego_filename = None
            stego_size_bytes = 0
            
            if uploaded_file:
                try:
                    image_bytes = uploaded_file.read()
                    stego_size_bytes = len(image_bytes)
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
                    
                    st.markdown("**🖼️ Gambar Steganografi**")
                    st.image(image, caption=f"{uploaded_file.name}", use_column_width=True)
                    
                    width, height = image.size
                    st.caption(f"💾 Ukuran file: {format_bytes(stego_size_bytes)} | Resolusi: {width}x{height}")
                    
                    if min(width, height) < 256:
                        st.error(f"⚠️ Resolusi terlalu kecil ({width}x{height}). Minimal 256 pixel.")
                    else:
                        st.markdown(f"""
                        <div class="success-status">
                        ✓ {uploaded_file.name}<br>
                        📊 Resolusi: {width} x {height} px<br>
                        💾 Ukuran: {format_bytes(stego_size_bytes)}
                        </div>
                        """, unsafe_allow_html=True)
                        stego_image_data = image_bytes
                        stego_filename = uploaded_file.name
                        st.session_state['temp_stego_image'] = stego_image_data
                        st.session_state['temp_stego_name'] = stego_filename
                
                except Exception as e:
                    st.error(f"Error membaca gambar: {str(e)}")
            
            st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
            
            if st.button("🧠 EKSTRAK DATA", use_container_width=True, key="extract_button"):
                temp_stego = st.session_state.get('temp_stego_image')
                if not temp_stego:
                    st.error("❌ Silakan upload gambar steganografi")
                else:
                    try:
                        with st.spinner("🧠 Mengekstrak data dengan AI Model..."):
                            start_time = time.time()
                            encrypted_data = reveal_encrypted_data(temp_stego)
                            extraction_time = time.time() - start_time
                            
                            perf_metrics = {
                                'extraction_time': extraction_time,
                                'extracted_size': len(encrypted_data),
                                'extraction_speed': len(encrypted_data) / (extraction_time + 0.001)
                            }
                            
                            if len(encrypted_data) < 33:
                                raise ValueError(f"Data ekstraksi terlalu pendek: {len(encrypted_data)} bytes")
                            
                            st.session_state['extracted_data'] = encrypted_data
                            st.session_state['perf_metrics'] = perf_metrics
                            st.session_state['decrypt_stage'] = 1.5
                            
                            st.success("✅ Ekstraksi berhasil!")
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        with col_right:
            st.markdown("### 📋 INFO EKSTRAKSI")
            st.info("⏳ Upload gambar steganografi, kemudian klik tombol EKSTRAK")
            st.caption("Data terenkripsi akan diekstrak dari gambar")
    
    # ===================== STAGE 1.5: EXTRACTION COMPARISON =====================
    elif st.session_state.decrypt_stage == 1.5:
        st.markdown("## ✅ HASIL EKSTRAKSI - PERBANDINGAN DATA")
        st.markdown("---")
        
        stego_image_data = st.session_state.get('temp_stego_image')
        extracted_data = st.session_state.get('extracted_data', b'')
        perf_metrics = st.session_state.get('perf_metrics', {})
        stego_name = st.session_state.get('temp_stego_name', 'stego.png')
        
        st.markdown("### 📊 PERBANDINGAN GAMBAR & DATA EKSTRAKSI")
        
        col_before, col_after = st.columns(2)
        
        with col_before:
            st.markdown("<p style='text-align: center; color: #64b5f6; font-weight: bold; font-size: 1.2rem;'>🖼️ GAMBAR ASLI (STEGO)</p>", unsafe_allow_html=True)
            st.markdown(f"**Ukuran:** {format_bytes(perf_metrics.get('image_size', len(stego_image_data)) if 'image_size' in perf_metrics else len(stego_image_data))}")
            
            if stego_image_data:
                stego_pil = Image.open(io.BytesIO(stego_image_data))
                st.image(stego_pil, use_column_width=True)
                st.caption(f"File: {stego_name}")
        
        with col_after:
            st.markdown("<p style='text-align: center; color: #81c784; font-weight: bold; font-size: 1.2rem;'>📦 DATA DIEKSTRAK</p>", unsafe_allow_html=True)
            st.markdown(f"**Ukuran:** {format_bytes(len(extracted_data))}")
            
            # Tampilkan extracted data dengan expander - FULL DATA
            extracted_hex = extracted_data.hex().upper()
            
            with st.expander("🔐 Lihat Data Diekstrak (Hex)", expanded=True):
                st.text_area(
                    "Data Terenkripsi (Hexadecimal)",
                    value=extracted_hex,
                    height=350,
                    disabled=True,
                    label_visibility="collapsed"
                )
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        st.markdown("### ⏱️ STATISTIK EKSTRAKSI")
        col_stat_1, col_stat_2, col_stat_3 = st.columns(3)
        
        with col_stat_1:
            st.metric("Waktu Ekstraksi", f"{perf_metrics.get('extraction_time', 0):.3f}s")
        with col_stat_2:
            st.metric("Kecepatan", f"{format_bytes(perf_metrics.get('extraction_speed', 0))}/s")
        with col_stat_3:
            st.metric("Data Diekstrak", format_bytes(perf_metrics.get('extracted_size', 0)))
        
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        
        st.markdown("### 🎯 LANJUT KE TAHAP BERIKUTNYA")
        
        if st.button("🔐 LANJUT KE DEKRIPSI", use_container_width=True, key="proceed_to_decrypt"):
            st.session_state.decrypt_stage = 2
            st.rerun()
        
        if st.button("↺ ULANGI EKSTRAKSI", use_container_width=True, key="restart_extract"):
            st.session_state.decrypt_stage = 1
            st.rerun()
    
    # ===================== STAGE 2: DECRYPTION =====================
    elif st.session_state.decrypt_stage == 2:
        st.markdown("## 🔐 STAGE 2: DEKRIPSI DATA TERENKRIPSI")
        st.markdown("---")
        
        extracted_data = st.session_state.get('extracted_data', b'')
        perf_metrics = st.session_state.get('perf_metrics', {})
        
        col_decrypt_left, col_decrypt_right = st.columns([1.2, 1], gap="large")
        
        with col_decrypt_left:
            st.markdown("### INPUT PASSWORD DEKRIPSI")
            
            st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Masukkan password yang sama saat enkripsi",
                label_visibility="collapsed",
                key="decrypt_password"
            )
            
            st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
            
            if st.button("🔓 DEKRIPSI SEKARANG", use_container_width=True, key="decrypt_button"):
                if not password:
                    st.error("❌ Password diperlukan untuk dekripsi")
                else:
                    try:
                        with st.spinner("⚙️ Mendekripsi data dengan Xoodyak..."):
                            start_time = time.time()
                            try:
                                plaintext, info, is_verified = decrypt_file(extracted_data, password)
                                file_data = plaintext
                                error_msg = None
                            except Exception as e:
                                st.warning(f"⚠️ Autentikasi gagal, mencoba extract...")
                                
                                from xoodyak_core import XoodyakAEAD
                                from xoodyak_utils import derive_key
                                
                                version = extracted_data[0:1]
                                nonce = extracted_data[1:17]
                                tag = extracted_data[17:33]
                                ciphertext = extracted_data[33:]
                                
                                key = derive_key(password.strip())
                                aead = XoodyakAEAD(key, nonce, b'')
                                plaintext, is_verified = aead.decrypt(ciphertext, tag)
                                
                                file_data = plaintext
                                error_msg = f"Data extracted (no verification)"
                                info = {'algorithm': 'Xoodyak AEAD'}
                            
                            decryption_time = time.time() - start_time
                            
                            perf_metrics['decryption_time'] = decryption_time
                            perf_metrics['decrypted_size'] = len(file_data)
                            perf_metrics['decryption_speed'] = len(file_data) / (decryption_time + 0.001)
                            
                            # Extract file extension
                            file_ext, data_offset = decode_file_extension(file_data, 0)
                            actual_data = file_data[data_offset:]
                            
                            post_hash = calculate_hash(actual_data)
                            
                            output_filename = f"decrypted_file.{file_ext}"
                            stego_name = st.session_state.get('temp_stego_name', 'file')
                            if stego_name:
                                base_name = stego_name.rsplit('.', 1)[0]
                                if base_name.endswith('_stego'):
                                    base_name = base_name[:-6]
                                output_filename = f"{base_name}_decrypted.{file_ext}"
                            
                            st.session_state['decrypt_result'] = actual_data
                            st.session_state['decrypt_filename'] = output_filename
                            st.session_state['file_extension'] = file_ext
                            st.session_state['is_verified'] = is_verified
                            st.session_state['post_hash'] = post_hash
                            st.session_state['decrypt_info'] = info
                            st.session_state['error_msg'] = error_msg
                            st.session_state['perf_metrics'] = perf_metrics
                            st.session_state['decrypt_stage'] = 2.5
                            
                            st.success("✅ Dekripsi berhasil!")
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        with col_decrypt_right:
            st.markdown("### 📋 INFO DEKRIPSI")
            st.info("⏳ Masukkan password yang sama dengan saat enkripsi")
            st.caption("Data akan dikembalikan ke bentuk aslinya")
            st.metric("Data Terenkripsi", format_bytes(len(extracted_data)))
    
    # ===================== STAGE 2.5: DECRYPTION RESULT =====================
    elif st.session_state.decrypt_stage == 2.5:
        st.markdown("## ✅ HASIL DEKRIPSI")
        st.markdown("---")
        
        result = st.session_state.get('decrypt_result', b'')
        output_filename = st.session_state.get('decrypt_filename', 'file')
        file_ext = st.session_state.get('file_extension', 'txt')
        is_verified = st.session_state.get('is_verified', False)
        post_hash = st.session_state.get('post_hash', '')
        extracted_data = st.session_state.get('extracted_data', b'')
        perf_metrics = st.session_state.get('perf_metrics', {})
        
        st.markdown("### 📊 PERBANDINGAN DATA SEBELUM & SESUDAH DEKRIPSI")
        
        col_decrypt_before, col_decrypt_after = st.columns(2)
        
        with col_decrypt_before:
            st.markdown("<p style='text-align: center; color: #64b5f6; font-weight: bold; font-size: 1.2rem;'>🔒 SEBELUM DEKRIPSI (ENCRYPTED)</p>", unsafe_allow_html=True)
            st.markdown(f"**Ukuran:** {format_bytes(perf_metrics.get('extracted_size', 0))}")
            
            # Tampilkan encrypted data dengan expander - FULL DATA
            encrypted_hex = extracted_data.hex().upper()
            
            with st.expander("🔐 Lihat Data Terenkripsi (Hex)", expanded=True):
                st.text_area(
                    "Data Terenkripsi (Hexadecimal)",
                    value=encrypted_hex,
                    height=350,
                    disabled=True,
                    label_visibility="collapsed"
                )
        
        with col_decrypt_after:
            st.markdown("<p style='text-align: center; color: #81c784; font-weight: bold; font-size: 1.2rem;'>🔓 SESUDAH DEKRIPSI (PLAINTEXT)</p>", unsafe_allow_html=True)
            st.markdown(f"**Ukuran:** {format_bytes(len(result))}")
            
            # Tampilkan plaintext dengan expander - FULL DATA
            try:
                text_preview = result.decode('utf-8', errors='ignore')
                
                with st.expander("📖 Lihat Data Plaintext Lengkap", expanded=True):
                    st.text_area(
                        "Data Plaintext",
                        value=text_preview,
                        height=350,
                        disabled=True,
                        label_visibility="collapsed"
                    )
            except:
                st.info("(Data binary atau non-text)")
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        st.markdown("### ⏱️ STATISTIK DEKRIPSI")
        col_stat_1, col_stat_2, col_stat_3 = st.columns(3)
        
        with col_stat_1:
            st.metric("Waktu Dekripsi", f"{perf_metrics.get('decryption_time', 0):.3f}s")
        with col_stat_2:
            st.metric("Kecepatan", f"{format_bytes(perf_metrics.get('decryption_speed', 0))}/s")
        with col_stat_3:
            st.metric("Data Hasil", format_bytes(perf_metrics.get('decrypted_size', 0)))
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        st.markdown("### 📋 FILE INFO")
        status_icon = "✅" if is_verified else "⚠️"
        status_text = "VERIFIED" if is_verified else "EXTRACTED"
        
        st.markdown(f"""
        <div class="success-status">
        ✓ Nama File: {output_filename}<br>
        ✓ Ukuran: {format_bytes(len(result))}<br>
        ✓ Tipe: .{file_ext.upper()}<br>
        {status_icon} Status: {status_text}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)
        
        if post_hash:
            st.markdown(f"""
            <div class="hash-label">Hash MD5</div>
            <div class="hash-box">{post_hash}</div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        
        mime_type = get_mime_type(file_ext)
        st.download_button(
            label="⬇️ DOWNLOAD FILE HASIL",
            data=result,
            file_name=output_filename,
            mime=mime_type,
            use_container_width=True,
            help=f"Download file {file_ext.upper()}"
        )
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        if st.button("🔄 MULAI DARI AWAL", use_container_width=True, key="reset_all_decrypt"):
            keys_to_clear = ['decrypt_result', 'decrypt_filename', 'is_verified', 'post_hash', 
                            'file_extension', 'perf_metrics', 'extracted_data', 'temp_stego_image', 
                            'temp_stego_name', 'decrypt_info', 'error_msg']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.decrypt_stage = 1
            st.rerun()