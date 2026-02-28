import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_pipeline.scrape_websites import main as scrape_main
from data_pipeline.create_database import process_all_data
from RAG.document_query_embedder import DenseRetriever
from RAG.sparse_embedder import SparseRetriever

def run_pipeline():
    print("STEP 1: Scraping Websites")
    scrape_main()
    
    print("STEP 2: Creating Database (from baseline & scraped data)")
    process_all_data()

    print("STEP 3: Building Dense Retrieval Index (FAISS)")
    dense = DenseRetriever()
    dense.build_index()

    print("STEP 4: Building Sparse Retrieval Index (BM25)")
    sparse = SparseRetriever()
    sparse.build_index()
    
    print("DATA PIPELINE COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_pipeline()
