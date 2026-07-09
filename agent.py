import os
import asyncio
import sys
from dotenv import load_dotenv
load_dotenv(dotenv_path="apis.env")

os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY")

from llama_index.core import Settings
from llama_index.llms.groq import Groq
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent import ReActAgent


class ChemAgent:
    """Wraps the MCP-connected ReActAgent. Initialize happens automatically on first ask()."""

    def __init__(self):
        self.agent = None
        self._initialized = False

    async def initialize(self):
        """Set up the MCP client, tools, and agent. Only needs to run once."""
        if self._initialized:
            return

        client = BasicMCPClient(sys.executable, args=["mcp_server.py"])
        tool_spec = McpToolSpec(client=client)
        tools = await tool_spec.to_tool_list_async()

        llm = Groq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY")
        )
        Settings.llm = llm

        self.agent = ReActAgent(tools=tools, llm=llm, verbose=True)
        self._initialized = True

    async def ask(self, query: str) -> str:
        """Ask a question. Initializes automatically on first call."""
        if not self._initialized:
            await self.initialize()

        guided_query = (
            "Answer the user's question. If the question asks about uploaded "
            "documents, manuals, PDFs, files, or document-specific facts, you "
            "must call the query_documents tool and base the answer only on "
            "the retrieved document content. If the documents do not contain "
            "the answer, say that clearly.\n\n"
            f"User question: {query}"
        )
        response = await self.agent.run(guided_query)
        return str(response)


async def main():
    agent = ChemAgent()
    
    test_queries = [
        "I have a first-order reaction with k=0.5/min, feed rate 100 L/min. What CSTR volume do I need for 80% conversion?",
        "According to the uploaded notes, what is a CSTR? Then calculate the required CSTR volume for a flow rate of 20 L/min, a rate constant of 0.5 min⁻¹, and a conversion of 80%",
    ]

    for q in test_queries:
        print(f"Q: {q}\n")
        response = await agent.ask(q)
        print(f"A: {response}\n")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())
