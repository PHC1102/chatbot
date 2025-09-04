"""
AI Models management for medical chatbot
"""
import streamlit as st
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from config.settings import Config
import json
import os
class VisionModel:
    """Handles skin disease classification model"""
    
    def __init__(self):
        self.processor = None
        self.model = None
        self._load_model()
        json_path = os.path.join(os.path.dirname(__file__), 'disease_mapping.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            self.name_mapping = json.load(f)
    
    @st.cache_resource
    def _load_model(_self):
        """Load dinov2-skindisease-finetuned model locally"""
        try:
            processor = AutoImageProcessor.from_pretrained(Config.VISION_MODEL)
            model = AutoModelForImageClassification.from_pretrained(Config.VISION_MODEL)
            return processor, model
        except Exception as e:
            st.error(f"Không thể load model: {str(e)}")
            return None, None
    
    def load_model(self):
        """Initialize the model"""
        self.processor, self.model = self._load_model()
    
    def is_loaded(self):
        """Check if model is loaded successfully"""
        return self.processor is not None and self.model is not None
    
    def predict(self, image):
        """
        Analyze skin disease from image
        
        Args:
            image: PIL Image object
            
        Returns:
            List of predictions with labels and scores
        """
        if not self.is_loaded():
            return None
            
        try:
            # Preprocess image
            inputs = self.processor(images=image, return_tensors="pt")
            
            # Inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Get top 3 predictions
            top3_indices = torch.topk(predictions, 3).indices[0]
            top3_scores = torch.topk(predictions, 3).values[0]
            
            # Format results
            results = []
            for idx, score in zip(top3_indices, top3_scores):
                label = self.model.config.id2label[idx.item()]
                results.append({
                    'label': label + self.name_mapping.get(label, label),
                    'score': score.item()
                })
            
            return results
        except Exception as e:
            st.error(f"Lỗi khi phân tích ảnh: {str(e)}")
            return None

class ModelManager:
    """Central model management class"""
    
    def __init__(self):
        self.vision_model = VisionModel()
    
    def initialize_models(self):
        """Initialize all models"""
        self.vision_model.load_model()
    
    def get_vision_model(self):
        """Get vision model instance"""
        return self.vision_model