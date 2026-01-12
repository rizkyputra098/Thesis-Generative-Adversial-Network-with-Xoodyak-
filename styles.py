"""
styles.py - Custom CSS untuk Xoodyak UI
"""

import streamlit as st


def apply_custom_styles():
    st.markdown("""
    <style>
        * {
            margin: 0;
            padding: 0;
        }
        
        html, body, .stApp {
            background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 50%, #0f0f28 100%);
            color: #e0e0e0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            overflow-x: hidden;
        }
        
        /* Starfield background */
        .stApp::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(2px 2px at 20% 30%, #eee, rgba(0,0,0,0)),
                radial-gradient(2px 2px at 60% 70%, #fff, rgba(0,0,0,0)),
                radial-gradient(1px 1px at 50% 50%, #fff, rgba(0,0,0,0)),
                radial-gradient(1px 1px at 80% 10%, #fff, rgba(0,0,0,0)),
                radial-gradient(2px 2px at 90% 60%, #fff, rgba(0,0,0,0)),
                radial-gradient(1px 1px at 30% 80%, #fff, rgba(0,0,0,0));
            background-size: 200% 200%, 150% 150%, 180% 180%, 220% 220%, 250% 250%, 240% 240%;
            background-position: 0% 0%, 40% 60%, 130% 270%, 70% 100%, 150% 140%, 90% 10%;
            background-repeat: repeat;
            opacity: 0.5;
            pointer-events: none;
            z-index: 0;
            animation: twinkle 20s ease-in-out infinite;
        }
        
        @keyframes twinkle {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.7; }
        }
        
        .main {
            position: relative;
            z-index: 1;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {visibility: hidden;}
        
        /* Navbar styling */
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem 3rem;
            background: rgba(10, 14, 39, 0.3);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(100, 200, 255, 0.1);
            margin-bottom: 2rem;
            border-radius: 0;
        }
        
        .logo {
            font-weight: 800;
            font-size: 1.3rem;
            background: linear-gradient(135deg, #64b5f6 0%, #81c784 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 0.1em;
            cursor: pointer;
        }
        
        /* Hero section */
        .hero {
            text-align: center;
            padding: 4rem 2rem 2rem;
            margin-bottom: 3rem;
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: 900;
            line-height: 1.2;
            background: linear-gradient(135deg, #ffffff 0%, #64b5f6 50%, #81c784 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1.5rem;
            animation: fadeInUp 0.8s ease;
        }
        
        .hero-subtitle {
            font-size: 1.1rem;
            color: #b0bec5;
            margin: 0 auto 2rem;
            line-height: 1.6;
            animation: fadeInUp 0.8s ease 0.2s backwards;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Glow ring effect */
        .glow-ring {
            position: relative;
            height: 300px;
            margin: 3rem 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .ring-outer {
            position: absolute;
            width: 250px;
            height: 250px;
            border: 2px solid;
            border-image: linear-gradient(135deg, #64b5f6 0%, #81c784 50%, #64b5f6 100%) 1;
            border-radius: 50%;
            animation: rotate 8s linear infinite;
            filter: drop-shadow(0 0 30px rgba(100, 181, 246, 0.3));
        }
        
        .ring-middle {
            position: absolute;
            width: 180px;
            height: 180px;
            border: 1px solid rgba(129, 199, 132, 0.5);
            border-radius: 50%;
            animation: rotate 12s linear infinite reverse;
            filter: drop-shadow(0 0 20px rgba(129, 199, 132, 0.2));
        }
        
        .ring-inner {
            position: absolute;
            width: 120px;
            height: 120px;
            border: 1px solid rgba(100, 181, 246, 0.3);
            border-radius: 50%;
            animation: rotate 6s linear infinite;
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        /* Card styling */
        .card {
            background: rgba(20, 30, 50, 0.4);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(100, 181, 246, 0.2);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(100, 181, 246, 0.1),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(100, 181, 246, 0.4), transparent);
        }
        
        .card:hover {
            border-color: rgba(100, 181, 246, 0.5);
            box-shadow: 0 12px 48px rgba(100, 181, 246, 0.2),
                        inset 0 1px 0 rgba(255, 255, 255, 0.15);
            background: rgba(20, 30, 50, 0.6);
        }
        
        /* Option card untuk home */
        .option-card {
            background: rgba(20, 30, 50, 0.5);
            backdrop-filter: blur(20px);
            border: 2px solid rgba(100, 181, 246, 0.2);
            border-radius: 24px;
            padding: 3rem 2rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
        }
        
        .option-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(100, 181, 246, 0.6), transparent);
        }
        
        .option-card:hover {
            border-color: rgba(100, 181, 246, 0.6);
            box-shadow: 0 16px 56px rgba(100, 181, 246, 0.25);
            transform: translateY(-8px);
            background: rgba(20, 30, 50, 0.7);
        }
        
        .option-icon {
            font-size: 4rem;
            margin-bottom: 1.5rem;
            filter: drop-shadow(0 4px 20px rgba(100, 181, 246, 0.3));
        }
        
        .option-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #64b5f6;
            margin-bottom: 1rem;
            letter-spacing: 0.05em;
        }
        
        .option-desc {
            color: #b0bec5;
            font-size: 0.95rem;
            line-height: 1.6;
        }
        
        /* Input elements */
        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox select {
            background: rgba(15, 25, 45, 0.6) !important;
            border: 1px solid rgba(100, 181, 246, 0.2) !important;
            border-radius: 12px !important;
            color: #e0e0e0 !important;
            padding: 0.9rem !important;
            font-family: 'Courier New', monospace !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput input:focus,
        .stTextArea textarea:focus {
            border-color: rgba(129, 199, 132, 0.6) !important;
            box-shadow: 0 0 20px rgba(129, 199, 132, 0.2) !important;
            background: rgba(15, 25, 45, 0.8) !important;
        }
        
        /* Button styling */
        .stButton button {
            background: linear-gradient(135deg, #64b5f6 0%, #81c784 100%) !important;
            border: 1px solid rgba(129, 199, 132, 0.4) !important;
            border-radius: 12px !important;
            padding: 1rem 2rem !important;
            color: white !important;
            font-weight: 700 !important;
            letter-spacing: 0.08em !important;
            box-shadow: 0 4px 20px rgba(100, 181, 246, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
            transition: all 0.4s ease !important;
            text-transform: uppercase !important;
            font-size: 0.9rem !important;
        }
        
        .stButton button:hover {
            box-shadow: 0 8px 40px rgba(129, 199, 132, 0.4),
                        inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
            transform: translateY(-2px) !important;
            background: linear-gradient(135deg, #81c784 0%, #64b5f6 100%) !important;
        }
        
        /* Radio buttons */
        .stRadio > div {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .stRadio label {
            background: rgba(25, 35, 60, 0.5) !important;
            border: 1px solid rgba(100, 181, 246, 0.2) !important;
            padding: 0.8rem 1.5rem !important;
            border-radius: 10px !important;
            color: #b0bec5 !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
        }
        
        .stRadio label:has(input:checked) {
            background: linear-gradient(135deg, rgba(100, 181, 246, 0.2), rgba(129, 199, 132, 0.2)) !important;
            border-color: rgba(100, 181, 246, 0.5) !important;
            color: #e0e0e0 !important;
        }
        
        /* Hash display */
        .hash-box {
            background: rgba(15, 25, 45, 0.8);
            border: 1px solid rgba(100, 181, 246, 0.2);
            border-left: 3px solid rgba(100, 181, 246, 0.6);
            padding: 1rem;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 0.7rem;
            word-break: break-all;
            color: #64b5f6;
            margin: 1rem 0;
            line-height: 1.6;
        }
        
        .hash-label {
            color: #90caf9;
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.5rem;
        }
        
        /* Status boxes */
        .success-status {
            background: rgba(129, 199, 132, 0.1);
            border: 1px solid rgba(129, 199, 132, 0.3);
            border-left: 3px solid rgba(129, 199, 132, 0.8);
            padding: 1rem;
            border-radius: 10px;
            color: #81c784;
            margin: 1rem 0;
        }
        
        .error-status {
            background: rgba(239, 83, 80, 0.1);
            border: 1px solid rgba(239, 83, 80, 0.3);
            border-left: 3px solid rgba(239, 83, 80, 0.8);
            padding: 1rem;
            border-radius: 10px;
            color: #ef5350;
            margin: 1rem 0;
        }
        
        .info-status {
            background: rgba(100, 181, 246, 0.1);
            border: 1px solid rgba(100, 181, 246, 0.3);
            border-left: 3px solid rgba(100, 181, 246, 0.8);
            padding: 1rem;
            border-radius: 10px;
            color: #64b5f6;
            margin: 1rem 0;
        }
        
        /* File uploader */
        .stFileUploader {
            background: rgba(15, 25, 45, 0.4) !important;
            border: 2px dashed rgba(100, 181, 246, 0.3) !important;
            border-radius: 14px !important;
            padding: 2rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stFileUploader:hover {
            border-color: rgba(100, 181, 246, 0.6) !important;
            background: rgba(15, 25, 45, 0.6) !important;
        }
        
        /* Metrics */
        .stMetric {
            background: rgba(25, 35, 60, 0.4) !important;
            border: 1px solid rgba(100, 181, 246, 0.15) !important;
            padding: 1.2rem !important;
            border-radius: 12px !important;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            margin-top: 4rem;
            background: rgba(10, 14, 39, 0.3);
            border-top: 1px solid rgba(100, 200, 255, 0.1);
            border-radius: 12px;
            color: #90caf9;
            font-size: 0.85rem;
            line-height: 1.8;
        }
    </style>
    """, unsafe_allow_html=True)