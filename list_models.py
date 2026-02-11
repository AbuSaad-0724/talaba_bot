#!/usr/bin/env python3
"""
List AI Models
Shows available AI models from different providers
"""

import google.generativeai as genai
from config import GEMINI_API_KEY
import asyncio

def list_gemini_models():
    """List available Gemini models"""
    print("🤖 Available Gemini Models\n")
    print("=" * 70)
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        print("\nFetching models from Google AI...\n")
        
        models = genai.list_models()
        
        gemini_models = []
        for model in models:
            if 'gemini' in model.name.lower():
                gemini_models.append(model)
        
        if gemini_models:
            print(f"Found {len(gemini_models)} Gemini models:\n")
            
            for i, model in enumerate(gemini_models, 1):
                print(f"{i}. {model.name}")
                print(f"   Display Name: {model.display_name}")
                print(f"   Description: {model.description[:100]}..." if len(model.description) > 100 else f"   Description: {model.description}")
                
                # Supported generation methods
                if hasattr(model, 'supported_generation_methods'):
                    methods = ', '.join(model.supported_generation_methods)
                    print(f"   Methods: {methods}")
                
                # Input/Output token limits
                if hasattr(model, 'input_token_limit'):
                    print(f"   Input Limit: {model.input_token_limit:,} tokens")
                if hasattr(model, 'output_token_limit'):
                    print(f"   Output Limit: {model.output_token_limit:,} tokens")
                
                print()
        else:
            print("⚠️  No Gemini models found")
        
        # Recommended models
        print("\n" + "=" * 70)
        print("Recommended Models for Bot:")
        print("=" * 70)
        print("\n1. gemini-1.5-flash")
        print("   ✅ Fast and efficient")
        print("   ✅ Good for chat and quick responses")
        print("   ✅ Lower cost")
        
        print("\n2. gemini-1.5-pro")
        print("   ✅ More accurate")
        print("   ✅ Better for complex tasks")
        print("   ✅ Higher quality output")
        
        print("\n3. gemini-pro")
        print("   ✅ Balanced performance")
        print("   ✅ Good for general use")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPossible issues:")
        print("  1. Invalid GEMINI_API_KEY")
        print("  2. Network connection problem")
        print("  3. API quota exceeded")

def list_openai_models():
    """List OpenAI models (if configured)"""
    print("\n\n🤖 OpenAI Models\n")
    print("=" * 70)
    
    try:
        from config import OPENAI_API_KEY
        
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            print("⚠️  OpenAI API key not configured")
            print("\nAvailable OpenAI models (reference):")
            print("  • gpt-4-turbo")
            print("  • gpt-4")
            print("  • gpt-3.5-turbo")
            print("  • gpt-3.5-turbo-16k")
            return
        
        # If key is configured, try to list models
        import openai
        openai.api_key = OPENAI_API_KEY
        
        print("✅ OpenAI API key configured")
        print("\nRecommended models:")
        print("  • gpt-4-turbo (most capable)")
        print("  • gpt-3.5-turbo (fast and efficient)")
        
    except ImportError:
        print("⚠️  OpenAI library not installed")
        print("   Install: pip install openai")
    except Exception as e:
        print(f"⚠️  Could not check OpenAI: {e}")

def show_current_config():
    """Show current AI configuration"""
    print("\n\n⚙️ Current Bot Configuration\n")
    print("=" * 70)
    
    try:
        from services.gemini_service import MODEL_NAME
        print(f"Gemini Model: {MODEL_NAME}")
    except:
        print("Gemini Model: Not configured")
    
    try:
        from services.ai_service import OPENAI_MODEL
        print(f"OpenAI Model: {OPENAI_MODEL}")
    except:
        print("OpenAI Model: Not configured")

if __name__ == "__main__":
    list_gemini_models()
    list_openai_models()
    show_current_config()
    
    print("\n" + "=" * 70)
    print("✅ Model listing completed!")
