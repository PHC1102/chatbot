"""
Medical Chatbot - Main Application
Refactored with OOP structure
"""
import streamlit as st
from PIL import Image

# Import custom modules
from config.settings import Config
from models.ai_models import ModelManager
from services.chat_service import ChatService
from services.diagnosis_service import DiagnosisService
from ui.components import UIComponents
from utils.helpers import SessionManager, ErrorHandler

class MedicalChatbot:
    """Main Medical Chatbot Application Class"""
    
    def __init__(self):
        """Initialize the application"""
        # Configure Streamlit page
        st.set_page_config(
            page_title="Medical Chatbot",
            page_icon="🩺",
            layout="wide"
        )
        
        # Initialize components
        self.session_manager = SessionManager()
        self.ui_components = UIComponents()
        self.error_handler = ErrorHandler()
        
        # Initialize services and models
        self.model_manager = ModelManager()
        self.chat_service = ChatService()
        
        # Setup
        self._setup_application()
    
    def _setup_application(self):
        """Setup the application"""
        # Initialize session state
        self.session_manager.initialize_session()
        
        # Initialize models
        self.model_manager.initialize_models()
        
        # Get vision model
        vision_model = self.model_manager.get_vision_model()
        
        # Initialize diagnosis service
        self.diagnosis_service = DiagnosisService(vision_model)
    
    def _handle_regular_chat(self):
        """Handle regular chat interactions"""
        prompt = self.ui_components.render_chat_input()
        
        if prompt:
            # Add user message
            self.session_manager.add_message("user", prompt)
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get response from GPT-OSS
            with st.chat_message("assistant"):
                with st.spinner("Đang suy nghĩ..."):
                    messages = self.session_manager.get_messages()
                    api_messages = self.chat_service.prepare_messages_for_api(messages)
                    response = self.chat_service.send_message(api_messages, is_diagnosis=False)
                    st.markdown(response)
                    
                    # Add assistant response to history
                    self.session_manager.add_message("assistant", response)
    
    def _handle_diagnosis_mode(self):
        """Handle diagnosis mode interactions"""
        vision_model = self.model_manager.get_vision_model()
        
        if not vision_model.is_loaded():
            self.error_handler.display_error(Config.MODEL_LOAD_ERROR)
            self.session_manager.set_diagnosis_mode(False)
            return
        
        # Show diagnosis interface
        st.markdown("### 📷 Chế độ chẩn đoán đang hoạt động")
        st.info("🔍 Tải ảnh da liễu lên để bắt đầu phân tích")
        
        # Show file uploader
        uploaded_file = self.ui_components.render_file_uploader()
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            
            # Add user message to chat
            self.diagnosis_service.add_diagnosis_to_chat(image, self.session_manager.get_messages())
            
            # Process diagnosis
            with st.spinner("Đang phân tích ảnh..."):
                success, response_message = self.diagnosis_service.process_image_diagnosis(
                    image, self.session_manager.get_messages()
                )
                
                if success:
                    # Display results in chat
                    self.diagnosis_service.display_diagnosis_in_chat(
                        image, response_message, self.session_manager.get_messages()
                    )
                else:
                    self.error_handler.display_error(response_message)
                    self.session_manager.add_message("assistant", response_message)
            
            # Return to chat mode automatically
            self.session_manager.set_diagnosis_mode(False)
            st.rerun()
    
    def run(self):
        """Main application loop"""
        # Render custom CSS
        self.ui_components.render_custom_css()
        
        # Render header
        self.ui_components.render_header()
        
        # Render diagnosis button
        if self.ui_components.render_diagnosis_button():
            self.session_manager.set_diagnosis_mode(True)
        
        st.markdown("---")
        
        # Render chat history
        messages = self.session_manager.get_messages()
        self.ui_components.render_chat_history(messages)
        
        # Handle different modes
        if self.session_manager.get_diagnosis_mode():
            self._handle_diagnosis_mode()
        else:
            self._handle_regular_chat()
        
        # Render sidebar
        vision_model = self.model_manager.get_vision_model()
        model_status = vision_model.is_loaded()
        self.ui_components.render_sidebar(model_status)

def main():
    """Application entry point"""
    app = MedicalChatbot()
    app.run()

if __name__ == "__main__":
    main()