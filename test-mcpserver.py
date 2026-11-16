#!/usr/bin/env python3
import uvicorn
from mcp.server import MCPServer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import asyncio
import json
import redis.asyncio as redis
from dotenv import load_dotenv
import os
from tavily import AsyncTavilyClient
import httpx
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from tavily.errors import TimeoutError as TavilyTimeoutError

mcp = MCPServer(
    name="Weather MCP Server",
    version="1.0.0",
)

@mcp.tool()
async def progress_demo(ctx: Context) -> str:
    """模拟三个耗时步骤，并报告进度。"""
    steps = ["读取数据", "处理数据", "整理结果"]

    for index, step in enumerate(steps, start=1):
        await asyncio.sleep(1)

        await ctx.report_progress(
            index,
            total=len(steps),
            message=f"完成{step}"
        )
    return "全部处理完成"

@mcp.tool()
async def get_weather(location: str) -> dict:
    # """Gets current weather for a location."""
    # return {
    #     "temperature": 72.5,
    #     "conditions": "Sunny",
    #     "location": location
    # }
    async with redis.Redis(
        host="127.0.0.1", port=6379, decode_responses=True
    ) as cache:
        key = f"mcp:weather:{location}"
        cached = await cache.get(key)

        if cached is not None:
            result = json.loads(cached)
            result["source"] = "redis"
            return result

        # 模拟一次需要两秒的天气查询
        await asyncio.sleep(2)

        result = {
            "location": location,
            "temperature": 72.5,
            "conditions": "Sunny",
            "source": "query",
        }

        await cache.set(key, json.dumps(result), ex=30)
        return result


@mcp.tool()
def add(a:int, b:int)->int:
    """Add two numbers"""
    return a+b

@mcp.tool()
def calculate_product(a: int, b: int) -> int:
    """Calculate the product of two numbers"""
    return a * b

@mcp.tool()
def get_server_info() -> dict:
    """Get information about this MCP server"""
    return {
        "server_name": "example-stdio-server",
        "version": "1.0.0",
        "transport": "stdio",
        "capabilities": ["tools"]
    }

@mcp.tool()
async def web_server(query:str)->dict:
    """搜索互联网，返回最多三条结果的标题、链接和摘要，搜索词不能为空。"""

    query = query.strip()
    if not query:
        raise ToolError("搜索词不能为空，请提供要搜索的内容。")

    try:

        async with httpx.AsyncClient(trust_env=False) as http_client:
            async with AsyncTavilyClient(
                api_key=os.getenv("TAVILY_API_KEY"),
                client=http_client
            ) as search_client:
                response = await search_client.search(
                    query=query,
                    search_depth="basic",
                    max_results=3,
                    include_answer=False,
                )
    except TavilyTimeoutError as exc:
        raise ToolError("搜索请求超时，请稍后再试。") from exc
    except httpx.RequestError as exc:
        raise ToolError("搜索服务连接失败，请检查网络。") from exc

    results=[]
    for item in response["results"]:
        results.append({
            "title": item["title"],
            "url": item["url"],
            "content": item["content"],
        })

    return {"results": results}


@mcp.resource("greeting://{name}")
def get_greeting(name:str)->str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# 使用类的替代方法
class WeatherTools:
    def forecast(self, location: str, days: int = 1) -> dict:
        """查询指定地点的天气预报，天数必须在 1～7 之间。"""

        if not  1 <= days <=7:
            raise ToolError("days 必须在 1～7 之间。")
        return {
            "location": location,
            "forecast": [
                {
                    "day": i+1,
                    "temperature": 70 + i,
                    "conditions": "Partly Cloudy"
                }
                for i in range(days)
            ]
        }

# 注册类工具
weather_tools = WeatherTools()
mcp.add_tool(weather_tools.forecast)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        token = request.headers.get("Authorization")
        if token != "Bearer learn-mcp":
            return Response(
                "Unauthorized",
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"}
            )
        return await call_next(request)

if __name__ == "__main__":
    #mcp.run(transport="stdio")
    #mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
    load_dotenv()
    app = mcp.streamable_http_app()
    app.add_middleware(AuthMiddleware)
    uvicorn.run(app, host="127.0.0.1", port=8000)
