import os
import torch
from transformers import pipeline
from RAG.document_query_embedder import DenseRetriever
from RAG.sparse_embedder import SparseRetriever
from RAG.retriever import HybridRetriever

class AnswerGenerator:
    def __init__(self, model_name="Qwen/Qwen2.5-0.5B-Instruct"):
        print(f"Loading Generation Model: {model_name}...")
        
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {device}")
        
       self.generator = pipeline(
            "text-generation",
            model=model_name,
            device=device,
            torch_dtype=torch.float32
        )

    def build_prompt(self, question: str, retrieved_chunks: list[dict]) -> str:
        context_str = "\n---\n".join([f"Source: {c['source']}\nText: {c['text']}" for c in retrieved_chunks])
        
        prompt = f"""You are a helpful and precise assistant. Answer the user's question using ONLY the provided context. If the context does not contain the answer, say "I don't know based on the provided context." Be strictly factual and concise.

                    Context:
                    {context_str}

                    Question: {question}

                    Answer:
                """
        return prompt

    def generate(self, question: str, retrieved_chunks: list[dict], max_new_tokens=50, temperature=0.1) -> str:
        prompt = self.build_prompt(question, retrieved_chunks)
        
        outputs = self.generator(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True,
            return_full_text=False
        )
        
        generated_text = outputs[0]["generated_text"].strip()
        return generated_text

if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    print("Loading Retrievers...")
    dense = DenseRetriever()
    dense.load_index()
    
    sparse = SparseRetriever()
    sparse.load_index()
    
    hybrid = HybridRetriever(dense, sparse)
    
    generator = AnswerGenerator()
    
    test_question = "What was the original purpose of the Carnegie Technical Schools?"
    print(f"\nQuestion: {test_question}")
    
    print("Retrieving context chunks using Hybrid (RRF)...")
    chunks = hybrid.search(test_question, top_k=3, method="rrf")
    
    print("Generating Answer...\n")
    answer = generator.generate(test_question, chunks)
    
    print(f"RAG Answer:\n{answer}")
