"""
Minimal test script to verify all 16 digital personas can be invoked by a UserProxyAgent.

Usage:
    python3 test_autogen_personas.py

This script will:
1. Import all digital personas from autogen_digital_personas.py
2. Create a UserProxyAgent
3. Test each persona with a simple "Hello, introduce yourself" message
4. Report success/failure for each agent
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import AutoGen and our personas
try:
    import autogen
    from autogen_digital_personas import ALL_DIGITAL_PERSONAS, PERSONA_REGISTRY
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you have installed the required packages:")
    print("pip install pyautogen python-dotenv")
    sys.exit(1)

async def test_single_persona(user_proxy, persona_agent):
    """Test a single persona agent with a simple message."""
    try:
        # Initiate a chat with the persona
        await user_proxy.a_initiate_chat(
            persona_agent,
            message="Hello! Please introduce yourself briefly, stating your name and primary role.",
            max_turns=2  # Keep it short
        )
        return True
    except Exception as e:
        print(f"❌ Error testing {persona_agent.name}: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Starting AutoGen Digital Personas Test...")
    print(f"Found {len(ALL_DIGITAL_PERSONAS)} personas to test.\n")
    
    # Create a UserProxyAgent (this is the 'user' that will call our personas)
    user_proxy = autogen.UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",  # No human input needed for this test
        max_consecutive_auto_reply=1,
        code_execution_config=False,  # We don't need code execution for this test
        llm_config=None  # UserProxy doesn't need an LLM config for simple message passing
    )
    
    # Test each persona
    successful_tests = 0
    total_tests = len(ALL_DIGITAL_PERSONAS)
    
    for i, persona in enumerate(ALL_DIGITAL_PERSONAS, 1):
        print(f"[{i}/{total_tests}] Testing {persona.name}...")
        
        if await test_single_persona(user_proxy, persona):
            print(f"✅ {persona.name} responded successfully!\n")
            successful_tests += 1
        else:
            print(f"❌ {persona.name} failed!\n")
    
    # Final summary
    print("=" * 60)
    print(f"Test Complete! {successful_tests}/{total_tests} personas passed.")
    
    if successful_tests == total_tests:
        print("🎉 All digital personas are working correctly!")
        print("Your AutoGen Digital Persona System is ready for production use.")
    else:
        print("⚠️  Some personas failed. Please check the error messages above.")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    # Run the async main function
    success = asyncio.run(main())
    sys.exit(0 if success else 1)