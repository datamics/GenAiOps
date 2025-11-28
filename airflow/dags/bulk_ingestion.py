"""
Airflow DAG for ingesting PDF documents into Qdrant vector database.

This DAG monitors the source_data directory for new PDF files and automatically
processes them when detected. Processed files are moved to processed_data directory.
"""

from datetime import datetime, timedelta
import logging
import os
import glob
import shutil
from airflow import DAG
from airflow.operators.python import PythonOperator
from utils.PdfToQdrant import DocumentProcessor
from utils.load_config import load_config_from_yaml

# Directory paths - relative to the DAG file location
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = "/opt/airflow/"
qdrant_config, embed_config, directory_config = load_config_from_yaml(f"{BASE_DIR}/dags/config/ingestion_dev.yaml")

# setup logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s") 
    
def check_for_pdf_files(**context):
    """Check if there are any PDF files in the source_data directory."""
    
    try:
        # Check if the source directory exists, raise error if not
        if os.path.exists(f"{BASE_DIR}/{directory_config.source_data_dir}"):
            
            #get list of pdf files
            pdf_files = glob.glob(os.path.join(f"{BASE_DIR}/{directory_config.source_data_dir}", "*.pdf"))
            
            if pdf_files:
                logging.info(f"Found {len(pdf_files)} PDF file(s) in {directory_config.source_data_dir}")
                # Push the PDF file paths to XCom for the next task
                context['task_instance'].xcom_push(key='PDF_FILES', value=pdf_files)
                return pdf_files
            else:
                logging.info(f"No PDF files found in {directory_config.source_data_dir}")
                return False
        else:
            raise FileNotFoundError(f"Source directory does not exist: {directory_config.source_data_dir}")
    except Exception as e:
        logging.error(f"Error checking for PDF files: {e}")
        raise

def process_all_pdfs(**context):
    """Process all PDF files in the source_data directory."""
    
    pdf_file_paths = context['task_instance'].xcom_pull(
        task_ids='check_for_pdf_files', 
        key='PDF_FILES'
    )
    
    if not pdf_file_paths:
        logging.info("No PDF files to process. Skipping processing step.")
        return True
    
    try:
        # upload each PDF one by one
        for document in pdf_file_paths:
            logging.info(f"Processing PDF: {document}")
            dp = DocumentProcessor(qdrant_config, embed_config)
            dp.main(pdf_file_path=document)
            logging.info(f"Completed processing for PDF: {document}")
            
            logging.info(f"Moving processed PDF: {document} to {directory_config.processed_data_dir}")        
            if not os.path.exists(directory_config.processed_data_dir):
                os.makedirs(directory_config.processed_data_dir)
    
            filename = os.path.basename(document)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(filename)
            destination = os.path.join(f"{BASE_DIR}/{directory_config.processed_data_dir}", f"{name}_{timestamp}{ext}")
            shutil.move(document, destination)
            logging.info(f"Moved {filename} to {f'{BASE_DIR}/{directory_config.processed_data_dir}'} directory")
    except Exception as e:
        logging.error(f"Error processing PDF files: {e}")
        raise  
        
    return True

# Default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define the DAG
with DAG(
    dag_id="pdf_to_qdrant_bulk_ingestion",
    default_args=default_args,
    description="Monitor source_data for new PDFs and ingest into Qdrant automatically",
    schedule=None,  # Manual trigger
    start_date=datetime(2025, 11, 18),
    catchup=False,
    tags=["qdrant", "pdf", "bulk_ingestion"],
) as dag:
    
    
    # Task 1: Check if there are PDF files in source_data directory
    check_pdfs = PythonOperator(
        task_id="check_for_pdf_files",
        python_callable=check_for_pdf_files,
    )
    
    # Task 2: Process all found PDF files
    process_pdfs = PythonOperator(
        task_id="process_all_pdfs",
        python_callable=process_all_pdfs,
    )

    # Define task dependencies
    check_pdfs >> process_pdfs
