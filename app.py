"""
app.py - Xoodyak AEAD UI dengan Streamlit (Modular) + PyTorch Steganography
Updated untuk menggunakan enhanced_encoder.pth dan enhanced_decoder.pth
"""

import streamlit as st
from pages import home, encrypt, decrypt
from styles import apply_custom_styles
from stego_models_pytorch import SteganographyEngine
import os


# Global model loader with caching
@st.cache_resource(show_spinner=False)
def load_stego_models():
    """
    Load dan cache PyTorch steganography models at startup.
    Models akan di-load sekali dan reused across all sessions.
    """
    engine = SteganographyEngine()
    success = engine.load_models()
    
    if not success:
        return None, False
    
    return engine, True


def check_model_files():
    """Check if PyTorch model files exist before loading"""
    model_dir = "models"
    required_files = ['enhanced_encoder.pth', 'enhanced_decoder.pth']
    
    # Check if models directory exists
    if not os.path.exists(model_dir):
        return False, [f"❌ Folder '{model_dir}/' tidak ditemukan di root project!"]
    
    # Check each model file
    missing_files = []
    for f in required_files:
        full_path = os.path.join(model_dir, f)
        if not os.path.exists(full_path):
            missing_files.append(f"{model_dir}/{f}")
    
    if missing_files:
        return False, missing_files
    
    return True, []


def main():
    st.set_page_config(
        page_title="XOODYAK - Encryption",
        page_icon="⬡",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Apply custom styles
    apply_custom_styles()
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    if 'models_loaded' not in st.session_state:
        st.session_state.models_loaded = False
    
    if 'model_check_done' not in st.session_state:
        st.session_state.model_check_done = False
    
    # ===== MODEL INITIALIZATION =====
    # Only show loading on first run
    if not st.session_state.model_check_done:
        # Check if model files exist
        files_exist, missing_files = check_model_files()
        
        if not files_exist:
            st.error(f"""
            ❌ **MODEL FILES TIDAK DITEMUKAN!**
            
            File yang hilang:
            {chr(10).join(f'• {f}' for f in missing_files)}
            
            **Struktur folder yang benar:**
            ```
            xoodyak/
            ├── app.py
            ├── stego_models_pytorch.py
            ├── pages/
            └── models/              ← Buat folder ini!
                ├── enhanced_encoder.pth
                └── enhanced_decoder.pth
            ```
            
            **Langkah perbaikan:**
            1. Buat folder `models/` di root project Anda
            2. Letakkan file:
               - enhanced_encoder.pth
               - enhanced_decoder.pth
               di dalam folder `models/`
            3. Restart aplikasi dengan: `streamlit run app.py`
            
            **Atau gunakan script copy otomatis:**
            ```bash
            # Jika model ada di folder lain
            cp /path/to/enhanced_encoder.pth ./models/
            cp /path/to/enhanced_decoder.pth ./models/
            ```
            """)
            st.stop()
        
        # Load models with progress indicator
        with st.spinner("🧠 Loading PyTorch Steganography Models..."):
            engine, success = load_stego_models()
            
            if success:
                st.session_state.stego_engine = engine
                st.session_state.models_loaded = True
                st.session_state.model_check_done = True
                
                # Show success message briefly
                success_placeholder = st.empty()
                success_placeholder.success("✅ PyTorch Models loaded successfully!")
                
                # Auto-hide success message after 2 seconds
                import time
                time.sleep(2)
                success_placeholder.empty()
            else:
                st.error("""
                ❌ **GAGAL LOAD PYTORCH MODELS!**
                
                **Kemungkinan penyebab:**
                • File .pth corrupt atau tidak valid
                • PyTorch belum terinstall
                • Versi PyTorch tidak kompatibel
                • CUDA drivers tidak match (jika pakai GPU)
                
                **Solusi:**
                
                1. **Install PyTorch:**
                ```bash
                # CPU only
                pip install torch torchvision
                
                # GPU (CUDA 11.8)
                pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
                
                # GPU (CUDA 12.1)
                pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
                ```
                
                2. **Verify PyTorch Installation:**
                ```python
                import torch
                print(f"PyTorch version: {torch.__version__}")
                print(f"CUDA available: {torch.cuda.is_available()}")
                print(f"Device: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}")
                ```
                
                3. **Verify Model File:**
                ```python
                import torch
                try:
                    model = torch.load('models/enhanced_encoder.pth')
                    print("✅ Model file valid!")
                except Exception as e:
                    print(f"❌ Error: {e}")
                ```
                
                4. **Check Model Compatibility:**
                Model mungkin di-training dengan PyTorch versi tertentu.
                Coba install dengan pip install torch==2.0.0 (sesuaikan versi)
                """)
                st.stop()
    
    # Navbar
    st.markdown("""
    <div class="navbar">
        <div class="logo">⬡ XOODYAK</div>
        <div style="color: #64b5f6; font-size: 0.85rem;">
            Steganografi Berbasis GAN dengan Enkripsi Xoodyak
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show model status indicator
    if st.session_state.models_loaded:
        device_info = "🚀 GPU" if st.session_state.stego_engine.device.type == "cuda" else "⚡ CPU"
        st.markdown(f"""
        <div style="position: fixed; bottom: 20px; right: 20px; 
                    background: rgba(76, 175, 80, 0.2); 
                    padding: 8px 16px; border-radius: 20px;
                    border: 1px solid rgba(76, 175, 80, 0.5);
                    font-size: 0.85rem; color: #81c784;
                    z-index: 9999;">
            🟢 PyTorch Ready ({device_info})
        </div>
        """, unsafe_allow_html=True)
    
    # Route to appropriate page
    if st.session_state.page == 'home':
        home.render()
    elif st.session_state.page == 'encrypt':
        encrypt.render()
    elif st.session_state.page == 'decrypt':
        decrypt.render()


if __name__ == "__main__":
    main()