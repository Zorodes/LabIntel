import os
import asyncio
from dotenv import load_dotenv
load_dotenv(dotenv_path="apis.env")

os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY")  # workaround for async client

from llama_index.core import Settings
from llama_index.llms.groq import Groq
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent import ReActAgent

async def main():
    client = BasicMCPClient("python", args=["mcp_server.py"])
    tool_spec = McpToolSpec(client=client)
    tools = await tool_spec.to_tool_list_async()

    llm = Groq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY")
    )
    Settings.llm = llm

    agent = ReActAgent(tools=tools, llm=llm, verbose=True)

    test_queries = [
        "I have a first-order reaction with k=0.5/min, feed rate 100 L/min. What CSTR volume do I need for 80% conversion?",
        "Is it safe to run at 150C and 10atm with stainless steel?",
    ]

    for q in test_queries:
        print(f"Q: {q}\n")
        response = await agent.run(q)
        print(f"A: {response}\n")
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(main())