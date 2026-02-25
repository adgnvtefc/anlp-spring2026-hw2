import sys
import os

# Add project root to python path to import everything
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_pipeline.scrape_websites import main as scrape_main
from data_pipeline.create_database import process_all_data
from RAG.document_query_embedder import DenseRetriever
from RAG.sparse_embedder import SparseRetriever

def run_pipeline():
    print("==================================================")
    print("STEP 1: Scraping Websites")
    print("==================================================")
    scrape_main()
    
    print("\n==================================================")
    print("STEP 2: Creating Database (from baseline & scraped data)")
    print("==================================================")
    process_all_data()

    print("\n==================================================")
    print("STEP 3: Building Dense Retrieval Index (FAISS)")
    print("==================================================")
    dense = DenseRetriever()
    dense.build_index()

    print("\n==================================================")
    print("STEP 4: Building Sparse Retrieval Index (BM25)")
    print("==================================================")
    sparse = SparseRetriever()
    sparse.build_index()
    
    print("\n==================================================")
    print("DATA PIPELINE COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_pipeline()
