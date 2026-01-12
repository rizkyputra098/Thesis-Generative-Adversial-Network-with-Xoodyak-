"""
pages/home.py - Homepage dengan pilihan Enkripsi/Dekripsi
"""

import streamlit as st


def render():
    # Hero Section
    st.markdown("""
    <div class="hero">
        <h1 class="hero-title">Supercharge Your Data Security</h1>
        <p class="hero-subtitle">
            Model Steganografi Berbasis GAN dengan Enkripsi Xoodyak. 
            Keamanan tingkat tinggi dengan performa optimal dan interface modern.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    
    # Two main options
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        opt_col1, opt_col2 = st.columns(2, gap="large")
        
        with opt_col1:
            if st.button("", key="encrypt_btn", use_container_width=True):
                st.session_state.page = 'encrypt'
                st.rerun()
            
            st.markdown("""
            <div class="option-card">
                <div class="option-icon">🔐</div>
                <div class="option-title">ENKRIPSI</div>
                <div class="option-desc">
                    Amankan file dan teks Anda dengan enkripsi Xoodyak AEAD. 
                    Proteksi data dengan standar kriptografi terkini.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with opt_col2:
            if st.button("", key="decrypt_btn", use_container_width=True):
                st.session_state.page = 'decrypt'
                st.rerun()
            
            st.markdown("""
            <div class="option-card">
                <div class="option-icon">🔓</div>
                <div class="option-title">DEKRIPSI</div>
                <div class="option-desc">
                    Kembalikan file terenkripsi ke bentuk aslinya dengan aman. 
                    Verifikasi integritas data otomatis.
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 5rem 0;'></div>", unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
       st.markdown("""
    <div style="text-align: center; padding: 1.5rem;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🧠</div>
        <div style="color: #64b5f6; font-weight: 600; margin-bottom: 0.5rem;">Intelligent</div>
        <div style="color: #b0bec5; font-size: 0.85rem;">
            Pemanfaatan deep learning untuk penyisipan data adaptif
        </div>
    </div>
    """, unsafe_allow_html=True)
       
    with col2:
      st.markdown("""
    <div style="text-align: center; padding: 1.5rem;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎭</div>
        <div style="color: #64b5f6; font-weight: 600; margin-bottom: 0.5rem;">Stealthy</div>
        <div style="color: #b0bec5; font-size: 0.85rem;">
            Media stego sulit dibedakan dari media asli
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with col3:
       st.markdown("""
    <div style="text-align: center; padding: 1.5rem;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔁</div>
        <div style="color: #64b5f6; font-weight: 600; margin-bottom: 0.5rem;">Reliable</div>
        <div style="color: #b0bec5; font-size: 0.85rem;">
            Proses ekstraksi data yang konsisten dan stabil
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with col4:
         st.markdown("""
    <div style="text-align: center; padding: 1.5rem;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">✨</div>
        <div style="color: #64b5f6; font-weight: 600; margin-bottom: 0.5rem;">User-Friendly</div>
        <div style="color: #b0bec5; font-size: 0.85rem;">
            Antarmuka sederhana untuk eksperimen dan evaluasi
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
    
   # Footer
    st.markdown("""
    <div class="footer">
        <strong>Hybrid Generative Adversarial Network System</strong><br>
        Secure Data Embedding and Extraction Framework<br>
        Final Project Implementation
    </div>
    """, unsafe_allow_html=True)


