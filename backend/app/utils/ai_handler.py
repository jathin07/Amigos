from google import genai
from flask import current_app

def analyze_notes_with_ai(notes: str) -> str:
    """
    Calls the Gemini API (new genai SDK) to analyze the given notes and return a friendly helpful travel tip.
    """
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        return ""
        
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        Act as a friendly, expert travel agent. Read this customer's trip planning note. 
        If they mention specific needs (like traveling with kids, a honeymoon, elderly, budget constraints, adventure, etc.), 
        give exactly ONE 1-2 sentence friendly travel tip or suggestion related to our services that fits their need. 
        Do not say "Sure" or greet them, just output the tip directly.
        If the note is generic or short, return exactly nothing (empty string).
        
        Customer Note: "{notes}"
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        text = response.text.strip()
        
        return text
    except Exception as e:
        print(f"AI API Error: {e}")
        return ""
