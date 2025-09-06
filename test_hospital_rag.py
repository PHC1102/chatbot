"""
Test script for Hospital RAG functionality
"""
import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(__file__))

def test_hospital_rag():
    """Test hospital RAG functionality"""
    print("Testing Hospital RAG functionality...")
    print("="*50)
    
    try:
        from services.rag_service import RAGService
        
        rag_service = RAGService()
        
        # Test queries for different districts
        test_queries = [
            "Tìm cơ sở da liễu ở quận Long Biên",
            "Phòng khám da liễu tại quận Cầu Giấy",
            "Bệnh viện da liễu ở quận Đống Đa",
            "Cơ sở chữa trị da liễu tại Hoàn Kiếm",
            "Phòng khám da liễu quận Tây Hồ",
            "Da liễu ở huyện Sóc Sơn",
            "Cơ sở da liễu quận Ba Đình",
            "Bệnh viện da liễu Thanh Xuân",
            "Phòng khám quận không tồn tại",  # Test non-existent district
            "Cho tôi thông tin về melanoma",  # Disease query (should use disease RAG)
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            print("-" * 40)
            
            # Check query type detection
            is_hospital = rag_service._is_hospital_related_query(query)
            is_disease = rag_service._is_disease_related_query(query)
            
            print(f"Hospital-related: {is_hospital}")
            print(f"Disease-related: {is_disease}")
            
            # Get context
            context, images = rag_service.retrieve_relevant_context(query)
            
            if context:
                print("📋 Retrieved context:")
                # Show first 300 characters to avoid too much output
                print(context[:300] + "..." if len(context) > 300 else context)
            else:
                print("❌ No context found")
            
            if images:
                print(f"🖼️ Images found: {len(images)}")
            
            print()
    
    except Exception as e:
        print(f"❌ Error in hospital RAG test: {str(e)}")

def test_district_extraction():
    """Test district extraction functionality"""
    print("\n" + "="*50)
    print("Testing District Extraction")
    print("="*50)
    
    try:
        from services.rag_service import RAGService
        
        rag_service = RAGService()
        
        test_cases = [
            ("Tìm phòng khám da liễu ở quận Long Biên", "Long Biên"),
            ("Cơ sở da liễu tại quận Cầu Giấy", "Cầu Giấy"),
            ("Bệnh viện ở Đống Đa", "Đống Đa"),
            ("Phòng khám quận Hoàn Kiếm", "Hoàn Kiếm"),
            ("Da liễu huyện Sóc Sơn", "Sóc Sơn"),
            ("Tìm bác sĩ ở Tây Hồ", "Tây Hồ"),
            ("Phòng khám da liễu", None),  # No district mentioned
            ("Bệnh xyz ở quận không tồn tại", None),  # Non-existent district
        ]
        
        for query, expected in test_cases:
            extracted = rag_service._extract_district_from_query(query)
            status = "✅" if extracted == expected else "❌"
            print(f"{status} Query: '{query}'")
            print(f"    Expected: {expected}")
            print(f"    Got: {extracted}")
            print()
            
    except Exception as e:
        print(f"❌ Error in district extraction test: {str(e)}")

def test_hospital_database_access():
    """Test hospital database access"""
    print("\n" + "="*50)
    print("Testing Hospital Database Access")
    print("="*50)
    
    try:
        from services.rag_service import RAGService
        
        rag_service = RAGService()
        
        # Test getting hospitals by district
        test_districts = ["Long Biên", "Cầu Giấy", "Đống Đa", "NonExistent"]
        
        for district in test_districts:
            hospitals = rag_service._get_hospitals_by_district(district)
            print(f"🏥 District: {district}")
            print(f"    Found {len(hospitals)} hospitals")
            
            if hospitals:
                # Show first hospital as example
                first_hospital = hospitals[0]
                print(f"    Example: {first_hospital['name']}")
                print(f"    Address: {first_hospital['address']}")
            print()
            
    except Exception as e:
        print(f"❌ Error in hospital database test: {str(e)}")

def test_enhanced_prompt():
    """Test enhanced prompt generation"""
    print("\n" + "="*50)
    print("Testing Enhanced Prompt Generation")
    print("="*50)
    
    try:
        from services.rag_service import RAGService
        
        rag_service = RAGService()
        
        # Test hospital query
        hospital_query = "Phòng khám da liễu ở quận Long Biên"
        base_prompt = "Bạn là chuyên gia da liễu"
        
        enhanced_prompt, images = rag_service.enhance_prompt_with_rag(hospital_query, base_prompt)
        
        print("🏥 Hospital Query Enhancement:")
        print(f"Query: {hospital_query}")
        if "CHỈ DẮN ĐẶC BIỆT CHO CƠ SỞ Y TẾ" in enhanced_prompt:
            print("✅ Rule-based instruction found in prompt")
        else:
            print("❌ Rule-based instruction NOT found")
            # print(f"Debug - prompt contains: {enhanced_prompt[:500]}...")  # Comment out debug
        
        # Test disease query
        disease_query = "Triệu chứng của melanoma"
        enhanced_prompt_disease, images_disease = rag_service.enhance_prompt_with_rag(disease_query, base_prompt)
        
        print("\n🦠 Disease Query Enhancement:")
        print(f"Query: {disease_query}")
        if "TRẢ LỜI NGẮN GỌN, SÚC TÍCH" in enhanced_prompt_disease:
            print("✅ Concise instruction found in prompt")
        else:
            print("❌ Concise instruction NOT found")
            
    except Exception as e:
        print(f"❌ Error in enhanced prompt test: {str(e)}")

def main():
    """Run all tests"""
    print("🧪 HOSPITAL RAG FUNCTIONALITY TESTS")
    print("="*60)
    
    test_hospital_rag()
    test_district_extraction()
    test_hospital_database_access()
    test_enhanced_prompt()
    
    print("\n" + "="*60)
    print("🎉 All tests completed!")
    print("\n📝 To test in the app:")
    print("1. Run: streamlit run app.py")
    print("2. Ask: 'Phòng khám da liễu ở quận Long Biên'")
    print("3. Should get exact results from database only")

if __name__ == "__main__":
    main()