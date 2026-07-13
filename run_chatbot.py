import sys
import os
import traceback
import logging

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO)

from src.modules.chatbot.services import ChatbotService

def run_test():
    print("Initializing ChatbotService...")
    service = ChatbotService()
    print("Calling generate_chat_response...")
    
    try:
        response = service.generate_chat_response("What is the policy coverage?", "")
        print("SUCCESS!")
        print(response)
    except Exception as e:
        print("\n=== CAUGHT EXCEPTION ===")
        print(f"Type: {type(e)}")
        print(f"Message: {str(e)}")
        print(f"Module: {type(e).__module__}")
        print("========================\n")

if __name__ == "__main__":
    run_test()
