import asyncio
import json
import os

from mcp import Resource
from mcp.types import Prompt

from agent.mcp_client import MCPClient
from agent.dial_client import DialClient
from agent.models.message import Message, Role
from agent.prompts import SYSTEM_PROMPT


# https://remote.mcpservers.org/fetch/mcp
# Pay attention that `fetch` doesn't have resources and prompts

DIAL_ENDPOINT = os.getenv("DIAL_API_ENDPOINT", "http://localhost:8000/v1/chat/completions")
DIAL_API_KEY = os.getenv("DIAL_API_KEY", "your_api_key_here")

async def main():
    #TODO:
    # 1. Create MCP client and open connection to the MCP server (use `async with {YOUR_MCP_CLIENT} as mcp_client`),
    #    mcp_server_url="http://localhost:8005/mcp"
    # 2. Get Available MCP Resources and print them
    # 3. Get Available MCP Tools, assign to `tools` variable, print tool as well
    # 4. Create DialClient
    # 5. Create list with messages and add there SYSTEM_PROMPT with instructions to LLM
    # 6. Add to messages Prompts from MCP server as User messages
    # 7. Create console chat (infinite loop + ability to exit from chat + preserve message history after the call to dial client)
    async with MCPClient(mcp_server_url="http://localhost:8005/mcp") as mcp_client:
        # 2. Get Available MCP Resources and print them
        resources: list[Resource] = await mcp_client.get_resources()
        print("Available MCP Resources:")
        for resource in resources:
            print(resource)

        # 3. Get Available MCP Tools, assign to `tools` variable, print tool as well
        tools = await mcp_client.get_tools()
        print("\nAvailable MCP Tools:")
        for tool in tools:
            print(tool)

        # 4. Create DialClient
        dial_client = DialClient(
            endpoint=DIAL_ENDPOINT,
            api_key=DIAL_API_KEY,
            mcp_client=mcp_client, 
            tools=tools
            )

        # 5. Create list with messages and add there SYSTEM_PROMPT with instructions to LLM
        messages: list[Message] = [
            Message(role=Role.SYSTEM, content=SYSTEM_PROMPT)
        ]

        # 6. Add to messages Prompts from MCP server as User messages
        prompts: list[Prompt] = await mcp_client.get_prompts()
        for prompt in prompts:
            prompt_content = await mcp_client.get_prompt(prompt.name)
            messages.append(Message(role=Role.USER, content=prompt_content))

        # 7. Create console chat (infinite loop + ability to exit from chat + preserve message history after the call to dial client)
        print("\nYou can start chatting with the AI assistant now! Type 'exit' to quit.")
        while True:
            user_input = input("👤: ")
            if user_input.lower() == "exit":
                print("Exiting chat. Goodbye!")
                break

            messages.append(Message(role=Role.USER, content=user_input))
            ai_message: Message = await dial_client.get_completion(messages)
            messages.append(ai_message)


    raise NotImplementedError()


if __name__ == "__main__":
    asyncio.run(main())
