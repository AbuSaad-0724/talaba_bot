#!/usr/bin/env python3
"""
PowerPoint Generation Debug Tool
Tests PPTX generation with various content formats
"""

from utils.pptx_gen import create_presentation_pptx
from utils.template_gen import create_starter_template
import os

def test_ppt_generation():
    """Test PowerPoint generation with different content"""
    print("🔍 Testing PowerPoint Generation...\n")
    
    # Test 1: Simple content with ||| delimiter
    print("Test 1: Simple content with ||| delimiter")
    print("-" * 60)
    content1 = """
||| Kirish
Bu test prezentatsiyasi.
AI tomonidan yaratilgan.

||| Asosiy Qism
• Birinchi nuqta
• Ikkinchi nuqta
• Uchinchi nuqta

||| Xulosa
Prezentatsiya muvaffaqiyatli yaratildi.
"""
    
    try:
        output1 = "temp/test_ppt_simple.pptx"
        os.makedirs("temp", exist_ok=True)
        create_presentation_pptx("Test Prezentatsiya", content1, output1)
        print(f"✅ Created: {output1}")
        print(f"   Size: {os.path.getsize(output1)} bytes\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Test 2: Content with "Slayd" pattern
    print("Test 2: Content with 'Slayd' pattern")
    print("-" * 60)
    content2 = """
Slayd 1: Kirish
Bu ikkinchi test.

Slayd 2: Asosiy
Ma'lumotlar bu yerda.

Slayd 3: Xulosa
Yakuniy fikrlar.
"""
    
    try:
        output2 = "temp/test_ppt_slayd.pptx"
        create_presentation_pptx("Slayd Test", content2, output2)
        print(f"✅ Created: {output2}")
        print(f"   Size: {os.path.getsize(output2)} bytes\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Test 3: Content with double newlines
    print("Test 3: Content with double newlines")
    print("-" * 60)
    content3 = """
Birinchi Slide
Bu birinchi slide matni.

Ikkinchi Slide
Bu ikkinchi slide matni.

Uchinchi Slide
Bu uchinchi slide matni.
"""
    
    try:
        output3 = "temp/test_ppt_newlines.pptx"
        create_presentation_pptx("Newline Test", content3, output3)
        print(f"✅ Created: {output3}")
        print(f"   Size: {os.path.getsize(output3)} bytes\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Test 4: Template generation
    print("Test 4: Template generation")
    print("-" * 60)
    try:
        create_starter_template()
        if os.path.exists("data/templates/default.pptx"):
            print(f"✅ Template exists")
            print(f"   Size: {os.path.getsize('data/templates/default.pptx')} bytes\n")
        else:
            print("❌ Template not created\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    print("=" * 60)
    print("✅ PowerPoint generation tests completed!")

if __name__ == "__main__":
    test_ppt_generation()
