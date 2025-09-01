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
        self.system_prompt = (
            "Bạn là một chatbot hỗ trợ da liễu chuyên nghiệp. "
            "Luôn chào hỏi người dùng một cách lịch sự khi họ bắt đầu hội thoại, "
            "nhưng sau đó chỉ tập trung vào các vấn đề về da liễu. "
            "Trả lời ngắn gọn, dễ hiểu, chỉ cung cấp thông tin tham khảo, "
            "không đưa ra chẩn đoán y tế thay thế bác sĩ."
        )
    
    def send_message(self, user_message):
        """
        Send message to GPT-OSS via OpenRouter
        
        Args:
            user_message: String, nội dung người dùng
            
        Returns:
            String response từ GPT-OSS
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Messages: luôn có system prompt đầu tiên, rồi user message
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        data = {
            "model": Config.LLM_MODEL,
            "messages": messages,           # messages bao gồm system + user
            "temperature": Config.TEMPERATURE,
            "max_tokens": Config.MAX_TOKENS,
            
           
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
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
