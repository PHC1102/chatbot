"""
UI Components for the medical chatbot
"""
import streamlit as st
from config.settings import Config

class UIComponents:
    """Class containing all UI components"""

    @staticmethod
    def render_header():
        """Render the main header"""
        st.title("🩺 Medical Chatbot")
        st.markdown("---")

    @staticmethod
    def render_diagnosis_button():
        """
        Render diagnosis camera icon button in chat input area
        
        Returns:
            bool: True if button was clicked
        """
        col1, col2 = st.columns([0.1, 0.9])
        
        with col1:
            result = st.button("📷", key="diagnosis-btn", help="Chẩn đoán da liễu")
        
        with col2:
            st.empty()  # This will be used for the chat input
            
        return result

    @staticmethod
    def render_file_uploader():
        """
        Render file uploader for diagnosis
        
        Returns:
            Uploaded file object or None
        """
        st.markdown("### 📷 Upload ảnh da liễu để chẩn đoán")
        
        return st.file_uploader(
            "Chọn ảnh (JPG, JPEG, PNG):",
            type=Config.ALLOWED_IMAGE_TYPES,
            key="diagnosis_uploader"
        )

    @staticmethod
    def render_chat_history(messages):
        """
        Render chat history
        
        Args:
            messages: List of chat messages
        """
        chat_container = st.container()
        with chat_container:
            for message in messages:
                with st.chat_message(message["role"]):
                    if message["role"] == "user" and "image" in message:
                        st.image(message["image"], width=Config.IMAGE_WIDTH)
                    st.markdown(message["content"])

    @staticmethod
    def render_chat_input_with_diagnosis():
        """
        Render chat input with integrated diagnosis button
        
        Returns:
            tuple: (user_input, diagnosis_clicked)
        """
        col1, col2 = st.columns([0.08, 0.92])
        
        with col1:
            diagnosis_clicked = st.button("📷", key="diagnosis-btn", help="Chẩn đoán da liễu", use_container_width=True)
        
        with col2:
            user_input = st.chat_input("Nhập tin nhắn của bạn...")
            
        return user_input, diagnosis_clicked
    
    @staticmethod
    def render_chat_input():
        """
        Render regular chat input (for backward compatibility)
        
        Returns:
            User input string or None
        """
        return st.chat_input("Nhập tin nhắn của bạn...")

    @staticmethod
    def render_sidebar(model_status):
        """
        Render sidebar with information
        
        Args:
            model_status: Boolean indicating if models are loaded
        """
        with st.sidebar:
            st.markdown("### ℹ️ Thông tin")
            st.markdown("""
            **💬 Chat thường:**
            - Luôn sẵn sàng trò chuyện
            - Sử dụng GPT-OSS
            
            **🔬 Chẩn đoán da liễu:**
            - Nhấn nút "Chẩn đoán bệnh da liễu"
            - Upload ảnh → Tự động phân tích
            - Quay lại chat thường sau khi xong
            
            ⚠️ **Lưu ý quan trọng:**
            Kết quả chỉ mang tính tham khảo, 
            không thay thế chẩn đoán y tế chuyên nghiệp.
            """)
            
            if st.button("🗑️ Xóa lịch sử chat"):
                st.session_state.messages = []
                st.rerun()
            
            st.markdown("---")
            st.markdown("**Model đang sử dụng:**")
            st.markdown("- Chat: GPT-OSS")
            st.markdown("- Vision: DinoV2 SkinDisease (Local)")
            
            # Model status indicator
            if model_status:
                st.success("✅ Model đã load thành công")
            else:
                st.error("❌ Model chưa load được")

    @staticmethod
    def render_custom_css():
        """Render custom CSS styling"""
        st.markdown("""
        <style>
            .stApp {
                max-width: 100% !important;
                padding: 0 1rem !important;
            }
            .main .block-container {
                max-width: 100% !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            /* Camera diagnosis button styling - SUPER BEAUTIFUL VERSION */
            div[data-testid="column"]:first-child .stButton > button {
                width: 100% !important;
                height: 3.5rem !important;
                border-radius: 20px !important;
                border: none !important;
                background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 30%, #45b7d1 70%, #96ceb4 100%) !important;
                color: white !important;
                font-size: 1.6rem !important;
                font-weight: bold !important;
                transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important;
                margin-bottom: 0.5rem !important;
                box-shadow: 0 8px 32px rgba(255, 107, 107, 0.4) !important;
                position: relative !important;
                overflow: hidden !important;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
            }
            
            /* Hover effect - even more beautiful */
            div[data-testid="column"]:first-child .stButton > button:hover {
                background: linear-gradient(135deg, #4ecdc4 0%, #45b7d1 30%, #96ceb4 70%, #ff6b6b 100%) !important;
                transform: translateY(-4px) scale(1.05) rotate(2deg) !important;
                box-shadow: 0 15px 40px rgba(78, 205, 196, 0.6) !important;
                animation: pulse 0.6s ease-in-out !important;
            }
            
            /* Active/click effect */
            div[data-testid="column"]:first-child .stButton > button:active {
                transform: translateY(-1px) scale(1.02) !important;
                box-shadow: 0 5px 20px rgba(255, 107, 107, 0.4) !important;
            }
            
            /* Animated background gradient */
            div[data-testid="column"]:first-child .stButton > button::before {
                content: '' !important;
                position: absolute !important;
                top: 0 !important;
                left: -100% !important;
                width: 100% !important;
                height: 100% !important;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent) !important;
                transition: left 0.8s ease !important;
            }
            
            div[data-testid="column"]:first-child .stButton > button:hover::before {
                left: 100% !important;
            }
            
            /* Pulse animation keyframes */
            @keyframes pulse {
                0% { box-shadow: 0 15px 40px rgba(78, 205, 196, 0.6); }
                50% { box-shadow: 0 15px 40px rgba(78, 205, 196, 0.8), 0 0 30px rgba(78, 205, 196, 0.4); }
                100% { box-shadow: 0 15px 40px rgba(78, 205, 196, 0.6); }
            }

            .stChatMessage {
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 1rem;
            }
            
            .stButton > button {
                width: 100%;
                border-radius: 10px;
                border: none;
                background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                font-weight: bold;
                padding: 0.5rem 1rem;
                transition: all 0.3s ease;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .stFileUploader {
                border: 2px dashed #4facfe;
                border-radius: 10px;
                padding: 2rem;
                text-align: center;
            }
        </style>
        """, unsafe_allow_html=True)
