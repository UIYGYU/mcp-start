# mcp-start

独立的 MCP 学习与实验项目，用于跟随微软 MCP for Beginners 编写 Python Server、Client 和工具示例。

## 环境

- Python：3.13.14（`.python-version` 固定解释器版本）
- Python 支持范围：`>=3.13,<3.14`
- 依赖管理：uv
- MCP SDK：`mcp[cli]>=1.28,<2`，初始化时锁定为 1.30.0
- 仓库：https://github.com/UIYGYU/mcp-start （私有）

教程的基础示例使用 `from mcp.server.fastmcp import FastMCP`，因此先使用仍维护的 SDK 1.x。SDK 2.x 已更改部分接口；以后有迁移需求时再调整版本并重新验证。

当前只初始化环境，不预先实现课程作业。运行 SDK、编写普通 MCP 工具不需要 LLM API Key；接入大模型时再按所选服务配置。

## 开始使用

在 PowerShell 中进入项目：

```powershell
cd "E:\python workspace\mcp-start"
uv sync --locked
uv run --locked python main.py
```

预期显示 Python 3.13.14 和 MCP SDK 1.30.0。

使用 `uv run` 时不必手动激活虚拟环境。需要在终端直接使用 `python` 时，可以先运行：

```powershell
.\.venv\Scripts\Activate.ps1
```

VS Code 打开本目录后，项目设置指向 `.venv/Scripts/python.exe`。若已缓存其他解释器，在命令面板运行 `Python: Select Interpreter` 选择本项目虚拟环境。

## 后续练习

按实际学习进度添加 Server 和 Client 文件。写好 Server 后可使用：

```powershell
uv run mcp dev server.py
```

上面的 `server.py` 是后续自行创建的示例文件，目前尚不存在。Inspector 需要 Node.js/npm，该命令可能下载 Inspector 组件。

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
- [MCP Python SDK 1.x 文档](https://github.com/modelcontextprotocol/python-sdk/tree/v1.x)
- [MCP SDK 2.x 迁移文档](https://py.sdk.modelcontextprotocol.io/migration/)
