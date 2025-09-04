"""
Configuration settings for the medical chatbot application
"""
import streamlit as st

class Config:
    """Application configuration class"""
    
    # API Configuration
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
    OPENROUTER_URL = "https://openrouter.ai/api/v1"

    
    # Model Configuration
    LLM_MODEL = "openai/gpt-oss-20b:free"
    VISION_MODEL = "Jayanth2002/dinov2-base-finetuned-SkinDisease"
    
    # Chat Configuration
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7
    
    # UI Configuration
    IMAGE_WIDTH = 300
    UPLOAD_IMAGE_WIDTH = 400
    
    # File Types
    ALLOWED_IMAGE_TYPES = ['jpg', 'jpeg', 'png']
    
    # Messages
    DIAGNOSIS_USER_MESSAGE = "Tôi đã gửi ảnh da liễu để chẩn đoán"
    ERROR_MESSAGE = "Không thể phân tích ảnh này. Vui lòng thử ảnh khác."
    MODEL_LOAD_ERROR = "Model chưa được load thành công. Vui lòng kiểm tra lại."