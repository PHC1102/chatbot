"""
RAG Management Utility - Test and manage RAG functionality
"""
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rag_service import RAGService

def test_rag_functionality():
    """Test the RAG service functionality"""
    print("Initializing RAG Service...")
    rag_service = RAGService()
    
    # Test queries
    test_queries = [
        "Basal Cell Carcinoma là gì?",
        "Triệu chứng của melanoma",
        "Cách điều trị psoriasis",
        "Làm thế nào để chăm sóc da bị tinea corporis?",
        "Tôi có nốt ruồi đen trên da",
        "Da tôi bị ngứa và đỏ",
        "Hello, how are you today?",  # Non-disease query
    ]
    
    print("\n" + "="*50)
    print("TESTING RAG RETRIEVAL")
    print("="*50)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 30)
        
        # Check if disease-related
        is_disease_related = rag_service._is_disease_related_query(query)
        print(f"Disease-related: {is_disease_related}")
        
        # Get context
        context = rag_service.retrieve_relevant_context(query)
        if context:
            print(f"Retrieved context (first 200 chars):\n{context[:200]}...")
        else:
            print("No relevant context found")
        
        print("\n" + "-"*50)

def test_disease_info():
    """Test specific disease information retrieval"""
    print("\n" + "="*50)
    print("TESTING DISEASE INFO RETRIEVAL")
    print("="*50)
    
    rag_service = RAGService()
    
    # Test specific diseases
    diseases = ["Melanoma", "Psoriasis", "Basal Cell Carcinoma", "NonExistentDisease"]
    
    for disease in diseases:
        print(f"\nDisease: {disease}")
        print("-" * 30)
        
        disease_info = rag_service.get_disease_info(disease)
        if disease_info:
            print(f"Found: {disease_info['tên bệnh']}")
            print(f"Danger level: {disease_info['độ nguy hiểm']}")
            print(f"Symptoms count: {len(disease_info.get('triệu chứng', []))}")
        else:
            print("Disease not found")

def show_collection_stats():
    """Show ChromaDB collection statistics"""
    print("\n" + "="*50)
    print("COLLECTION STATISTICS")
    print("="*50)
    
    rag_service = RAGService()
    
    try:
        count = rag_service.collection.count()
        print(f"Total documents in collection: {count}")
        
        # Get a sample of documents
        sample = rag_service.collection.peek(limit=5)
        print(f"\nSample documents:")
        for i, (doc, meta) in enumerate(zip(sample['documents'], sample['metadatas'])):
            print(f"{i+1}. {meta['disease_name']} ({meta['chunk_type']})")
            print(f"   Text preview: {doc[:100]}...")
            
    except Exception as e:
        print(f"Error getting collection stats: {str(e)}")

def main():
    """Main function to run all tests"""
    print("RAG Service Testing Utility")
    print("=" * 50)
    
    try:
        test_rag_functionality()
        test_disease_info()
        show_collection_stats()
        
        print("\n" + "="*50)
        print("All tests completed successfully!")
        print("RAG service is ready for use.")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()