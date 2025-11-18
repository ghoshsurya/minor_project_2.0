#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ats_optimizer.settings')
django.setup()

import google.generativeai as genai
from django.conf import settings

def test_gemini():
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        print(f"API Key configured: {settings.GEMINI_API_KEY[:10]}...")
        
        # List available models
        models = genai.list_models()
        print("Available models:")
        for model in models:
            print(f"- {model.name}")
            
        # Try to use a model
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, test message")
        print(f"Test response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_gemini()