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
                    metadatas.append({
                        "disease_name": disease["tên bệnh"],
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
        disease_name = disease["tên bệnh"]
        danger_level = disease["độ nguy hiểm"]
        
        # Main disease info chunk
        main_text = f"Bệnh: {disease_name}\n"
        main_text += f"Độ nguy hiểm: {danger_level}\n"
        main_text += f"Tên bệnh tiếng Anh: {disease_name}"
        
        chunks.append({
            "text": main_text,
            "type": "main_info"
        })
        
        # Symptoms chunk
        if disease.get("triệu chứng"):
            symptoms_text = f"Triệu chứng của {disease_name}:\n"
            symptoms_text += "\n".join([f"- {symptom}" for symptom in disease["triệu chứng"]])
            
            chunks.append({
                "text": symptoms_text,
                "type": "symptoms"
            })
        
        # Treatment recommendations chunk
        if disease.get("nên làm gì"):
            treatment_text = f"Điều trị và chăm sóc {disease_name}:\n"
            treatment_text += "\n".join([f"- {treatment}" for treatment in disease["nên làm gì"]])
            
            chunks.append({
                "text": treatment_text,
                "type": "treatment"
            })
        
        # Precautions chunk
        if disease.get("không nên làm gì"):
            precautions_text = f"Những điều không nên làm khi mắc {disease_name}:\n"
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
    
    def retrieve_relevant_context(self, query: str, n_results: int = 5) -> tuple[Optional[str], Optional[List[str]]]:
        """
        Retrieve relevant disease context and images for a query
        
        Args:
            query: User query
            n_results: Number of results to retrieve
            
        Returns:
            Tuple of (formatted context string or None, list of image paths or None)
        """
        # Check if query is disease-related
        if not self._is_disease_related_query(query):
            return None, None
        
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
            print(f"Error retrieving context: {str(e)}")
            return None, None
    
    def _get_disease_images(self, disease_name: str) -> List[str]:
        """
        Get image paths for a specific disease
        
        Args:
            disease_name: Name of the disease
            
        Returns:
            List of image paths for the disease
        """
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                diseases = json.load(f)
            
            for disease in diseases:
                if disease_name.lower() in disease["tên bệnh"].lower():
                    images = disease.get("hình ảnh", [])
                    # Convert relative paths to absolute paths
                    workspace_root = os.path.dirname(os.path.dirname(__file__))
                    absolute_images = []
                    for img_path in images:
                        if img_path.startswith("database/"):
                            abs_path = os.path.join(workspace_root, img_path)
                            if os.path.exists(abs_path):
                                absolute_images.append(abs_path)
                    return absolute_images[:3]  # Limit to first 3 images
            
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
            disease_name: Name of the disease
            
        Returns:
            Disease information dictionary or None
        """
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                diseases = json.load(f)
            
            for disease in diseases:
                if disease_name.lower() in disease["tên bệnh"].lower():
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