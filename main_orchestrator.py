"""
Main Orchestrator for David's AutoGen Digital Persona System

This script serves as the central hub that connects David (the user) with his 16 digital personas.
It acts as the '总调度助手' (Chief Orchestrator), automatically routing tasks to the appropriate agents.

Architecture:
- User (David) <-> Main Orchestrator (This script) <-> 16 Digital Personas (AutoGen AssistantAgents)
"""

import os
import sys
import asyncio
from typing import List, Optional
from dotenv import load_dotenv

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import AutoGen and our personas
import autogen
from autogen_digital_personas import ALL_DIGITAL_PERSONAS, PERSONA_REGISTRY

class DavidOrchestrator:
    """
    The main orchestrator that manages communication between David and his digital personas.
    
    Responsibilities:
    1. Initialize all digital personas
    2. Create a UserProxyAgent to represent David
    3. Route incoming tasks to the most appropriate persona(s)
    4. Handle multi-agent collaboration when needed
    5. Return final results directly to David
    """
    
    def __init__(self):
        """Initialize the orchestrator with all digital personas."""
        self.personas = ALL_DIGITAL_PERSONAS
        self.persona_registry = PERSONA_REGISTRY
        
        # Create the UserProxyAgent that represents David
        self.user_proxy = autogen.UserProxyAgent(
            name="David_Proxy",
            human_input_mode="NEVER",  # The orchestrator handles all decisions
            max_consecutive_auto_reply=10,
            code_execution_config=False,
            llm_config=None,
            system_message="You are David's proxy in the AutoGen system. You receive tasks from David and coordinate with his digital personas to complete them."
        )
        
        print(f"✅ DavidOrchestrator initialized with {len(self.personas)} digital personas.")
    
    async def route_task(self, task_description: str, target_persona: Optional[str] = None) -> str:
        """
        Route a task to the appropriate digital persona(s).
        
        Args:
            task_description: The task description from David
            target_persona: Optional specific persona name to target
            
        Returns:
            The final result from the persona(s)
        """
        if target_persona:
            # If a specific persona is requested, use it directly
            if target_persona not in self.persona_registry:
                available_names = list(self.persona_registry.keys())
                return f"❌ Error: Persona '{target_persona}' not found. Available personas: {available_names}"
            
            selected_persona = self.persona_registry[target_persona]
            print(f"🎯 Routing task to specific persona: {selected_persona.name}")
        else:
            # TODO: Implement intelligent routing logic based on task description
            # For now, default to the first persona (Tech_Enthusiast)
            selected_persona = self.personas[0]
            print(f"🤖 Auto-routing task to: {selected_persona.name}")
        
        # Initiate chat with the selected persona
        await self.user_proxy.a_initiate_chat(
            selected_persona,
            message=task_description,
            max_turns=10
        )
        
        # Return the last message from the chat history as the result
        if self.user_proxy.chat_messages and len(self.user_proxy.chat_messages[selected_persona]) > 0:
            last_message = self.user_proxy.chat_messages[selected_persona][-1]
            return last_message.get("content", "No content returned.")
        else:
            return "❌ No response received from the persona."
    
    async def run_interactive_mode(self):
        """Run an interactive mode where David can input tasks continuously."""
        print("\n🚀 David's AutoGen Digital Persona System is ready!")
        print("Enter your tasks below. Type 'exit' to quit.")
        print("You can also specify a persona like: '@Tech_Enthusiast write a blog post about AI'")
        print("-" * 80)
        
        while True:
            try:
                user_input = input("\nDavid: ").strip()
                if user_input.lower() == 'exit':
                    print("👋 Goodbye, David!")
                    break
                
                if not user_input:
                    continue
                
                # Check if a specific persona is mentioned
                target_persona = None
                task_text = user_input
                
                if user_input.startswith('@'):
                    parts = user_input[1:].split(' ', 1)
                    if len(parts) == 2:
                        potential_persona, task_text = parts
                        if potential_persona in self.persona_registry:
                            target_persona = potential_persona
                        else:
                            print(f"⚠️ Warning: Persona '{potential_persona}' not found. Using auto-routing.")
                
                # Route the task and get the result
                result = await self.route_task(task_text, target_persona)
                print(f"\n🤖 Result:\n{result}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye, David!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

# Entry point for the orchestrator
async def main():
    """Main entry point."""
    orchestrator = DavidOrchestrator()
    
    # Check if we're running in interactive mode or with command line args
    if len(sys.argv) > 1:
        # Run a single task from command line
        task = " ".join(sys.argv[1:])
        result = await orchestrator.route_task(task)
        print(result)
    else:
        # Run interactive mode
        await orchestrator.run_interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())