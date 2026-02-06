
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Config
DOWNLOAD_DIR = Path("/Users/david/david_project/知识库/microblock/download")
METADATA_FILE = DOWNLOAD_DIR / "metadata.json"
OUTPUT_FILE = Path("/Users/david/david_project/知识库/microblock/extracted_knowledge.json")

load_dotenv("/Users/david/david_project/.env")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EXTRACTION_PROMPT = """
You are an expert Knowledge Engineer. Your task is to extract structured knowledge from the provided article about MicroBlocks.

Extract the following:
1.  **Summary**: A concise 2-3 sentence summary of the article.
2.  **Entities**: Identify key entities relevant to MicroBlocks ecosystem.
    -   Types: HARDWARE (Boards, Sensors), SOFTWARE (Features, Libraries), EVENT (Conferences, Workshops), ORGANIZATION (Companies, Schools), PERSON (Key contributors), CONCEPT (Programming concepts).
    -   Format: {"name": "Name", "type": "TYPE", "description": "Brief description"}
3.  **Relations**: Identify relationships between entities.
    -   Format: {"source": "Entity A", "target": "Entity B", "relation": "RELATION_TYPE", "description": "Context"}
    -   Relation Examples: SUPPORTS, DEVELOPED_BY, FEATURED_AT, COMPATIBLE_WITH, EXTENDS.

Return the result as a valid JSON object with keys: "summary", "entities", "relations".
Do not include markdown formatting (```json), just the raw JSON.
"""

def process_article(entry):
    text_path = entry.get("text_path")
    if not text_path or not os.path.exists(text_path):
        return None
        
    print(f"Processing: {entry.get('title')}...")
    
    with open(text_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Truncate content if too long (Gemini Flash has large context, but let's be safe/efficient)
    if len(content) > 30000:
        content = content[:30000] + "...(truncated)"
        
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
            contents=[
                types.Part.from_text(text=EXTRACTION_PROMPT),
                types.Part.from_text(text=f"Article Content:\n{content}")
            ]
        )
        
        result = json.loads(response.text)
        # Add metadata to result
        result["source_url"] = entry.get("url")
        result["source_title"] = entry.get("title")
        return result
        
    except Exception as e:
        print(f"Error extracting from {entry.get('title')}: {e}")
        return None

def main():
    if not METADATA_FILE.exists():
        print("Metadata file not found. Run crawler first.")
        return
        
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
        
    all_knowledge = []
    
    print(f"Found {len(metadata)} articles to process.")
    
    for i, entry in enumerate(metadata):
        print(f"[{i+1}/{len(metadata)}] Analyzing article...")
        knowledge = process_article(entry)
        if knowledge:
            all_knowledge.append(knowledge)
        
        # Rate limit friendly
        time.sleep(1)
        
    # Save results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_knowledge, f, indent=2, ensure_ascii=False)
        
    print(f"Extraction complete. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
