import os
import json
import bm25s

class SparseRetriever:
    def __init__(self, index_dir="data/bm25_index"):
        self.index_dir = index_dir
        self.retriever = None
        self.id_to_doc = {}

    def build_index(self, knowledge_base_path="data/knowledge_base.jsonl"):
        print("Reading knowledge base for BM25...")
        texts = []
        doc_ids = []
        
        with open(knowledge_base_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                record = json.loads(line)
                texts.append(record['text'])
                doc_ids.append(record)
                self.id_to_doc[i] = record
                
        print(f"Tokenizing {len(texts)} chunks for sparse retrieval...")
        corpus_tokens = bm25s.tokenize(texts)
        
        print("Building BM25 index...")
        self.retriever = bm25s.BM25()
        self.retriever.index(corpus_tokens)
        
        self.save_index()
        print(f"BM25 Index successfully built and saved to {self.index_dir}!")

    def save_index(self):
        os.makedirs(self.index_dir, exist_ok=True)
        self.retriever.save(self.index_dir)
        
        map_path = os.path.join(self.index_dir, "mapping.json")
        with open(map_path, 'w', encoding='utf-8') as f:
            json.dump(self.id_to_doc, f, ensure_ascii=False, indent=2)

    def load_index(self):
        if os.path.exists(self.index_dir):
            try:
                self.retriever = bm25s.BM25.load(self.index_dir, load_corpus=False)
                
                map_path = os.path.join(self.index_dir, "mapping.json")
                with open(map_path, 'r', encoding='utf-8') as f:
                    raw_mapping = json.load(f)
                    self.id_to_doc = {int(k): v for k, v in raw_mapping.items()}
                return True
            except Exception as e:
                print(f"Failed to load BM25 index: {e}")
                return False
        return False

    def search(self, query: str, top_k: int = 5):
        if self.retriever is None:
            if not self.load_index():
                raise FileNotFoundError("BM25 index not found. Please run build_index() first.")
                
        query_tokens = bm25s.tokenize([query])
        
        results_obj = self.retriever.retrieve(query_tokens, k=top_k)
        
        doc_indices = results_obj.documents[0]
        doc_scores = results_obj.scores[0]
        
        results = []
        for idx, score in zip(doc_indices, doc_scores):
            idx = int(idx)
            if idx in self.id_to_doc:
                doc = self.id_to_doc[idx]
                results.append({
                    "score": float(score),
                    "chunk_id": doc.get('id'),
                    "source": doc.get('source'),
                    "text": doc.get('text')
                })
                
        return results

if __name__ == "__main__":
    sparse_retriever = SparseRetriever()
    
    if not os.path.exists(sparse_retriever.index_dir):
        sparse_retriever.build_index()
        
    print("\n--- Testing Sparse (BM25) Retrieval ---")
    question = "What was the original purpose of the Carnegie Technical Schools?"
    print(f"Query: '{question}'")
    
    results = sparse_retriever.search(question, top_k=3)
    for i, res in enumerate(results):
        print(f"\nResult {i+1} (Score: {res['score']:.4f}) [Source: {res['source']}]")
        print(f"Text: {res['text'][:150]}...")
