def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    """
    Splits a large string of text into smaller chunks based on word count.
    A sliding window overlap ensures context is preserved across chunk boundaries.
    """
    words = text.split()
    chunks = []
    
    if not words:
        return chunks
        
    # Slide a window of size `chunk_size` over the words array
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunks.append(" ".join(chunk_words))
        
        # Break if the end of the text is reached
        if i + chunk_size >= len(words):
            break
            
    return chunks

# More advanced chunking can be added here using NLTK sentence tokenization
# or Huggingface tokenizers to chunk tightly around semantic boundaries instead of whitespace.
