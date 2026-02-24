import os
import torch
from transformers import pipeline

class AnswerGenerator:
    def __init__(self, model_name="Qwen/Qwen2.5-0.5B-Instruct"):
        """
        Initializes an open-weights LLM generator compliant with the assignment <32B parameter constraint.
        We default to Qwen2.5-0.5B-Instruct since it is fast and efficient for CPU/Metal devices on laptop.
        You can swap this for 'meta-llama/Llama-3.2-1B-Instruct' (requires HF token permission) 
        or 'mistralai/Mistral-7B-Instruct-v0.3' if you have the memory.
        """
        print(f"Loading Generation Model: {model_name}...")
        
        # Optimize for Mac's MPS (Metal Performance Shaders) if available, else CPU
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {device}")
        
        # Load HuggingFace text-generation pipeline
        self.generator = pipeline(
            "text-generation",
            model=model_name,
            device=device,
            torch_dtype=torch.float16 if device == "mps" else torch.float32
        )

    def build_prompt(self, question: str, retrieved_chunks: list[dict]) -> str:
        """
        Constructs the RAG prompt connecting the factual context with the user's question.
        Returns a single prompt string.
        """
        context_str = "\n---\n".join([f"Source: {c['source']}\nText: {c['text']}" for c in retrieved_chunks])
        
        prompt = f"""You are a helpful and precise assistant. Answer the user's question using ONLY the provided context. If the context does not contain the answer, say "I don't know based on the provided context." Be strictly factual and concise.

Context:
{context_str}

Question: {question}

Answer:"""
        return prompt

    def generate(self, question: str, retrieved_chunks: list[dict], max_new_tokens=50, temperature=0.1) -> str:
        """
        Generates the answer given the question and the retrieved hybrid chunks.
        """
        # The assignment calls for standard token-based evaluation metrics (F1 overlap),
        # so answers should be concise and strictly pull from context.
        prompt = self.build_prompt(question, retrieved_chunks)
        
        outputs = self.generator(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True, # Even with low temp to enforce strictness, sampling helps avoid loops
            return_full_text=False # Don't prepend the entire context in the return output
        )
        
        generated_text = outputs[0]["generated_text"].strip()
        return generated_text

if __name__ == "__main__":
    import sys
    # Add project root to python path to import the retrieving classes
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from RAG.document_query_embedder import DenseRetriever
    from RAG.sparse_embedder import SparseRetriever
    from RAG.retriever import HybridRetriever
    
    # 1. Load Retrievers
    print("Loading Retrievers...")
    dense = DenseRetriever()
    dense.load_index()
    
    sparse = SparseRetriever()
    sparse.load_index()
    
    hybrid = HybridRetriever(dense, sparse)
    
    # 2. Load Generator
    generator = AnswerGenerator()
    
    # 3. Test Full Pipeline
    test_question = "What was the original purpose of the Carnegie Technical Schools?"
    print(f"\nQuestion: {test_question}")
    
    print("Retrieving context chunks using Hybrid (RRF)...")
    chunks = hybrid.search(test_question, top_k=3, method="rrf")
    
    print("Generating Answer...\n")
    answer = generator.generate(test_question, chunks)
    
    print(f"RAG Answer:\n{answer}")
