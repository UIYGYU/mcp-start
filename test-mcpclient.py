from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 为 stdio 连接创建服务器参数
server_params = StdioServerParameters(
    command="mcp",  # 可执行文件
    args=["run", "test-mcpserver.py"],# 可选的命令行参数
    env=None# 可选的环境变量
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write
        ) as session:
            # 初始化连接
            await session.initialize()

            # 列出可用资源
            templates = await session.list_resource_templates()
            for template in templates.resource_templates:
                print("Resource template:", template.uri_template)

            # 列出可用工具
            tools = await session.list_tools()
            print("LISTING TOOLS")
            for tool in tools.tools:
                print("Tool: ", tool.name)

            # 读取一个资源
            print("READING RESOURCE")
            result = await session.read_resource("greeting://hello")
            for content in result.contents:
                print(content.text)
                print(content.mime_type)

            # 调用一个工具
            print("CALL TOOL")
            result = await session.call_tool("add", arguments={"a": 1, "b": 7})
            print(result.content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
