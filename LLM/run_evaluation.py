import os
import sys
import json
import torch
from tqdm import tqdm
from RAG.document_query_embedder import DenseRetriever
from RAG.sparse_embedder import SparseRetriever
from RAG.retriever import HybridRetriever
from LLM.llm import AnswerGenerator

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    leaderboard_file = "leaderboard_queries.json"
    output_file = "system_outputs/system_output_5.json"
    andrew_id = "hanmozha"
    
    print(f"Loading queries from {leaderboard_file}...")
    with open(leaderboard_file, 'r', encoding='utf-8') as f:
        queries = json.load(f)
        
    print(f"Found {len(queries)} questions.")

    print("Initializing Dense Retriever...")
    dense = DenseRetriever()
    dense.load_index()
    
    print("Initializing Sparse Retriever...")
    sparse = SparseRetriever()
    sparse.load_index()
    
    print("Setting up Hybrid Retriever...")
    hybrid = HybridRetriever(dense, sparse)
    
    print("Loading Generator LLM...")
    generator = AnswerGenerator()
    
    results = {}
    results["andrewid"] = andrew_id
    
    print("\nStarting generation pipeline...")
    for q in tqdm(queries, desc="Evaluating Queries"):
        q_id = q["id"]
        q_text = q["question"]
        
        chunks = hybrid.search(q_text, top_k=10, method="rrf")
        
        answer = generator.generate(q_text, chunks)
        
        results[q_id] = answer

        # Clear MPS cache for Apple Silicon
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
            
        # Clear CUDA cache for NVIDIA GPUs
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"\nEvaluation complete! Results saved to {output_file}")
    print("File is ready for leaderboard submission.")

if __name__ == "__main__":
    main()
