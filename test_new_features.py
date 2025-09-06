"""
Test script for new features:
1. Concise LLM responses
2. Quick question popup after diagnosis
"""
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(__file__))

def test_concise_rag_responses():
    """Test that RAG responses include concise instruction"""
    print("Testing concise RAG responses...")
    
    try:
        from services.rag_service import RAGService
        
        rag_service = RAGService()
        
        # Test query about a disease
        test_query = "Melanoma có nguy hiểm không?"
        base_prompt = "Bạn là chuyên gia da liễu"
        
        enhanced_prompt, images = rag_service.enhance_prompt_with_rag(test_query, base_prompt)
        
        # Check if the concise instruction is included
        if "TRẢ LỜI NGẮN GỌN, SÚC TÍCH" in enhanced_prompt:
            print("✅ Concise instruction found in enhanced prompt")
            return True
        else:
            print("❌ Concise instruction NOT found in enhanced prompt")
            print(f"Prompt preview: {enhanced_prompt[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error testing concise responses: {str(e)}")
        return False

def test_disease_extraction():
    """Test disease name extraction from diagnosis response"""
    print("Testing disease name extraction...")
    
    try:
        from services.diagnosis_service import DiagnosisService
        from models.ai_models import ModelManager
        
        model_manager = ModelManager()
        vision_model = model_manager.get_vision_model()
        diagnosis_service = DiagnosisService(vision_model)
        
        # Test response text with disease name
        test_response = "Model dự đoán đây là Melanoma với độ tin cậy 85%. Melanoma là một loại ung thư da nguy hiểm..."
        
        extracted_disease = diagnosis_service._extract_primary_disease_from_response(test_response)
        
        if extracted_disease == "Melanoma":
            print("✅ Disease name extraction working correctly")
            return True
        else:
            print(f"❌ Expected 'Melanoma', got '{extracted_disease}'")
            return False
            
    except Exception as e:
        print(f"❌ Error testing disease extraction: {str(e)}")
        return False

def test_ui_components():
    """Test UI components import"""
    print("Testing UI components...")
    
    try:
        from ui.components import UIComponents
        
        # Check if the new method exists
        if hasattr(UIComponents, 'render_quick_question_popup'):
            print("✅ Quick question popup method exists")
            return True
        else:
            print("❌ Quick question popup method NOT found")
            return False
            
    except Exception as e:
        print(f"❌ Error testing UI components: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("="*50)
    print("TESTING NEW FEATURES")
    print("="*50)
    
    results = []
    
    # Test 1: Concise RAG responses
    results.append(test_concise_rag_responses())
    print()
    
    # Test 2: Disease extraction
    results.append(test_disease_extraction())
    print()
    
    # Test 3: UI components
    results.append(test_ui_components())
    print()
    
    # Summary
    print("="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! New features are ready to use.")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
    
    print("\n🚀 To test the full functionality:")
    print("1. Run: streamlit run app.py")
    print("2. Upload an image for diagnosis")
    print("3. Check if quick question popup appears")
    print("4. Ask about a disease and check if response is concise")

if __name__ == "__main__":
    main()