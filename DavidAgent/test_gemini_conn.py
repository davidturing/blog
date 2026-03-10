import google.genai as genai
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
os.environ['GRPC_DNS_RESOLVER'] = 'native'
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key, transport='rest')

async def test_conn():
    print(f"Testing connectivity with key: {api_key[:10]}...")
    
    try:
        print("Listing models with generateContent support...")
        for m in genai.list_models():
             if 'generateContent' in m.supported_generation_methods:
                  print(f" - {m.name}")
    except Exception as e:
        print(f"Failed to list models: {e}")

    # Use a likely candidate based on common naming
    model_name = 'models/gemini-1.5-flash'
    print(f"Final attempt with {model_name}...")
    model = genai.GenerativeModel(model_name)
    try:
        response = await model.generate_content_async("Hello")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_conn())
