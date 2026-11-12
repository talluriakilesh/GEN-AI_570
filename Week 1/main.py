import os
from dotenv import load_dotenv
from google import genai

# Step 1: Load API key from .env
load_dotenv()

# Step 2: Read Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

# Step 3: Initialize Gemini client
client = genai.Client(api_key=api_key)

# Step 4: Make LLM call (Using gemini-3.5-flash-lite to avoid server capacity spikes)
response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Explain Generative AI with two real-world examples."
)

# Step 5: Display response
print("\nLLM Response:")
print(response.text)