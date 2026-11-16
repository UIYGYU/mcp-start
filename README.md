# mcp-start

独立的 MCP 学习与实验项目，用于跟随微软 MCP for Beginners 编写 Python Server、Client 和工具示例。

## 环境

- Python：3.13.14（`.python-version` 固定解释器版本）
- Python 支持范围：`>=3.13,<3.14`
- 依赖管理：uv
- MCP SDK：官方 Python SDK 2.x，依赖范围 `mcp[cli]>=2.3,<3`，当前锁定为 2.3.0
- 仓库：https://github.com/UIYGYU/mcp-start （私有）

跟随微软教程学习概念与安排练习，直接使用官方 SDK 2.x 编写代码。教程中的 `from mcp.server.fastmcp import FastMCP` 对应 v1；本项目使用 `from mcp.server import MCPServer`。安装命令与具体 API 以 v2 官方文档为准。

`main.py` 用于检查环境；`test-mcpserver.py` 是当前的第一个 stdio Server 练习，提供 `get_weather`、`add`、`forecast` 三个工具和 `greeting://{name}` 资源模板。天气与预报是静态演示数据。运行这些工具不需要 LLM API Key；接入大模型时再按所选服务配置。

## 开始使用

在 PowerShell 中进入项目：

```powershell
cd "E:\python workspace\mcp-start"
uv sync --locked
uv run --locked python main.py
```

预期显示 Python 3.13.14 和 MCP SDK 2.3.0。

使用 `uv run` 时不必手动激活虚拟环境。需要在终端直接使用 `python` 时，可以先运行：

```powershell
.\.venv\Scripts\Activate.ps1
```

VS Code 打开本目录后，项目设置指向 `.venv/Scripts/python.exe`。若已缓存其他解释器，在命令面板运行 `Python: Select Interpreter` 选择本项目虚拟环境。

## 当前 Server 练习

直接启动现有的 stdio Server：

```powershell
uv run --locked python test-mcpserver.py
```

stdio Server 通过标准输入／输出与客户端通信，不会打开网页或监听 HTTP 端口。单独启动时等待协议输入属于正常行为，可以按 Ctrl+C 结束；通常由 MCP 客户端启动该进程。

使用图形界面的 MCP Inspector 发现、调用工具和读取资源：

```powershell
uv run --locked mcp dev test-mcpserver.py
```

Inspector 需要 Node.js/npm，首次运行可能下载 Inspector 组件。SDK 2.x 的 CLI 会将生成的子命令约束到当前 SDK 版本。2026-10-31 已通过临时 v2 `Client` 验证真实 stdio 通信：协商协议版本 `2026-07-28`，三个工具的发现与调用、资源模板发现和问候资源读取均通过；没有将临时验证脚本保存为课程 Client 作业，也未验证 Inspector 界面。

依赖异常时先运行 `uv sync --locked`，让 `.venv` 与项目锁文件一致。`mcp[cli]` 中的 `cli` 是命令行功能的可选依赖，不代表独立的 `fastmcp` 框架。本项目使用官方 SDK 的 `MCPServer`，不依赖独立 `fastmcp`。

学习顺序：直接用 v2 完成 Server／Client、Tools、Resources、Prompts 的练习，再学习 Streamable HTTP 等内容。旧教程可以帮助理解概念与练习目标，遇到接口差异时查阅 v2 官方文档与迁移说明，不必先实现一遍 v1。

沿 v1 教程编写 v2 代码时，先留意这些差异：

- 服务端入口是 `MCPServer`，基础的 `@mcp.tool()`、`@mcp.resource()`、`@mcp.prompt()` 仍可使用。
- v2 提供 `Client`，使用 `async with Client(StdioServerParameters(...))` 自动连接与协商；不要在这个高层接口上再照搬显式 `initialize()`。
- Python 结果字段采用 snake_case，例如 `is_error`、`structured_content`、`resource_templates`、`uri_template`。
- SDK 的 `2.x` 是 Python 包版本；`2026-07-28` 是协议版本，两者分别管理。

## 第 3.3 章：带 LLM 的客户端

`llm-client.py` 按教程的 Python 示例写成一条简单流程：连接 Server → 发现工具 → 模型选择工具 → 执行工具并打印结果。MCP 使用 v2 `Client` 自动发现新版协议；LLM 使用 CLIProxy 的 OpenAI 兼容接口。

在 `.env` 填写：

```dotenv
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=
```

- 地址通常以 `/v1` 结尾；Key 和模型名填写 CLIProxy 提供的值。
- 模型需要支持工具调用。真实 `.env` 已被 Git 忽略。

在项目目录、已激活 `(mcp-start)` 的终端运行：

```powershell
python .\llm-client.py
```

脚本内 `messages` 中的 `content` 就是问题，直接改那一行即可。客户端会自己启动 Server；阅读代码中的 1～4 步注释就能跟上流程。

参考：[微软第 3.3 章](https://github.com/microsoft/mcp-for-beginners/blob/main/translations/zh-CN/03-GettingStarted/03-llm-client/README.md)、[MCP v2 客户端](https://py.sdk.modelcontextprotocol.io/client/)。

## 版本管理

提交 `pyproject.toml`、`uv.lock`、`.python-version`、源码和学习文档。修改已有文件也需要 `git add` 才会纳入下一次提交。

```powershell
git status
git add main.py
git commit -m "study: add MCP exercise"
git push
```

GitHub Desktop 可通过 `File -> Add local repository` 添加本目录。

`.venv/`、`.env`、`.env.*`、日志、抓包和 `artifacts/` 运行产物已忽略；`.env.example` 可提交，但只保留变量名与空值。

`.gitignore` 只影响未被追踪的文件。已经提交过的敏感文件不能仅靠添加忽略规则移除。JSON、DOCX 没有整类屏蔽，以免误忽略后续工具配置；具体本地文件按需要添加规则。

## 操作记录

本次初始化的工具清单、配置决策、命令、失败及处理过程见 [初始化操作记录](docs/SETUP_LOG.md)。后续每次实际操作，可继续在该文档中追加日期、工具、操作和结果，避免记录任何密钥。

## 参考资料

- [微软 MCP for Beginners 简体中文](https://github.com/microsoft/mcp-for-beginners/blob/main/translations/zh-CN/README.md)
- [MCP Python SDK 2.x 官方文档](https://py.sdk.modelcontextprotocol.io/)
- [MCP Python SDK 2.x 中文文档](https://py.sdk.modelcontextprotocol.io/zh/)（必要时对照英文原文）
- [MCP SDK 2.x 迁移文档](https://py.sdk.modelcontextprotocol.io/migration/)

## 本地 MQTT 诊断实验环境

现成的 Mosquitto 服务器、收发客户端和故障案例生成入口已安装到 `mqtt-lab/`。使用现有 Python 环境运行 `python .\mqtt-lab\lab.py start` 启动，运行 `python .\mqtt-lab\lab.py cases` 生成正常和故障证据；使用说明见 [MQTT 实验环境](mqtt-lab/README.md)，操作记录见 [SETUP_LOG](docs/SETUP_LOG.md)。
