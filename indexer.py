import os
import glob
import chromadb
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BOOKS_DIR = os.path.join("知识库", "books")
DB_PATH = os.path.join("知识库", "chroma_db")
COLLECTION_NAME = "books_knowledge_base"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for the given files to be active."""
    print("Waiting for file processing...")
    for name in (f.name for f in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files active")

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

def is_quota_error(exception):
    return "429" in str(exception) or "Resource exhausted" in str(exception)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception(is_quota_error),
    reraise=True
)
def extract_text_with_gemini(gemini_file, start_page, end_page):
    """
    Extracts text from a range of pages using Gemini.
    """
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    
    prompt = f"""
    Please extract the text from pages {start_page} to {end_page} of this PDF. 
    Maintain the original structure and hierarchy. 
    If there are tables, represent them as Markdown tables.
    Return the text for each page clearly demarcated by '--- PAGE X ---'.
    """
    
    response = model.generate_content([gemini_file, prompt], request_options={"timeout": 600})
    return response.text

def main():
    print(f"Starting Gemini-powered PDF indexer...")
    
    # Ensure directory exists
    if not os.path.exists(BOOKS_DIR):
        print(f"Error: Directory '{BOOKS_DIR}' does not exist.")
        return

    # Find all PDF files
    pdf_files = glob.glob(os.path.join(BOOKS_DIR, "*.pdf"))
    if not pdf_files:
        print("No PDF files found to process.")
        return

    # Initialize ChromaDB
    print(f"Initializing ChromaDB at {DB_PATH}...")
    try:
        # Compatibility handling
        chroma_client = None
        try:
             chroma_client = chromadb.PersistentClient(path=DB_PATH)
        except AttributeError:
             from chromadb.config import Settings
             chroma_client = chromadb.Client(Settings(
                 chroma_db_impl="duckdb+parquet",
                 persist_directory=DB_PATH
             ))
        
        collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    except Exception as e:
        print(f"Failed to initialize ChromaDB: {e}")
        return

    start_time = time.time()
    
    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        print(f"\nProcessing: {filename} with Gemini...")
        
        try:
            # Upload PDF to Gemini
            gemini_file = upload_to_gemini(pdf_path, mime_type="application/pdf")
            wait_for_files_active([gemini_file])
            
            # Get total pages using PyMuPDF locally
            import fitz
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()
            
            print(f"Total pages to index: {total_pages}")
            
            batch_size = 20
            all_page_texts = []
            
            for start in range(1, total_pages + 1, batch_size):
                end = min(start + batch_size - 1, total_pages)
                print(f"Extracting pages {start} to {end}...")
                
                try:
                    batch_text = extract_text_with_gemini(gemini_file, start, end)
                    # Simple splitting by demarcation
                    pages = batch_text.split("--- PAGE ")
                    for p in pages:
                        if not p.strip(): continue
                        # Re-extract page number and content
                        parts = p.split(" ---", 1)
                        if len(parts) == 2:
                            try:
                                page_num = int(parts[0].strip())
                                content = parts[1].strip()
                                all_page_texts.append((page_num, content))
                            except ValueError:
                                all_page_texts.append((len(all_page_texts) + 1, p.strip()))
                        else:
                            all_page_texts.append((len(all_page_texts) + 1, p.strip()))
                except Exception as e:
                    print(f"Error extracting batch {start}-{end}: {e}")
                
                # Proactive delay to avoid rate limits
                time.sleep(5)

            if all_page_texts:
                print(f"Upserting {len(all_page_texts)} pages to ChromaDB...")
                documents = [text for num, text in all_page_texts]
                metadatas = [{"file_path": pdf_path, "filename": filename, "page": num, "source": "gemini-ocr"} for num, text in all_page_texts]
                ids = [f"{filename}_gemini_ocr_p{num}" for num, text in all_page_texts]
                
                if hasattr(collection, 'upsert'):
                    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
                else:
                    collection.add(documents=documents, metadatas=metadatas, ids=ids)
                
                if hasattr(chroma_client, 'persist'):
                    chroma_client.persist()
                    
                print(f"Finished indexing {filename} with Gemini OCR.")
            else:
                print(f"No text extracted from {filename} via Gemini.")

            # Cleanup Gemini file
            genai.delete_file(gemini_file.name)
            print(f"Deleted Gemini file reference.")

        except Exception as e:
            print(f"Failed to process {pdf_path} with Gemini: {e}")

    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
