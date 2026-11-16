import asyncio
import httpx2

from mcp import Client
from mcp.client.streamable_http import streamable_http_client

async def show_progress(progress, total, message):
    """每收到一条进度通知，SDK 就调用这个函数。"""
    print(f"进度 {progress}/{total}：{message}")

async def run():
    async with httpx2.AsyncClient(
        headers={"Authorization":"Bearer learn-mcp"},
        trust_env=False,
    ) as http_client:
        transport = streamable_http_client(
            "http://127.0.0.1:8000/mcp",
            http_client=http_client
        )

        async with Client(transport, mode="auto") as client:
            print("MCP 协议：", client.protocol_version)

            result = await client.call_tool(
                "progress_demo",
                arguments={},
                progress_callback=show_progress
            )

            print("工具结果：", result.content[0].text)

if __name__ == "__main__":
    asyncio.run(run())