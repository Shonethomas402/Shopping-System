import os
import google.generativeai as genai

def initialize_gemini():
    # Get API key from environment variable or use a default one
    # api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyBLSAPqtZQ4KhCTNP9zkM2Dke9giqwhENc')
    api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyApyXt0Voap0SOj2C6Y1SE7CMniT1xuKLU')
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # List available models and their details
        models = genai.list_models()
        for model in models:
            print(f"Available model: {model.name}")
            
        return True
    except Exception as e:
        print(f"Error initializing Gemini: {str(e)}")
        return False 