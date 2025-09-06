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
            Tuple of (success: bool, response_message: str, diagnosis_images: list or None)
        """
        # Step 1: Analyze image with vision model
        predictions = self.vision_model.predict(image)
        
        if not predictions:
            return False, Config.ERROR_MESSAGE
        
        # Step 2: Create diagnosis prompt
        diagnosis_prompt = self.chat_service.create_diagnosis_prompt(predictions)
        
        # Step 3: Get explanation from GPT-OSS with RAG enhancement
        try:
            messages_for_api = [{"role": "user", "content": diagnosis_prompt}]
            # Use RAG for diagnosis context by passing the disease names from predictions
            disease_query = " ".join([pred['label'] for pred in predictions])
            response, diagnosis_images = self.chat_service.send_message(messages_for_api, user_query=disease_query)
            return True, response, diagnosis_images
        except Exception as e:
            return False, f"Lỗi khi tạo báo cáo: {str(e)}", None
    
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
    
    def display_diagnosis_in_chat(self, image, response_message, chat_history, diagnosis_images=None):
        """
        Display diagnosis results in chat interface
        
        Args:
            image: PIL Image object
            response_message: Response from diagnosis
            chat_history: Current chat history list
            diagnosis_images: List of relevant disease images
            
        Returns:
            str: Disease name for quick question if found, None otherwise
        """
        # Import here to avoid circular import
        from ui.components import UIComponents
        
        # Display user message with image
        with st.chat_message("user"):
            st.image(image, width=Config.IMAGE_WIDTH)
            st.markdown(Config.DIAGNOSIS_USER_MESSAGE)
        
        # Display assistant response
        with st.chat_message("assistant"):
            # Show relevant disease images first if available
            if diagnosis_images:
                st.markdown("**Hình ảnh minh họa bệnh tương tự:**")
                UIComponents.render_disease_images(diagnosis_images)
            
            # Show diagnosis text
            st.markdown(response_message)
            
        # Add to chat history
        chat_history.append({"role": "assistant", "content": response_message})
        
        # Extract disease name from response for quick question
        return self._extract_primary_disease_from_response(response_message)
    
    def _extract_primary_disease_from_response(self, response_message: str) -> str:
        """
        Extract the primary disease name from diagnosis response
        
        Args:
            response_message: Diagnosis response text
            
        Returns:
            Primary disease name or None
        """
        # List of common disease names to look for
        disease_names = [
            "Melanoma", "Basal Cell Carcinoma", "Squamous Cell Carcinoma", 
            "Actinic Keratosis", "Dermatofibroma", "Nevus", "Seborrheic Keratosis",
            "Psoriasis", "Tinea Corporis", "Eczema", "Atopic Dermatitis",
            "Contact Dermatitis", "Seborrheic Dermatitis", "Lupus", "Rosacea"
        ]
        
        # Check which disease names appear in the response
        for disease in disease_names:
            if disease.lower() in response_message.lower():
                return disease
        
        return None