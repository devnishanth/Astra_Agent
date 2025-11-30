from mcp import ClientSession, StdioServerParameters, types
import json
import nest_asyncio
import asyncio
from typing import List
from mcp.client.stdio import stdio_client
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

nest_asyncio.apply()

class MCP_ChatBot:

    def __init__(self):
        self.session: ClientSession = None
        self.available_tools: List[dict] = []

    async def process_query(self, query: str):
        messages = [SystemMessage("You are an helpful AI agent and you have access to set of tools from MCP server. "
                                  "You access the tools according to the users preference, if he didnt not specify you are good to go with ID enumeration method. "
                                  "And you can also choose the alternative approach if one tool fails."
                                  "When usernames are identified use brute force function to test for commonly used passwords."),
                    HumanMessage(content=query)]


        openai = ChatOpenAI(
            model_name="meta-llama/llama-4-scout-17b-16e-instruct",
            openai_api_key="use_api_key",  # Your Groq/OpenAI API key
            openai_api_base="https://api.groq.com/openai/v1",
            temperature=0.0,
        )

        openai_with_tools = openai.bind_tools(tools=self.available_tools)

        while True:
            # Ask model
            response = openai_with_tools.invoke(input=messages,)

            # Always show assistant text (if any)
            if response.content:
                # Handle case where response.content is list instead of str
                if isinstance(response.content, list):
                    resp_text = " ".join(
                        [c.text for c in response.content if hasattr(c, "text")]
                    )
                else:
                    resp_text = str(response.content)

                print(f"\nAssistant: {resp_text}")
                messages.append(AIMessage(content=resp_text))

            # Check if model requested a tool
            tool_calls = response.additional_kwargs.get("tool_calls", [])
            if not tool_calls:
                # No tool calls → stop
                break

            for call in tool_calls:
                tool_name = call["function"]["name"]
                tool_args = call["function"]["arguments"]

                # Parse JSON string → dict
                if isinstance(tool_args, str):
                    try:
                        tool_args = json.loads(tool_args)
                    except json.JSONDecodeError:
                        print(f"[ERROR] Could not parse tool args: {tool_args}")
                        return

                print(f"\n[Tool request] {tool_name} with args: {tool_args}")

                # Run MCP tool
                result = await self.session.call_tool(tool_name, arguments=tool_args)

                # Normalize result.content into a string
                tool_output = ""
                if isinstance(result.content, list):
                    tool_output = " ".join(
                        [c.text for c in result.content if hasattr(c, "text")]
                    )
                elif isinstance(result.content, str):
                    tool_output = result.content
                else:
                    tool_output = str(result.content)

                # Feed tool result back to model
                messages.append(
                    AIMessage(
                        content=tool_output,
                        additional_kwargs={"tool_call_id": call["id"]}
                    )
                )
                print(tool_output)
    async def chat_loop(self):
        print("\nMCP Chatbot Started")
        print("Type your queries or 'quit' to exit")

        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == "quit":
                    break

                await self.process_query(query)
                print("\n")
            except Exception as e:
                print(f"\nError 1: {str(e)}")

    async def connect_to_server_and_run(self):
        server_params = StdioServerParameters(
            command="python3",
            args=["mcp_server.py"],
            env=None,
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                await session.initialize()

                response = await session.list_tools()
                tools = response.tools
                print("\nConnected to server with Tools", [tool.name for tool in tools])

                self.available_tools = [{
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                } for tool in response.tools]

                await self.chat_loop()

async def main():
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_server_and_run()

if __name__ == "__main__":
    asyncio.run(main())
