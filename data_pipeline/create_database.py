import os
import json
import glob
from parser import parse_html_to_text, parse_pdf_to_text
from chunker import chunk_text

# Paths
BASELINE_DIR = "baseline_data"
OUTPUT_DB = "data/knowledge_base.jsonl"

def process_baseline():
    """
    Reads all `.htm` and `.pdf` files from the baseline directory,
    extracts the text, chunks it, and saves it to a persistent JSON Lines file.
    """
    os.makedirs(os.path.dirname(OUTPUT_DB), exist_ok=True)
    
    # Track metrics
    total_files = 0
    total_chunks = 0
    
    # Open the output file in write mode (creates or overwrites)
    with open(OUTPUT_DB, 'w', encoding='utf-8') as db_file:
        
        # 1. Process HTML files
        html_files = glob.glob(os.path.join(BASELINE_DIR, "*.htm"))
        for filepath in html_files:
            filename = os.path.basename(filepath)
            print(f"Processing: {filename}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            text = parse_html_to_text(html_content)
            chunks = chunk_text(text, chunk_size=200, overlap=50)
            
            for i, chunk in enumerate(chunks):
                record = {
                    "id": f"{filename}_chunk_{i}",
                    "source": filename,
                    "text": chunk
                }
                # Write each chunk as a JSON string on a new line
                db_file.write(json.dumps(record, ensure_ascii=False) + '\n')
                total_chunks += 1
            total_files += 1

        # 2. Process PDF files (if any exist in the baseline)
        pdf_files = glob.glob(os.path.join(BASELINE_DIR, "*.pdf"))
        for filepath in pdf_files:
            filename = os.path.basename(filepath)
            print(f"Processing PDF: {filename}")
            
            try:
                text = parse_pdf_to_text(filepath)
                chunks = chunk_text(text, chunk_size=200, overlap=50)
                
                for i, chunk in enumerate(chunks):
                    record = {
                        "id": f"{filename}_chunk_{i}",
                        "source": filename,
                        "text": chunk
                    }
                    db_file.write(json.dumps(record, ensure_ascii=False) + '\n')
                    total_chunks += 1
                total_files += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print("\n--- Database Creation Complete ---")
    print(f"Processed {total_files} files.")
    print(f"Generated {total_chunks} total chunks.")
    print(f"Saved to: {OUTPUT_DB}")

if __name__ == "__main__":
    process_baseline()
