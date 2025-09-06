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
        """Handle regular chat interactions with RAG support"""
        prompt, diagnosis_clicked = self.ui_components.render_chat_input_with_diagnosis()
        
        # Handle diagnosis button click
        if diagnosis_clicked:
            self.session_manager.set_diagnosis_mode(True)
            st.rerun()
        
        if prompt:
            # Add user message
            self.session_manager.add_message("user", prompt)
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get response from GPT-OSS with RAG enhancement
            with st.chat_message("assistant"):
                with st.spinner("Đang suy nghĩ..."):
                    messages = self.session_manager.get_messages()
                    api_messages = self.chat_service.prepare_messages_for_api(messages)
                    # Pass the user query for RAG context retrieval
                    response, relevant_images = self.chat_service.send_message(api_messages, user_query=prompt)
                    
                    # Display relevant disease images first if available
                    if relevant_images:
                        st.markdown("**Hình ảnh minh họa:**")
                        self.ui_components.render_disease_images(relevant_images)
                    
                    # Display text response
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
        
        # Show file uploader
        uploaded_file = self.ui_components.render_file_uploader()
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            
            # Add user message to chat
            self.diagnosis_service.add_diagnosis_to_chat(image, self.session_manager.get_messages())
            
            # Process diagnosis
            with st.spinner("Đang phân tích ảnh..."):
                success, response_message, diagnosis_images = self.diagnosis_service.process_image_diagnosis(
                    image, self.session_manager.get_messages()
                )
                
                if success:
                    # Display results in chat and get primary disease name
                    primary_disease = self.diagnosis_service.display_diagnosis_in_chat(
                        image, response_message, self.session_manager.get_messages(), diagnosis_images
                    )
                    
                    # Show quick question popup if a disease was identified
                    if primary_disease:
                        question_clicked = self.ui_components.render_quick_question_popup(primary_disease)
                        
                        if question_clicked:
                            # Add the quick question to chat and process it
                            quick_question = f"cho tôi thông tin bệnh {primary_disease}"
                            self.session_manager.add_message("user", quick_question)
                            
                            # Process the quick question immediately
                            with st.chat_message("user"):
                                st.markdown(quick_question)
                            
                            with st.chat_message("assistant"):
                                with st.spinner("Đang tìm thông tin..."):
                                    messages = self.session_manager.get_messages()
                                    api_messages = self.chat_service.prepare_messages_for_api(messages)
                                    response, relevant_images = self.chat_service.send_message(api_messages, user_query=quick_question)
                                    
                                    # Display relevant disease images first if available
                                    if relevant_images:
                                        st.markdown("**Hình ảnh minh họa:**")
                                        self.ui_components.render_disease_images(relevant_images)
                                    
                                    # Display text response
                                    st.markdown(response)
                                    
                                    # Add assistant response to history
                                    self.session_manager.add_message("assistant", response)
                else:
                    self.error_handler.display_error(response_message)
                    self.session_manager.add_message("assistant", response_message)
            
            # Return to chat mode
            self.session_manager.set_diagnosis_mode(False)
            st.rerun()
    
    def run(self):
        """Main application loop"""
        # Render custom CSS
        self.ui_components.render_custom_css()
        
        # Render header
        self.ui_components.render_header()
        
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