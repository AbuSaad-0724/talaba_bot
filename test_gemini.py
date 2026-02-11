#!/usr/bin/env python3
"""
Gemini API Test
Tests Gemini AI service with various prompts
"""

import asyncio
from services.gemini_service import gemini_generate, gemini_chat
from config import GEMINI_API_KEY

async def test_gemini():
    """Test Gemini API functionality"""
    print("🤖 Testing Gemini AI Service\n")
    print("=" * 70)
    
    # Check API key
    print("\n1. API Key Check")
    print("-" * 70)
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY not configured!")
        print("   Please set GEMINI_API_KEY in .env file")
        return
    else:
        masked_key = GEMINI_API_KEY[:10] + "..." + GEMINI_API_KEY[-10:]
        print(f"✅ API Key configured: {masked_key}")
    
    # Test 1: Simple generation
    print("\n2. Simple Text Generation")
    print("-" * 70)
    try:
        prompt = "Salom! Men talaba botman. O'zingizni qisqacha tanishtiring."
        print(f"Prompt: {prompt}\n")
        
        response = await gemini_generate(prompt)
        print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
        print("\n✅ Simple generation successful")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Chat conversation
    print("\n3. Chat Conversation")
    print("-" * 70)
    try:
        messages = [
            {"role": "user", "parts": ["Salom! Men matematika bo'yicha yordam kerak."]},
            {"role": "model", "parts": ["Salom! Albatta yordam beraman. Qanday savol bor?"]},
            {"role": "user", "parts": ["2+2 nechiga teng?"]}
        ]
        
        print("Conversation:")
        for msg in messages:
            role = "👤 User" if msg["role"] == "user" else "🤖 Bot"
            print(f"{role}: {msg['parts'][0]}")
        
        print("\nGenerating response...")
        response = await gemini_chat(messages)
        print(f"\n🤖 Bot: {response}")
        print("\n✅ Chat conversation successful")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Long text generation
    print("\n4. Long Text Generation (Referat)")
    print("-" * 70)
    try:
        prompt = """
        "Sun'iy intellekt" mavzusida qisqa referat yozing.
        Kirish, asosiy qism va xulosa bo'lsin.
        """
        
        print(f"Prompt: {prompt.strip()}\n")
        print("Generating referat...")
        
        response = await gemini_generate(prompt, max_tokens=1000)
        
        # Show first 300 characters
        preview = response[:300] + "..." if len(response) > 300 else response
        print(f"\nResponse preview:\n{preview}")
        print(f"\nTotal length: {len(response)} characters")
        print("\n✅ Long text generation successful")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Structured output (Test questions)
    print("\n5. Structured Output (Test Questions)")
    print("-" * 70)
    try:
        prompt = """
        Informatika fanidan 3 ta test savoli yarating.
        Har bir savol uchun 4 ta variant va to'g'ri javobni ko'rsating.
        """
        
        print(f"Prompt: {prompt.strip()}\n")
        print("Generating test questions...")
        
        response = await gemini_generate(prompt)
        print(f"\nResponse:\n{response[:400]}..." if len(response) > 400 else f"\nResponse:\n{response}")
        print("\n✅ Structured output successful")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Error handling
    print("\n6. Error Handling Test")
    print("-" * 70)
    try:
        # Very long prompt to test limits
        long_prompt = "Test " * 10000
        print(f"Testing with very long prompt ({len(long_prompt)} chars)...")
        
        response = await gemini_generate(long_prompt[:8000])  # Limit to 8000 chars
        print("✅ Long prompt handled successfully")
    except Exception as e:
        print(f"⚠️  Expected error: {str(e)[:100]}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ Gemini API testing completed!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_gemini())
