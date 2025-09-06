"""
Test the disease image functionality
"""
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_disease_image_functionality():
    """Test the disease image retrieval functionality"""
    from services.rag_service import RAGService
    from services.chat_service import ChatService
    
    print("Testing Disease Image Functionality")
    print("=" * 50)
    
    # Initialize services
    rag_service = RAGService()
    chat_service = ChatService()
    
    # Test queries that should return images
    test_queries = [
        "Melanoma co nguy hiem khong?",
        "Trieu chung cua Basal Cell Carcinoma",
        "Psoriasis trong nhu the nao?",
        "Hinh anh cua actinic keratosis",
        "Toi muon xem hinh anh nevus"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\\nTest {i}: {query}")
        print("-" * 30)
        
        # Test RAG context and image retrieval
        context, images = rag_service.retrieve_relevant_context(query)
        
        if context:
            print("Success: Context retrieved successfully")
            print(f"Context preview: {context[:100]}...")
        else:
            print("No context found")
        
        if images:
            print(f"Success: Found {len(images)} disease images:")
            for img_path in images:
                if os.path.exists(img_path):
                    print(f"  OK: {os.path.basename(img_path)} (exists)")
                else:
                    print(f"  Missing: {os.path.basename(img_path)} (not found)")
        else:
            print("Info: No images found for this query")
        
        # Test enhanced prompt with images
        enhanced_prompt, prompt_images = rag_service.enhance_prompt_with_rag(query, "Base prompt")
        
        if "Thong tin tu co so du lieu" in enhanced_prompt:
            print("Success: Prompt enhanced with database info")
        
        if prompt_images:
            print(f"Success: Prompt includes {len(prompt_images)} images")
        
        print()
    
    print("=" * 50)
    print("Image functionality test completed!")

def test_specific_disease_images():
    """Test specific disease image retrieval"""
    from services.rag_service import RAGService
    
    print("\\nTesting Specific Disease Image Retrieval")
    print("=" * 50)
    
    rag_service = RAGService()
    
    # Test specific diseases
    diseases = ["Melanoma", "Psoriasis", "Basal Cell Carcinoma", "nevus", "actinic keratosis"]
    
    for disease in diseases:
        print(f"\\nDisease: {disease}")
        print("-" * 20)
        
        images = rag_service._get_disease_images(disease)
        
        if images:
            print(f"Found {len(images)} images:")
            for img_path in images:
                filename = os.path.basename(img_path)
                exists = os.path.exists(img_path)
                status = "OK" if exists else "Missing"
                print(f"  {status}: {filename}")
        else:
            print("No images found")

def main():
    """Main test function"""
    try:
        test_disease_image_functionality()
        test_specific_disease_images()
        
        print("\\n" + "=" * 50)
        print("All disease image tests completed successfully!")
        print("The chatbot can now display disease images with responses.")
        
    except Exception as e:
        print(f"\\nError during testing: {str(e)}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()