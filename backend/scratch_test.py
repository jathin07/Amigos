from google import genai
import os

client = genai.Client(api_key="AIzaSyBm_QhEad26o9g7cUk14Y6pEAN0gAaYUzw")
for m in client.models.list():
    if "flash" in m.name:
        print(m.name)
