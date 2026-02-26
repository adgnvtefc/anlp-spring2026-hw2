import os
import json
import glob
from data_pipeline.parser import parse_html_to_text, parse_pdf_to_text
from data_pipeline.chunker import chunk_text

BASELINE_DIR = "baseline_data"
SCRAPED_DIR = "scraped_data"
OUTPUT_DB = "data/knowledge_base.jsonl"

def process_file(filepath, ext, db_file):
    filename = os.path.basename(filepath)
    print(f"Processing: {filename}")
    chunks_created = 0
    try:
        if ext == 'htm':
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            text = parse_html_to_text(html_content)
        elif ext == 'pdf':
            text = parse_pdf_to_text(filepath)
        else:
            return 0
            
        chunks = chunk_text(text, chunk_size=150, overlap=30)
        
        for i, chunk in enumerate(chunks):
            record = {
                "id": f"{filename}_chunk_{i}",
                "source": filename,
                "text": chunk
            }
            db_file.write(json.dumps(record, ensure_ascii=False) + '\n')
            chunks_created += 1
            
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        
    return chunks_created
    

def process_all_data():
    os.makedirs(os.path.dirname(OUTPUT_DB), exist_ok=True)
    
    total_files = 0
    total_chunks = 0
    
    # We will search both directories
    search_dirs = [BASELINE_DIR, SCRAPED_DIR]
    
    with open(OUTPUT_DB, 'w', encoding='utf-8') as db_file:
        for directory in search_dirs:
            if not os.path.exists(directory):
                continue
                
            # Process HTML
            html_files = glob.glob(os.path.join(directory, "*.htm")) + glob.glob(os.path.join(directory, "*.html"))
            for filepath in html_files:
                chunks_added = process_file(filepath, 'htm', db_file)
                total_chunks += chunks_added
                total_files += 1
                
            # Process PDFs
            pdf_files = glob.glob(os.path.join(directory, "*.pdf"))
            for filepath in pdf_files:
                chunks_added = process_file(filepath, 'pdf', db_file)
                total_chunks += chunks_added
                total_files += 1

    print("\n--- Database Creation Complete ---")
    print(f"Processed {total_files} files.")
    print(f"Generated {total_chunks} total chunks.")
    print(f"Saved to: {OUTPUT_DB}")

if __name__ == "__main__":
    process_all_data()
