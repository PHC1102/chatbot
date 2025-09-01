"""
Chat service for handling GPT-OSS interactions
"""
import requests
from config.settings import Config

class ChatService:
    """Service for handling chat interactions with GPT-OSS"""
    
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.api_url = Config.OPENROUTER_URL
    
    def send_message(self, messages):
        """
        Send message to GPT-OSS via OpenRouter
        
        Args:
            messages: List of message objects in OpenAI format
            
        Returns:
            String response from GPT-OSS
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": Config.LLM_MODEL,
            "messages": messages,
            "temperature": Config.TEMPERATURE,
            "max_tokens": Config.MAX_TOKENS
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            response_content = response.json()["choices"][0]["message"]["content"]

            marker = "assistantfinal"
            idx = response_content.lower().find(marker)  # tìm marker, không phân biệt hoa thường

            if idx != -1:
                # lấy text ngay sau marker
                final_text = response_content[idx + len(marker):].strip()
            else:
                # nếu không có marker thì dùng toàn bộ content
                final_text = response_content.strip()

            return final_text
        except Exception as e:
            return f"Lỗi khi gọi API: {str(e)}"
    
    def prepare_messages_for_api(self, chat_history):
        """
        Prepare chat history for API call (exclude images)
        
        Args:
            chat_history: List of chat messages
            
        Returns:
            List of messages formatted for API
        """
        return [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in chat_history 
            if "image" not in msg
        ]
    
    def create_diagnosis_prompt(self, predictions):
        """
        Create diagnosis prompt for GPT-OSS
        
        Args:
            predictions: List of prediction results from vision model
            
        Returns:
            Formatted prompt string
        """
        prompt = "Đây là ảnh da liễu.\n\n"
        prompt += "Model thị giác dự đoán:\n"
        
        for i, pred in enumerate(predictions, 1):
            disease = pred['label']
            confidence = pred['score'] * 100
            prompt += f"{i}. {disease}, độ tin cậy {confidence:.1f}%\n"
        
        prompt += "\nGiải thích thật ngắn gọn vì sao model có thể đưa ra dự đoán này dựa trên đặc điểm hình ảnh. Lưu ý: Đây chỉ là dự đoán của AI, không thay thế chẩn đoán y tế chuyên nghiệp."
        
        return prompt