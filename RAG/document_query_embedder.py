import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import json
import numpy as np
import torch
import faiss
from transformers import AutoTokenizer, AutoModel

class DenseRetriever:
    def __init__(self, model_name="BAAI/bge-small-en-v1.5", index_path="data/faiss_index.bin", map_path="data/faiss_mapping.json"):
        print(f"Loading HuggingFace model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")
        
        self.model.to(self.device)
        print(f"Model loaded to {self.device}")
        
        self.index_path = index_path
        self.map_path = map_path
        
        self.index = None
        self.id_to_doc = {} 

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0] 
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def encode(self, texts, batch_size=32):
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            encoded_input = self.tokenizer(batch_texts, padding=True, truncation=True, return_tensors='pt', max_length=512)
            encoded_input = {k: v.to(self.device) for k, v in encoded_input.items()}
            
            with torch.no_grad():
                model_output = self.model(**encoded_input)
                
            sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
            
            sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
            
            all_embeddings.extend(sentence_embeddings.cpu().numpy())
            
        return np.array(all_embeddings).astype('float32')

    def build_index(self, knowledge_base_path="data/knowledge_base.jsonl"):
        print("Reading knowledge base...")
        texts = []
        doc_ids = []
        
        with open(knowledge_base_path, 'r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line)
                texts.append(record['text'])
                doc_ids.append(record)
                
        print(f"Generating embeddings for {len(texts)} chunks (this might take a few minutes)...")
        embeddings = self.encode(texts)
        
        dimension = embeddings.shape[1]
        print(f"Building FAISS index (Dimension: {dimension})...")
        
        self.index = faiss.IndexFlatIP(dimension) 
        self.index.add(embeddings)
        
        for i, record in enumerate(doc_ids):
            self.id_to_doc[i] = record
            
        self.save_index()
        print("FAISS Index successfully built and saved!")

    def save_index(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.map_path, 'w', encoding='utf-8') as f:
            json.dump(self.id_to_doc, f, ensure_ascii=False, indent=2)

    def load_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.map_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.map_path, 'r', encoding='utf-8') as f:
                raw_mapping = json.load(f)
                self.id_to_doc = {int(k): v for k, v in raw_mapping.items()}
            return True
        return False

    def search(self, query: str, top_k: int = 5):
        # BGE models require an explicit instruction prefix for query embeddings
        instruction = "Represent this sentence for searching relevant passages: "
        query_embedding = self.encode([instruction + query])
        
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1:
                doc = self.id_to_doc.get(idx, {})
                results.append({
                    "score": float(dist),
                    "chunk_id": doc.get('id'),
                    "source": doc.get('source'),
                    "text": doc.get('text')
                })
                
        return results

if __name__ == "__main__":
    embedder = DenseRetriever()
    
    if not os.path.exists(embedder.index_path):
        embedder.build_index()
        
    print("\n--- Testing Dense Retrieval ---")
    question = "What was the original purpose of the Carnegie Technical Schools?"
    print(f"Query: '{question}'")
    
    results = embedder.search(question, top_k=3)
    for i, res in enumerate(results):
        print(f"\nResult {i+1} (Score: {res['score']:.4f}) [Source: {res['source']}]")
        print(f"Text: {res['text'][:150]}...")
