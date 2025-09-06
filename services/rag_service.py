"""
RAG (Retrieval-Augmented Generation) service for disease knowledge retrieval
"""
import json
import os
import chromadb
from chromadb.config import Settings
import tiktoken
from typing import List, Dict, Any, Optional, Tuple
from config.settings import Config

class RAGService:
    """Service for handling RAG operations with disease database"""
    
    def __init__(self, collection_name: str = "disease_knowledge"):
        """
        Initialize RAG service with ChromaDB
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.max_chunk_size = 500  # Maximum tokens per chunk
        self.database_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "diseases.json")
        self.hospital_database_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "hospital_rag.json")
        
        # Initialize ChromaDB
        self._initialize_chromadb()
        
        # Load and index disease data if collection is empty
        if self._is_collection_empty():
            self._load_and_index_diseases()
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create client with persistent storage
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chromadb")
            os.makedirs(db_path, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
        except Exception as e:
            print(f"Error initializing ChromaDB: {str(e)}")
            # Fallback to in-memory client
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def _is_collection_empty(self) -> bool:
        """Check if the collection is empty"""
        try:
            return self.collection.count() == 0
        except:
            return True
    
    def _load_and_index_diseases(self):
        """Load disease data from JSON and index it in ChromaDB"""
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                diseases = json.load(f)
            
            documents = []
            metadatas = []
            ids = []
            
            for i, disease in enumerate(diseases):
                # Create comprehensive text chunks for each disease
                chunks = self._create_disease_chunks(disease)
                
                for j, chunk in enumerate(chunks):
                    chunk_id = f"disease_{i}_chunk_{j}"
                    documents.append(chunk["text"])
                    
                    # Handle both list and string formats for disease names
                    disease_names = disease["tên bệnh"]
                    if isinstance(disease_names, list):
                        primary_name = disease_names[0]
                    else:
                        primary_name = disease_names
                    
                    metadatas.append({
                        "disease_name": primary_name,
                        "danger_level": disease["độ nguy hiểm"],
                        "chunk_type": chunk["type"],
                        "disease_index": i
                    })
                    ids.append(chunk_id)
            
            # Add documents to collection in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_metas = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids
                )
            
            print(f"Successfully indexed {len(documents)} disease knowledge chunks")
            
        except Exception as e:
            print(f"Error loading and indexing diseases: {str(e)}")
    
    def _create_disease_chunks(self, disease: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Create text chunks from disease data
        
        Args:
            disease: Disease data dictionary
            
        Returns:
            List of text chunks with metadata
        """
        chunks = []
        disease_names = disease["tên bệnh"]
        danger_level = disease["độ nguy hiểm"]
        
        # Handle both list and string formats (for backward compatibility)
        if isinstance(disease_names, list):
            primary_name = disease_names[0]  # Use first name as primary
            all_names = ", ".join(disease_names)
        else:
            primary_name = disease_names
            all_names = disease_names
        
        # Main disease info chunk
        main_text = f"Bệnh: {primary_name}\n"
        main_text += f"Tên khác: {all_names}\n"
        main_text += f"Độ nguy hiểm: {danger_level}\n"
        
        chunks.append({
            "text": main_text,
            "type": "main_info"
        })
        
        # Symptoms chunk
        if disease.get("triệu chứng"):
            symptoms_text = f"Triệu chứng của {primary_name}:\n"
            symptoms_text += "\n".join([f"- {symptom}" for symptom in disease["triệu chứng"]])
            
            chunks.append({
                "text": symptoms_text,
                "type": "symptoms"
            })
        
        # Treatment recommendations chunk
        if disease.get("nên làm gì"):
            treatment_text = f"Điều trị và chăm sóc {primary_name}:\n"
            treatment_text += "\n".join([f"- {treatment}" for treatment in disease["nên làm gì"]])
            
            chunks.append({
                "text": treatment_text,
                "type": "treatment"
            })
        
        # Precautions chunk
        if disease.get("không nên làm gì"):
            precautions_text = f"Những điều không nên làm khi mắc {primary_name}:\n"
            precautions_text += "\n".join([f"- {precaution}" for precaution in disease["không nên làm gì"]])
            
            chunks.append({
                "text": precautions_text,
                "type": "precautions"
            })
        
        return chunks
    
    def _is_disease_related_query(self, query: str) -> bool:
        """
        Check if a query is related to diseases or medical conditions
        
        Args:
            query: User query text
            
        Returns:
            Boolean indicating if query is disease-related
        """
        disease_keywords = [
            "bệnh", "triệu chứng", "điều trị", "chữa", "thuốc", "khám", "bác sĩ",
            "đau", "ngứa", "viêm", "nhiễm", "da", "liễu", "tổn thương", "loét",
            "mụn", "ban", "đỏ", "sưng", "vảy", "chẩn đoán", "phòng ngừa",
            "disease", "symptom", "treatment", "doctor", "medicine", "skin",
            "carcinoma", "keratosis", "melanoma", "psoriasis", "dermatitis",
            "lesion", "infection", "inflammation"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in disease_keywords)
    
    def _is_hospital_related_query(self, query: str) -> bool:
        """
        Check if a query is related to hospital/clinic information
        
        Args:
            query: User query text
            
        Returns:
            Boolean indicating if query is hospital-related
        """
        hospital_keywords = [
            "bệnh viện", "phòng khám", "cơ sở", "địa chỉ", "website", "liên hệ",
            "quận", "huyện", "phường", "xã", "đường", "phố", "ngõ", "số",
            "hospital", "clinic", "address", "location", "contact", "phone",
            "ở", "tại", "gần", "khu vực", "vùng", "khám bệnh", "chữa trị",
            "da liễu", "thẩm mỹ", "chuyên khoa", "đa khoa"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in hospital_keywords)
    
    def _extract_district_from_query(self, query: str) -> Optional[str]:
        """
        Extract district name from user query using rule-based matching
        
        Args:
            query: User query text
            
        Returns:
            District name if found, None otherwise
        """
        # List of districts in Hanoi from the hospital database
        districts = [
            "Cầu Giấy", "Thanh Xuân", "Hoàng Mai", "Đống Đa", "Hà Đông",
            "Hai Bà Trưng", "Hoàn Kiếm", "Long Biên", "Tây Hồ", "Bắc Từ Liêm",
            "Sóc Sơn", "Thạch Thất", "Thường Tín", "Ba Đình", "Thanh Trì",
            "Ba Vì", "Đan Phượng", "Gia Lâm", "Đông Anh", "Phúc Thọ",
            "Phú Xuyên", "Quốc Oai", "Ứng Hòa", "Sơn Tây", "Chương Mỹ",
            "Hoài Đức", "Mỹ Đức", "Thanh Oai", "Nam Từ Liêm"
        ]
        
        query_lower = query.lower()
        
        # Try to find district name in query
        for district in districts:
            district_lower = district.lower()
            # Check for exact match or with "quận" prefix
            if (district_lower in query_lower or 
                f"quận {district_lower}" in query_lower or
                f"huyện {district_lower}" in query_lower or
                f"thị xã {district_lower}" in query_lower):
                return district
        
        return None
    
    def _get_hospitals_by_district(self, district: str) -> List[Dict[str, Any]]:
        """
        Get hospitals in a specific district from hospital database
        
        Args:
            district: District name
            
        Returns:
            List of hospitals in the district
        """
        try:
            with open(self.hospital_database_path, 'r', encoding='utf-8') as f:
                hospitals = json.load(f)
            
            # Filter hospitals by district (case-insensitive)
            matching_hospitals = []
            district_lower = district.lower()
            
            for hospital in hospitals:
                hospital_district = hospital.get("district", "").lower()
                # Exact match or partial match (for cases like "Ba Đình (Lân cận...)")
                if district_lower in hospital_district or hospital_district in district_lower:
                    matching_hospitals.append(hospital)
            
            return matching_hospitals
            
        except Exception as e:
            print(f"Error getting hospitals by district: {str(e)}")
            return []
    
    def _format_hospital_context(self, hospitals: List[Dict[str, Any]], district: str) -> str:
        """
        Format hospital information into a context string
        
        Args:
            hospitals: List of hospital dictionaries
            district: District name
            
        Returns:
            Formatted context string
        """
        if not hospitals:
            return f"Không tìm thấy cơ sở da liễu nào tại quận/huyện {district}."
        
        context = f"Các cơ sở da liễu tại quận/huyện {district}:\n\n"
        
        for i, hospital in enumerate(hospitals, 1):
            context += f"{i}. **{hospital['name']}**\n"
            context += f"   - Địa chỉ: {hospital['address']}\n"
            
            if hospital.get('phone'):
                context += f"   - SĐT: {hospital['phone']}\n"
            
            if hospital.get('website') and hospital['website'] != 'N/A' and hospital['website']:
                context += f"   - Website: {hospital['website']}\n"
            
            # IMPORTANT: Always include location (Google Maps link)
            if hospital.get('location'):
                context += f"   - Vị trí trên bản đồ: {hospital['location']}\n"
            
            # Add nearby areas if available
            if hospital.get('nearby') and hospital['nearby']:
                nearby_str = ", ".join(hospital['nearby'][:3])  # Limit to first 3 nearby areas
                context += f"   - Khu vực lân cận: {nearby_str}\n"
            
            context += "\n"
        
        return context
    
    def retrieve_relevant_context(self, query: str, n_results: int = 5) -> tuple[Optional[str], Optional[List[str]]]:
        """
        Retrieve relevant context and images for a query (diseases or hospitals)
        
        Args:
            query: User query
            n_results: Number of results to retrieve
            
        Returns:
            Tuple of (formatted context string or None, list of image paths or None)
        """
        # Check if query is hospital-related first (more specific)
        if self._is_hospital_related_query(query):
            return self._retrieve_hospital_context(query)
        
        # Check if query is disease-related
        elif self._is_disease_related_query(query):
            return self._retrieve_disease_context(query, n_results)
        
        # Neither disease nor hospital related
        return None, None
    
    def _retrieve_hospital_context(self, query: str) -> tuple[Optional[str], Optional[List[str]]]:
        """
        Retrieve hospital context using rule-based district matching
        
        Args:
            query: User query
            
        Returns:
            Tuple of (formatted context string or None, None for images)
        """
        # Extract district from query
        district = self._extract_district_from_query(query)
        
        if not district:
            return None, None
        
        # Get hospitals in the district
        hospitals = self._get_hospitals_by_district(district)
        
        if not hospitals:
            return f"Không tìm thấy cơ sở da liễu nào tại quận/huyện {district}.", None
        
        # Format hospital information
        context = self._format_hospital_context(hospitals, district)
        
        return context, None  # No images for hospital queries
    
    def _retrieve_disease_context(self, query: str, n_results: int = 5) -> tuple[Optional[str], Optional[List[str]]]:
        """
        Retrieve disease context using ChromaDB vector search
        
        Args:
            query: User query
            n_results: Number of results to retrieve
            
        Returns:
            Tuple of (formatted context string or None, list of image paths or None)
        """
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results["documents"] or not results["documents"][0]:
                return None, None
            
            # Format the retrieved context
            context = "Thông tin từ cơ sở dữ liệu bệnh:\n\n"
            
            unique_diseases = set()
            relevant_images = []
            
            for i, (doc, metadata, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                # Only include relevant results (distance threshold)
                if distance < 0.7:  # Adjust threshold as needed
                    disease_name = metadata["disease_name"]
                    chunk_type = metadata["chunk_type"]
                    
                    # Avoid duplicate disease information
                    if disease_name not in unique_diseases or chunk_type == "main_info":
                        context += f"{doc}\n\n"
                        unique_diseases.add(disease_name)
                        
                        # Get images for this disease (only once per disease)
                        if disease_name not in [img_disease for img_disease, _ in relevant_images]:
                            disease_images = self._get_disease_images(disease_name)
                            if disease_images:
                                relevant_images.extend([(disease_name, img) for img in disease_images])
            
            context_result = context if len(unique_diseases) > 0 else None
            images_result = [img_path for _, img_path in relevant_images] if relevant_images else None
            
            return context_result, images_result
            
        except Exception as e:
            print(f"Error retrieving disease context: {str(e)}")
            return None, None
    
    def _get_disease_images(self, disease_name: str) -> List[str]:
        """
        Get image paths for a specific disease
        
        Args:
            disease_name: Name of the disease (English or Vietnamese)
            
        Returns:
            List of image paths for the disease
        """
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                diseases = json.load(f)
            
            # Normalize the search term
            disease_name_lower = disease_name.lower().strip()
            
            # Search in database with exact and partial matching
            for disease in diseases:
                disease_names = disease["tên bệnh"]
                
                # Handle both list and string formats (for backward compatibility)
                if isinstance(disease_names, list):
                    name_list = [name.lower() for name in disease_names]
                else:
                    name_list = [disease_names.lower()]
                
                # Try exact match first (highest priority)
                if disease_name_lower in name_list:
                    images = disease.get("hình ảnh", [])
                    workspace_root = os.path.dirname(os.path.dirname(__file__))
                    absolute_images = []
                    for img_path in images:
                        if img_path.startswith("database/"):
                            abs_path = os.path.join(workspace_root, img_path)
                            if os.path.exists(abs_path):
                                absolute_images.append(abs_path)
                    if absolute_images:
                        return absolute_images[:3]
                
                # Try partial match (lower priority) - only if no exact match found
                for name in name_list:
                    if (len(disease_name_lower) > 3 and disease_name_lower in name) or \
                       (len(name) > 3 and name in disease_name_lower):
                        images = disease.get("hình ảnh", [])
                        workspace_root = os.path.dirname(os.path.dirname(__file__))
                        absolute_images = []
                        for img_path in images:
                            if img_path.startswith("database/"):
                                abs_path = os.path.join(workspace_root, img_path)
                                if os.path.exists(abs_path):
                                    absolute_images.append(abs_path)
                        if absolute_images:
                            return absolute_images[:3]
            
            return []
            
        except Exception as e:
            print(f"Error getting disease images: {str(e)}")
            return []
    
    def enhance_prompt_with_rag(self, query: str, original_prompt: str) -> tuple[str, Optional[List[str]]]:
        """
        Enhance the original prompt with RAG context and return relevant images
        
        Args:
            query: User query
            original_prompt: Original system prompt
            
        Returns:
            Tuple of (enhanced prompt with retrieved context, list of image paths or None)
        """
        context, images = self.retrieve_relevant_context(query)
        
        if context:
            # Check if it's a hospital query for specific instructions
            if self._is_hospital_related_query(query):
                enhanced_prompt = f"""{original_prompt}

QUAN TRỌNG: Sử dụng thông tin sau từ cơ sở dữ liệu bệnh viện/phòng khám:

{context}

**CHỈ Dẫn ĐẶC BIỆT CHO CƠ SỞ Y TẾ:**
- CHỈ ĐƯƠ RA THÔNG TIN CÓ TRONG Tài LIỆU, KHÔNG BỊa THÊM
- TRẢ LỜI ĐÚNg, CHÍNH XÁC theo đúng dữ liệu JSON
- Hiển thị đầy đủ: tên, địa chỉ, sđt, website (nếu có)
- Sắp xếp theo thứ tự ưu tiên: cơ sở chuyên khoa da liễu trước
- KHÔNG bịa thêm thông tin nào khác ngoài JSON"""
            else:
                # Disease query - use existing format with concise instruction
                enhanced_prompt = f"""{original_prompt}

QUAN TRỌNG: Sử dụng thông tin sau từ cơ sở dữ liệu để trả lời chính xác hơn:

{context}

Hãy ưu tiên thông tin từ cơ sở dữ liệu trên khi trả lời về các bệnh da liễu. **TRẢ LỜI NGẮN GỌN, SÚC TÍCH - chỉ đưa ra thông tin cần thiết, tránh dài dòng.** Nếu thông tin trong cơ sở dữ liệu không liên quan đến câu hỏi, hãy trả lời dựa trên kiến thức chung của bạn."""
            
            return enhanced_prompt, images
        
        return original_prompt, None
    
    def get_disease_info(self, disease_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete information about a specific disease
        
        Args:
            disease_name: Name of the disease (English or Vietnamese)
            
        Returns:
            Disease information dictionary or None
        """
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                diseases = json.load(f)
            
            # Normalize the search term
            disease_name_lower = disease_name.lower().strip()
            
            # Search in database with exact and partial matching
            for disease in diseases:
                disease_names = disease["tên bệnh"]
                
                # Handle both list and string formats (for backward compatibility)
                if isinstance(disease_names, list):
                    name_list = [name.lower() for name in disease_names]
                else:
                    name_list = [disease_names.lower()]
                
                # Try exact match first (highest priority)
                if disease_name_lower in name_list:
                    return disease
                
                # Try partial match (lower priority) - only if no exact match found
                for name in name_list:
                    if (len(disease_name_lower) > 3 and disease_name_lower in name) or \
                       (len(name) > 3 and name in disease_name_lower):
                        return disease
            
            return None
            
        except Exception as e:
            print(f"Error getting disease info: {str(e)}")
            return None
    
    def update_disease_database(self, new_disease: Dict[str, Any]):
        """
        Add a new disease to the database and reindex
        
        Args:
            new_disease: New disease data dictionary
        """
        try:
            # Load existing diseases
            with open(self.database_path, 'r', encoding='utf-8') as f:
                diseases = json.load(f)
            
            # Add new disease
            diseases.append(new_disease)
            
            # Save updated database
            with open(self.database_path, 'w', encoding='utf-8') as f:
                json.dump(diseases, f, ensure_ascii=False, indent=2)
            
            # Reindex the collection
            self.collection.delete()
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self._load_and_index_diseases()
            
        except Exception as e:
            print(f"Error updating disease database: {str(e)}")