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
        Render diagnosis button
        
        Returns:
            bool: True if button was clicked
        """
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            return st.button("🔬 Chẩn đoán bệnh da liễu", type="primary", use_container_width=True)
    
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
    def render_chat_input():
        """
        Render chat input
        
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
            # Diagnosis toggle button at top
            st.markdown("### 🔬 Chức năng")
            # This will be handled in main app
            
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
                max-width: 1200px;
                margin: 0 auto;
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