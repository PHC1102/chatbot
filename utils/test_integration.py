"""
Simple test to verify the chatbot integration with RAG
"""
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_chat_service_with_rag():
    """Test the ChatService with RAG functionality"""
    from services.chat_service import ChatService
    
    print("Testing ChatService with RAG integration...")
    print("=" * 50)
    
    chat_service = ChatService()
    
    # Test messages and queries
    test_cases = [
        {
            "query": "Melanoma có nguy hiểm không?",
            "messages": [{"role": "user", "content": "Melanoma có nguy hiểm không?"}]
        },
        {
            "query": "Triệu chứng của psoriasis là gì?",
            "messages": [{"role": "user", "content": "Triệu chứng của psoriasis là gì?"}]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['query']}")
        print("-" * 30)
        
        # Test RAG context retrieval
        context = chat_service.rag_service.retrieve_relevant_context(test_case['query'])
        if context:
            print("✓ RAG context retrieved successfully")
            print(f"Context preview: {context[:150]}...")
        else:
            print("✗ No RAG context found")
        
        # Test enhanced prompt
        base_prompt = "You are a medical expert."
        enhanced_prompt = chat_service.rag_service.enhance_prompt_with_rag(test_case['query'], base_prompt)
        
        if "Thông tin từ cơ sở dữ liệu" in enhanced_prompt:
            print("✓ Prompt enhanced with RAG context")
        else:
            print("ℹ Prompt not enhanced (no relevant context)")
    
    print("\n" + "=" * 50)
    print("RAG integration test completed!")

if __name__ == "__main__":
    test_chat_service_with_rag()