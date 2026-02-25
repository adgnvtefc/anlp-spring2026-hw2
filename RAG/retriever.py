import os
import json
from data_pipeline.chunker import chunk_text
from RAG.sparse_embedder import SparseRetriever
from RAG.document_query_embedder import DenseRetriever

class HybridRetriever:
    def __init__(self, dense_retriever: DenseRetriever, sparse_retriever: SparseRetriever):
        self.dense = dense_retriever
        self.sparse = sparse_retriever

    def reciprocal_rank_fusion(self, dense_results, sparse_results, k=60, top_k=5):
        """
        Combines results via Reciprocal Rank Fusion (RRF).
        RRF Score = 1 / (k + rank)
        """
        rrf_scores = {}
        
        def process_results(results_list):
            for rank, res in enumerate(results_list):
                chunk_id = res['chunk_id']
                if chunk_id not in rrf_scores:
                    rrf_scores[chunk_id] = {
                        "score": 0.0,
                        "chunk_id": chunk_id,
                        "source": res['source'],
                        "text": res['text']
                    }
                rrf_scores[chunk_id]["score"] += 1.0 / (k + rank + 1) # rank is 0-indexed
                
        process_results(dense_results)
        process_results(sparse_results)
        
        fused_results = list(rrf_scores.values())
        fused_results.sort(key=lambda x: x["score"], reverse=True)
        
        return fused_results[:top_k]

    def normalize_min_max(self, results):
        if not results:
            return results
        
        scores = [r['score'] for r in results]
        min_score = min(scores)
        max_score = max(scores)
        
        denominator = max_score - min_score if (max_score - min_score) > 0 else 1.0
        
        for r in results:
            r['normalized_score'] = (r['score'] - min_score) / denominator
            
        return results

    def weighted_average_fusion(self, dense_results, sparse_results, dense_weight=0.6, sparse_weight=0.4, top_k=5):
        dense_norm = self.normalize_min_max(dense_results)
        sparse_norm = self.normalize_min_max(sparse_results)
        
        combined_scores = {}
        
        for res in dense_norm:
            chunk_id = res['chunk_id']
            combined_scores[chunk_id] = {
                "score": res['normalized_score'] * dense_weight,
                "chunk_id": chunk_id,
                "source": res['source'],
                "text": res['text']
            }
            
        for res in sparse_norm:
            chunk_id = res['chunk_id']
            if chunk_id in combined_scores:
                combined_scores[chunk_id]["score"] += (res['normalized_score'] * sparse_weight)
            else:
                combined_scores[chunk_id] = {
                    "score": res['normalized_score'] * sparse_weight,
                    "chunk_id": chunk_id,
                    "source": res['source'],
                    "text": res['text']
                }
                
        fused_results = list(combined_scores.values())
        fused_results.sort(key=lambda x: x["score"], reverse=True)
        
        return fused_results[:top_k]

    def search(self, query: str, top_k: int = 5, method="rrf"):
        candidate_count = max(top_k * 2, 20)
        
        dense_results = self.dense.search(query, top_k=candidate_count)
        sparse_results = self.sparse.search(query, top_k=candidate_count)
        
        if method == "rrf":
            return self.reciprocal_rank_fusion(dense_results, sparse_results, top_k=top_k)
        elif method == "weighted":
            return self.weighted_average_fusion(dense_results, sparse_results, top_k=top_k)
        else:
            raise ValueError("Fusion method must be 'rrf' or 'weighted'.")

if __name__ == "__main__":
    print("Loading Dense Retriever...")
    dense = DenseRetriever()
    dense.load_index()
    
    print("Loading Sparse Retriever...")
    sparse = SparseRetriever()
    sparse.load_index()
    
    print("Initializing Hybrid Fusion Retriever...")
    hybrid = HybridRetriever(dense, sparse)
    
    question = "What was the original purpose of the Carnegie Technical Schools?"
    print(f"\n--- Testing Hybrid Retrieval (Query: '{question}') ---\n")
    
    print("1. Testing Reciprocal Rank Fusion (RRF):")
    rrf_results = hybrid.search(question, top_k=3, method="rrf")
    for i, res in enumerate(rrf_results):
        print(f"Result {i+1} (RRF Score: {res['score']:.4f}) [Source: {res['source']}]")
        print(f"Text: {res['text'][:100]}...\n")
        
    print("2. Testing Weighted Average Fusion (60% Dense / 40% Sparse):")
    weighted_results = hybrid.search(question, top_k=3, method="weighted")
    for i, res in enumerate(weighted_results):
        print(f"Result {i+1} (Weight Score: {res['score']:.4f}) [Source: {res['source']}]")
        print(f"Text: {res['text'][:100]}...\n")
