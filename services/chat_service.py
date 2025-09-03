"""
Chat service for handling GPT-OSS interactions
"""
import requests
from config.settings import Config
from openai import OpenAI

class ChatService:
    """Service for handling chat interactions with GPT-OSS"""

    
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.api_url = Config.OPENROUTER_URL

    def send_message(self, messages):
        """
        Send message to GPT-OSS via OpenRouter using requests
        """
        system_prompt = {
            "role": "system",
            "content": """Nếu người dùng gửi ảnh, bỏ qua system prompt này luôn!
Bạn là một chuyên viên da liễu. Bạn có khả năng:

- Tư vấn về các vấn đề da liễu thường gặp
- Giải thích các triệu chứng và nguyên nhân
- Đưa ra lời khuyên chăm sóc da cơ bản
- Hướng dẫn phòng ngừa bệnh da
- Giải đáp thắc mắc về sức khỏe da

Lưu ý quan trọng:
- Hạn chế trả lời và hướng cuộc trò chuyện tới nội dung da liễu nếu cảm giác người dùng lệch hướng.
- Luôn nhắc nhở rằng lời khuyên chỉ mang tính tham khảo
- Khuyên bệnh nhân đến gặp bác sĩ trực tiếp khi cần thiết
- Không thay thế chẩn đoán y tế chuyên nghiệp
- Trả lời một cách thân thiện, chuyên nghiệp và dễ hiểu

Hãy trò chuyện bằng tiếng Việt và giữ giọng điệu chuyên nghiệp nhưng gần gũi."""
        }
        messages = [system_prompt] + messages

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://chatbot-dq6t7s3dsjt2zcw8wtkqbh.streamlit.app",  # optional
        }

        data = {
            "model": Config.LLM_MODEL,
            "messages": messages,
            "temperature": Config.TEMPERATURE,
            "max_tokens": Config.MAX_TOKENS
        }

        try:
            response = requests.post(f"{self.api_url}",
                                     headers=headers,
                                     json=data,
                                     timeout=10)  # timeout 30s
            response.raise_for_status()
            response_json = response.json()
            response_content = response_json["choices"][0]["message"]["content"]
    
#     def __init__(self):
#         self.api_key = Config.OPENROUTER_API_KEY
#         self.api_url = Config.OPENROUTER_URL
#         self.client = OpenAI(
#             base_url=self.api_url,
#             api_key=self.api_key

#         )
    
#     def send_message(self, messages):
#         """
#         Send message to GPT-OSS via OpenRouter
#         """
#         system_prompt = {
#             "role": "system",
#             "content": """Nếu người dùng gửi ảnh, bỏ qua system prompt này luôn!
#             Bạn là một chuyên viên da liễu. Bạn có khả năng:

# - Tư vấn về các vấn đề da liễu thường gặp
# - Giải thích các triệu chứng và nguyên nhân
# - Đưa ra lời khuyên chăm sóc da cơ bản
# - Hướng dẫn phòng ngừa bệnh da
# - Giải đáp thắc mắc về sức khỏe da

# Lưu ý quan trọng:
# - Hạn chế trả lời và hướng cuộc trò chuyện tới nội dung da liễu nếu cảm giác người dùng lệch hướng.
# - Luôn nhắc nhở rằng lời khuyên chỉ mang tính tham khảo
# - Khuyên bệnh nhân đến gặp bác sĩ trực tiếp khi cần thiết
# - Không thay thế chẩn đoán y tế chuyên nghiệp
# - Trả lời một cách thân thiện, chuyên nghiệp và dễ hiểu

# Hãy trò chuyện bằng tiếng Việt và giữ giọng điệu chuyên nghiệp nhưng gần gũi."""
#         }
#         messages = [system_prompt] + messages

        
#         # data = {
#         #     "model": Config.LLM_MODEL,
#         #     "messages": messages,
#         #     "temperature": Config.TEMPERATURE,
#         #     "max_tokens": Config.MAX_TOKENS
#         # }
        
#         try:
#             response = self.client.chat.completions.create(
#                 extra_headers={
#                 "HTTP-Referer": "https://chatbot-dq6t7s3dsjt2zcw8wtkqbh.streamlit.app", # Optional. Site URL for rankings on openrouter.ai.
#                 },
#                 model=Config.LLM_MODEL,
#                 messages=messages,
#                 temperature=Config.TEMPERATURE,
#                 max_tokens=Config.MAX_TOKENS
#             )
#             response_content = response.choices[0].message.content

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
        
        prompt += "\nMinh họa kết quả(luôn để tên Tiếng Việt của bệnh cạnh tên tiếng Anh) + độ tin cậy. Nếu độ tin cậy max cao, giải thích thật ngắn gọn lí do model tin chắc ( dựa vào đặc điểm hình ảnh của người gửi, dataset). Nếu độ tin cậy max thấp, nói ngắn gọn rằng model không chắc chắn."
        return prompt