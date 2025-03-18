import os

# Gemini API Configuration
# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyBLSAPqtZQ4KhCTNP9zkM2Dke9giqwhENc')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyApyXt0Voap0SOj2C6Y1SE7CMniT1xuKLU')
GEMINI_MODEL = 'gemini-pro'  # This is the correct model name

# Generation Settings
GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

# Safety Settings
SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
] 