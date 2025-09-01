"""
Diagnosis service for handling medical image analysis
"""
import streamlit as st
from PIL import Image
from services.chat_service import ChatService
from config.settings import Config

class DiagnosisService:
    """Service for handling medical diagnosis workflow"""
    
    def __init__(self, vision_model):
        self.vision_model = vision_model
        self.chat_service = ChatService()
    
    def process_image_diagnosis(self, image, chat_history):
        """
        Complete workflow for image diagnosis
        
        Args:
            image: PIL Image object
            chat_history: Current chat history
            
        Returns:
            Tuple of (success: bool, response_message: str)
        """
        # Step 1: Analyze image with vision model
        predictions = self.vision_model.predict(image)
        
        if not predictions:
            return False, Config.ERROR_MESSAGE
        
        # Step 2: Create diagnosis prompt
        diagnosis_prompt = self.chat_service.create_diagnosis_prompt(predictions)
        
        # Step 3: Get explanation from GPT-OSS
        try:
            messages_for_api = [{"role": "user", "content": diagnosis_prompt}]
            response = self.chat_service.send_message(messages_for_api)
            return True, response
        except Exception as e:
            return False, f"Lỗi khi tạo báo cáo: {str(e)}"
    
    def add_diagnosis_to_chat(self, image, chat_history):
        """
        Add diagnosis request to chat history
        
        Args:
            image: PIL Image object
            chat_history: Current chat history list
        """
        chat_history.append({
            "role": "user", 
            "content": Config.DIAGNOSIS_USER_MESSAGE,
            "image": image
        })
    
    def display_diagnosis_in_chat(self, image, response_message, chat_history):
        """
        Display diagnosis results in chat interface
        
        Args:
            image: PIL Image object
            response_message: Response from diagnosis
            chat_history: Current chat history list
        """
        # Display user message with image
        with st.chat_message("user"):
            st.image(image, width=Config.IMAGE_WIDTH)
            st.markdown(Config.DIAGNOSIS_USER_MESSAGE)
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response_message)
            
        # Add to chat history
        chat_history.append({"role": "assistant", "content": response_message})