#!/usr/bin/env python3
"""
Azure AI Foundry Agent Console Application with Yoda Transformation

This application demonstrates an agentic pattern with:
1. Foundry Web Search Agent - searches for event information
2. Yoda Transform Agent - transforms results into Yoda speak
3. Orchestrator Agent - coordinates the workflow
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase


class FoundrySearchAgent:
    """Agent that searches for information using Azure AI Foundry."""
    
    def __init__(self, project_client: AIProjectClient, agent_id: str):
        self.project_client = project_client
        self.agent_id = agent_id
        
    async def search(self, query: str) -> str:
        """Search for information using the Foundry agent."""
        try:
            print(f"🔍 [Foundry Agent] Searching for: {query}")
            
            # Create thread and send message
            thread = self.project_client.agents.threads.create()
            print(f"  📌 Created thread: {thread.id}")
            
            message = self.project_client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=query
            )
            print(f"  💬 Sent message: {message.id}")
            
            # Run agent
            print(f"  🤖 Running agent: {self.agent_id}")
            run = self.project_client.agents.runs.create_and_process(
                thread_id=thread.id,
                agent_id=self.agent_id
            )
            print(f"  ⚡ Run completed with status: {run.status}")
            
            if run.status == "failed":
                error_detail = run.last_error if hasattr(run, 'last_error') else 'Unknown error'
                print(f"  ❌ Run failed: {error_detail}")
                raise Exception(f"Foundry agent run failed: {error_detail}")
            
            # Get response
            messages = self.project_client.agents.messages.list(thread_id=thread.id)
            message_list = list(messages)
            print(f"  📨 Retrieved {len(message_list)} messages from thread")
            
            response = None
            for idx, msg in enumerate(message_list):
                print(f"    [{idx}] Role: {msg.role}")
                print(f"        Has text_messages: {hasattr(msg, 'text_messages')}")
                print(f"        Has content: {hasattr(msg, 'content')}")
                
                if hasattr(msg, 'content'):
                    print(f"        Content: {msg.content[:200] if msg.content else 'None'}...")
                if hasattr(msg, 'text_messages') and msg.text_messages:
                    print(f"        Text messages count: {len(msg.text_messages)}")
                    
                # Try different ways to get the response
                # Note: Azure AI Agents use MessageRole.AGENT (not "assistant")
                if msg.role in ["assistant", "agent"] or str(msg.role) == "MessageRole.AGENT":
                    if hasattr(msg, 'text_messages') and msg.text_messages:
                        response = msg.text_messages[-1].text.value
                        print(f"    ✓ Found response via text_messages: {len(response)} chars")
                        break
                    elif hasattr(msg, 'content') and msg.content:
                        response = msg.content
                        print(f"    ✓ Found response via content: {len(response)} chars")
                        break
            
            # Keep thread alive for visibility in Azure Foundry portal
            # (Not deleting so conversation history is preserved)
            print(f"  💾 Thread preserved: {thread.id} (visible in Azure Foundry portal)")
            print(f"  🔗 View in portal: https://ai.azure.com")
            
            if response:
                print(f"✓ [Foundry Agent] Retrieved {len(response)} characters")
                print(f"  📄 Raw response preview: {response[:150]}...")
            else:
                print(f"✗ [Foundry Agent] No response found")
                
            return response or "No results found"
            
        except Exception as e:
            print(f"✗ [Foundry Agent] Error: {e}")
            raise


class YodaTransformAgent:
    """Agent that transforms text into Yoda speak using Semantic Kernel."""
    
    def __init__(self, kernel: Kernel, service_id: str):
        self.kernel = kernel
        self.service_id = service_id
        
    async def transform(self, text: str) -> str:
        """Transform text into Yoda speak."""
        try:
            print(f"🎭 [Yoda Agent] Transforming response into Yoda speak...")
            
            # Create chat history with system message
            chat_history = ChatHistory()
            chat_history.add_system_message(
                "You are Master Yoda from Star Wars. Transform the following text into Yoda's speaking style. "
                "Maintain all factual information but restructure sentences in Yoda's characteristic pattern. "
                "Keep the transformation natural and readable. Important information, preserve you must."
            )
            chat_history.add_user_message(f"Transform this text into Yoda speak:\n\n{text}")
            
            # Get chat completion
            chat_completion: ChatCompletionClientBase = self.kernel.get_service(self.service_id)
            response = await chat_completion.get_chat_message_content(
                chat_history=chat_history,
                settings=chat_completion.get_prompt_execution_settings_class()(
                    max_tokens=1000,
                    temperature=0.7
                )
            )
            
            result = str(response)
            print(f"✓ [Yoda Agent] Transformed to {len(result)} characters")
            return result
            
        except Exception as e:
            print(f"✗ [Yoda Agent] Error: {e}")
            raise


class AgentOrchestrator:
    """Orchestrates the workflow between Foundry Search Agent and Yoda Transform Agent."""
    
    def __init__(self, search_agent: FoundrySearchAgent, transform_agent: YodaTransformAgent):
        self.search_agent = search_agent
        self.transform_agent = transform_agent
        
    async def process_query(self, query: str, use_yoda: bool = True) -> dict:
        """
        Process a query through the agent workflow.
        
        Returns:
            dict with 'original' and 'yoda' (if use_yoda=True) responses
        """
        print(f"\n{'='*60}")
        print(f"🚀 [Orchestrator] Starting workflow")
        print(f"{'='*60}\n")
        
        # Step 1: Search with Foundry Agent
        original_response = await self.search_agent.search(query)
        
        result = {
            "query": query,
            "original": original_response,
            "yoda": None
        }
        
        # Step 2: Transform with Yoda Agent (if requested)
        if use_yoda and original_response:
            result["yoda"] = await self.transform_agent.transform(original_response)
        
        print(f"\n{'='*60}")
        print(f"✓ [Orchestrator] Workflow completed")
        print(f"{'='*60}\n")
        
        return result


class AgentConsole:
    """Console application with multi-agent orchestration."""
    
    def __init__(self):
        """Initialize the agent console with configuration from environment variables."""
        load_dotenv()
        
        # Load configuration
        self.project_endpoint = os.getenv("PROJECT_ENDPOINT")
        self.agent_id = os.getenv("AGENT_ID")
        self.openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        self.openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        
        if not self.project_endpoint:
            raise ValueError("PROJECT_ENDPOINT is required in .env file")
        if not self.agent_id:
            raise ValueError("AGENT_ID is required in .env file")
        if not self.openai_endpoint or self.openai_endpoint.startswith("<"):
            raise ValueError(
                "AZURE_OPENAI_ENDPOINT is required in .env file for Yoda agent.\n"
                "Please set it to your Azure OpenAI endpoint, e.g.:\n"
                "AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/"
            )
        
        # Initialize Azure AI Project Client for Foundry Agent
        self.credential = DefaultAzureCredential()
        self.project_client = AIProjectClient(
            endpoint=self.project_endpoint,
            credential=self.credential
        )
        
        # Initialize Semantic Kernel for Yoda Agent
        self.kernel = Kernel()
        self.service_id = "yoda-chat"
        
        # Create a token provider that supplies the correct scope for Azure OpenAI
        def get_azure_openai_token():
            """Get Azure AD token for Azure OpenAI with the correct scope."""
            return self.credential.get_token("https://cognitiveservices.azure.com/.default").token
        
        self.kernel.add_service(
            AzureChatCompletion(
                service_id=self.service_id,
                deployment_name=self.openai_deployment,
                endpoint=self.openai_endpoint,
                api_version=self.openai_api_version,
                ad_token_provider=get_azure_openai_token
            )
        )
        
        # Initialize agents
        self.search_agent = FoundrySearchAgent(self.project_client, self.agent_id)
        self.transform_agent = YodaTransformAgent(self.kernel, self.service_id)
        self.orchestrator = AgentOrchestrator(self.search_agent, self.transform_agent)
        
        print(f"✓ Initialized Multi-Agent System")
        print(f"  Foundry Agent: {self.agent_id}")
        print(f"  Yoda Agent: {self.openai_deployment}")
        print()
    
    async def send_message(self, user_message: str, use_yoda: bool = True) -> dict:
        """
        Send a message through the agent orchestration workflow.
        
        Args:
            user_message: The message/query to process
            use_yoda: Whether to transform the response into Yoda speak
            
        Returns:
            dict with 'original' and 'yoda' responses
        """
        try:
            result = await self.orchestrator.process_query(user_message, use_yoda)
            return result
        except Exception as e:
            print(f"\n✗ Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return None
    
    def get_agent_info(self) -> dict:
        """Get information about the connected agent."""
        try:
            agent = self.project_client.agents.get_agent(agent_id=self.agent_id)
            return {
                "id": agent.id,
                "name": agent.name if hasattr(agent, 'name') else 'N/A',
                "description": agent.description if hasattr(agent, 'description') else None,
                "model": agent.model if hasattr(agent, 'model') else 'N/A',
                "instructions": agent.instructions[:100] + "..." if hasattr(agent, 'instructions') and agent.instructions and len(agent.instructions) > 100 else (agent.instructions if hasattr(agent, 'instructions') else None),
            }
        except Exception as e:
            print(f"✗ Error getting agent info: {e}", file=sys.stderr)
            return None
    
    async def interactive_mode(self):
        """Run the agent in interactive chat mode."""
        print("=" * 60)
        print("MULTI-AGENT SYSTEM - INTERACTIVE MODE")
        print("=" * 60)
        
        # Show agent info
        agent_info = self.get_agent_info()
        if agent_info:
            print(f"\nFoundry Agent Details:")
            print(f"  Name: {agent_info.get('name', 'N/A')}")
            print(f"  Model: {agent_info.get('model', 'N/A')}")
            if agent_info.get('description'):
                print(f"  Description: {agent_info['description']}")
        
        print("\n🎭 Yoda transformation is ENABLED by default")
        print("\nCommands:")
        print("  Type your query to search and transform")
        print("  'yoda off' - Disable Yoda transformation")
        print("  'yoda on'  - Enable Yoda transformation")
        print("  'exit' or 'quit' - End session")
        print("-" * 60)
        print()
        
        use_yoda = True
        
        try:
            while True:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\nGoodbye!")
                    break
                
                if user_input.lower() == 'yoda off':
                    use_yoda = False
                    print("✓ Yoda transformation disabled\n")
                    continue
                
                if user_input.lower() == 'yoda on':
                    use_yoda = True
                    print("✓ Yoda transformation enabled\n")
                    continue
                
                # Send message and get response
                result = await self.send_message(user_input, use_yoda)
                
                if result:
                    print(f"\n{'='*60}")
                    if use_yoda and result.get('yoda'):
                        print(f"🎭 Yoda Response:\n{result['yoda']}")
                    else:
                        print(f"📝 Response:\n{result['original']}")
                    print(f"{'='*60}\n")
                else:
                    print("\n✗ Failed to get response from agents")
                    print()
                
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
        except Exception as e:
            print(f"\n✗ Error in interactive mode: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()


async def main_async():
    """Async main entry point for the application."""
    print("\n" + "=" * 60)
    print("MULTI-AGENT SYSTEM: FOUNDRY + YODA")
    print("=" * 60)
    print()
    
    try:
        # Initialize the agent console
        console = AgentConsole()
        
        # Check if a message was provided as command line argument
        if len(sys.argv) > 1:
            # Check for --no-yoda flag
            use_yoda = "--no-yoda" not in sys.argv
            
            # Get message (filter out flags)
            message_parts = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
            message = " ".join(message_parts)
            
            if not message:
                print("Error: No query provided", file=sys.stderr)
                return 1
            
            print(f"Query: {message}")
            print(f"Yoda Mode: {'ON' if use_yoda else 'OFF'}\n")
            
            result = await console.send_message(message, use_yoda)
            
            if result:
                print(f"\n{'='*60}")
                if use_yoda and result.get('yoda'):
                    print(f"🎭 Yoda Response:\n{result['yoda']}")
                    print(f"\n{'─'*60}")
                    print(f"📝 Original Response:\n{result['original']}")
                else:
                    print(f"📝 Response:\n{result['original']}")
                print(f"{'='*60}\n")
                return 0
            else:
                return 1
        else:
            # Interactive mode
            await console.interactive_mode()
            return 0
            
    except ValueError as e:
        print(f"✗ Configuration Error: {e}", file=sys.stderr)
        print("\nPlease ensure you have a .env file with:", file=sys.stderr)
        print("  PROJECT_ENDPOINT=<your-endpoint>", file=sys.stderr)
        print("  AGENT_ID=<your-agent-id>", file=sys.stderr)
        print("  AZURE_OPENAI_ENDPOINT=<your-openai-endpoint>", file=sys.stderr)
        print("  AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Fatal Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 2


def main():
    """Main entry point for the application."""
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
