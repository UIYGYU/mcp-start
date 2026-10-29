"""MCP 学习项目的环境检查入口；具体 Server/Client 示例由后续练习添加。"""

import sys
from importlib.metadata import version


def main() -> None:
    print("MCP learning environment is ready.")
    print(f"Python: {sys.version.split()[0]}")
    print(f"MCP SDK: {version('mcp')}")


if __name__ == "__main__":
    main()
