"""
geminitesting.py

This script tests the validity of a Google Generative AI API key by attempting to list all available models.
If the API key is valid and working, it prints the names of the available models.
If the key is invalid or there is a connection issue, it prints an error message.

Useful for debugging authentication or checking available model options.
"""

import google.generativeai as genai

# Replace with your key
genai.configure(api_key="AIzaSyC_o4HHVxQiNukuyMTCeRqEOtZ7eJnNfFY")

try:
    models = genai.list_models()
    for model in models:
        print(model.name)
except Exception as e:
    print("API Key Test Failed:", e)
