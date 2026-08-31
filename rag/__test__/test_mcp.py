# Testing the sucessful working of the mcp server using static query
import asyncio
from fastmcp import Client
from setup_server import mcp


async def test_server():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "generate_insight",
            {
                "query": "Why are students struggling with Quiz Question 3 on Overfitting?",
                "top_k": 4,
            },
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(test_server())