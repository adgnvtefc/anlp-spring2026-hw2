import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    sentences = nltk.tokenize.sent_tokenize(text)
    chunks = []
    
    if not sentences:
        return chunks
        
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_words = len(sentence.split())
        
        if current_length + sentence_words > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            
            overlap_words = 0
            overlap_chunk = []
            for s in reversed(current_chunk):
                s_words = len(s.split())
                if overlap_words + s_words > overlap:
                    break
                overlap_chunk.insert(0, s)
                overlap_words += s_words
                
            current_chunk = overlap_chunk
            current_length = sum(len(s.split()) for s in current_chunk)
            
        current_chunk.append(sentence)
        current_length += sentence_words
        
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks