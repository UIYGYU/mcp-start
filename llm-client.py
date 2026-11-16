import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from mcp import Client, StdioServerParameters
from openai import AsyncOpenAI
import httpx2
from mcp.client.streamable_http import streamable_http_client

async def run():
    # 1. 客户端通过 stdio 启动 Server
    server = StdioServerParameters(
        command=sys.executable,
        args=["test-mcpserver.py"],
    )
    #async with Client(server, mode="auto") as client:
    #async with Client("http://127.0.0.1:8000/mcp", mode="auto") as client:
    async with httpx2.AsyncClient(
        headers={"Authorization":"Bearer learn-mcp"},
        timeout=httpx2.Timeout(30.0, read=300.0)
    ) as http_client:
        transport = streamable_http_client(
            "http://127.0.0.1:8000/mcp",
            http_client=http_client
        )

        async with Client(transport, mode="auto") as client:
            print("MCP 协议：", client.protocol_version)

            # 2. 发现 MCP 工具，转换成模型能理解的格式
            tools = await client.list_tools()
            functions = []
            for tool in tools.tools:
                functions.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.input_schema,
                    },
                })

            # 3. 把问题和工具定义交给 CLIProxy 后面的模型
            async with AsyncOpenAI(
                base_url=os.environ["LLM_BASE_URL"],
                api_key=os.environ["LLM_API_KEY"],
            ) as llm:
                response = await llm.chat.completions.create(
                    model=os.environ["LLM_MODEL"],
                    messages=[{"role": "user", "content": "请调用工具计算 2 加 20。"}],
                    tools=functions,
                )

            # 4. 执行模型选择的工具，打印结果（与教程的 Python 示例一致）
            message = response.choices[0].message
            if message.tool_calls:
                for call in message.tool_calls:
                    name = call.function.name
                    arguments = json.loads(call.function.arguments)
                    print("调用工具：", name, arguments)
                    result = await client.call_tool(name, arguments=arguments)
                    print("工具结果：", result.content)
            else:
                print("模型回答：", message.content)


if __name__ == "__main__":
    load_dotenv()
    asyncio.run(run())
