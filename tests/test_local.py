import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.lambda_function import lambda_handler

if __name__ == "__main__":
    print("--- 🧪 Starting Local Test ---")
    
    dummy_event = {}
    dummy_context = None
    
    response = lambda_handler(dummy_event, dummy_context)
    
    print("\n--- 🏁 Test Complete ---")
    print(response)