import os
import torch
from transformers import pipeline
from RAG.document_query_embedder import DenseRetriever
from RAG.sparse_embedder import SparseRetriever
from RAG.retriever import HybridRetriever

class AnswerGenerator:
    def __init__(self, model_name="Qwen/Qwen2.5-1.5B-Instruct"):
        print(f"Loading Generation Model: {model_name}...")
        
        if torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
        
        print(f"Using device: {device}")
        
        self.generator = pipeline(
            "text-generation",
            model=model_name,
            device=device,
            torch_dtype=torch.float16
        )

    def build_messages(self, question: str, retrieved_chunks: list[dict]) -> list[dict]:
        context_str = "\n---\n".join([f"Source: {c['source']}\nText: {c['text']}" for c in retrieved_chunks])
        
        system_prompt = "You are a helpful and precise assistant. Answer the user's question using ONLY the provided context. Respond minimally in one sentence; do not explain your reasoning."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Context:\nSource: history.txt\nText: Pittsburgh was named in 1758 by General John Forbes, in honor of British statesman William Pitt, 1st Earl of Chatham.\n\nQuestion: Who is Pittsburgh named after?"},
            {"role": "assistant", "content": "William Pitt"},
            {"role": "user", "content": "Context:\nSource: ml_conferences.pdf\nText: The International Conference on Machine Learning (ICML) is the leading international academic conference in machine learning. Its first iteration was held in Pittsburgh in 1980.\n\nQuestion: What famous machine learning venue had its first conference in Pittsburgh in 1980?"},
            {"role": "assistant", "content": "ICML"},
            {"role": "user", "content": "Context:\nSource: events.html\nText: October Schedule for PPG Paints Arena: Oct 12 - Penguins vs Capitals. Oct 13 - Billie Eilish concert. Oct 15 - Bruce Springsteen.\n\nQuestion: What musical artist is performing at PPG Arena on October 13?"},
            {"role": "assistant", "content": "Billie Eilish"},
            {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {question}"}
        ]
        return messages

    def generate(self, question: str, retrieved_chunks: list[dict], max_new_tokens=50) -> str:
        messages = self.build_messages(question, retrieved_chunks)
        
        prompt = self.generator.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        outputs = self.generator(
            prompt,
            max_new_tokens=max_new_tokens,
            return_full_text=False,
            temperature=None,
            top_p=None,
            top_k=None,
            do_sample=False
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
    chunks = hybrid.search(test_question, top_k=10, method="rrf")
    
    print("Generating Answer...\n")
    answer = generator.generate(test_question, chunks)
    
    print(f"RAG Answer:\n{answer}")
