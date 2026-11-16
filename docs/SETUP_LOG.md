# 初始化操作记录

日期：2026-10-29（北京时间）。目标目录：`E:\python workspace\mcp-start`。

## 用户授权与范围

- 用户要求初始化指定目录、使用 Python 3.13、建立 Git 版本管理并上传 GitHub。
- 用户在询问后明确选择 GitHub **私有**仓库，仓库名使用 `mcp-start`。
- 用户要求持久化记录所用 MCP 工具及所有操作，本文件记录本次工具调用、操作命令、决策与验证结果。
- 本次不配置 LLM 提供方，不需要用户提供 API Key，不预写教程 Server/Client 作业。

## 工具清单

以下区分 Codex 执行工具与真正的 MCP 服务，避免把安装 MCP SDK 和调用 MCP 工具混为一谈。

| 工具标识 | 类别 | 用途 |
| --- | --- | --- |
| `functions.exec` | Codex 编排工具 | 串行或并行调用下列嵌套工具，收集结果 |
| `tools.exec_command` | 终端工具 | 执行 PowerShell、uv、Git、Python、GitHub REST API 请求，写入本项目文件 |
| `tools.write_stdin` | 终端会话工具 | 等待 uv 依赖安装进程完成并读取结果 |
| `tools.web__run` | 网页检索工具 | 核对 MCP SDK 官方仓库、PyPI 和微软教程源码 |
| `functions.request_user_input_async` | 用户输入工具 | 询问仓库可见性；用户选择私有 |

没有调用用户自行部署的 MCP Server。没有通过 MCP 执行云资源操作；GitHub 仓库创建使用 HTTPS REST API，认证来自 Git 自带的凭据管理器。

## 初始检查（已完成）

1. 列出目标目录文件，确认目录存在且为空，没有 `.git`。
2. 检查 `E:\AGENTS.md`、`E:\python workspace\AGENTS.md`、目标目录 `AGENTS.md`，没有发现适用文件。
3. 使用 `Get-Command` 检查命令：uv、Git 可用；`gh` 未安装，当前 shell 没有可直接发现的 `python` 命令。
4. 版本：uv 0.11.28，Git 2.53.0.windows.2。
5. 查看 Git 凭据助手，配置为 `manager`；读取现有 Git 提交身份，沿用已有配置，没有修改全局身份。
6. 在默认沙箱内运行 `uv python list --only-installed`，因 uv 用户缓存目录访问问题失败；随后在获准的沙箱外执行相同查询成功。
7. 读取一次 computer-use 技能说明，作为 gh 不可用时的备用方案评估；最终没有使用 UI 自动化，也没有启动浏览器登录。

关键检查命令：

```powershell
Get-ChildItem -LiteralPath 'E:\python workspace\mcp-start' -Force
Get-Command uv,git,gh,python -ErrorAction SilentlyContinue
uv --version
git --version
gh auth status
git config --get-all credential.helper
git config --global user.name
git config --global user.email
uv python list --only-installed
```

`gh auth status` 因未安装 gh 失败，这不影响后续通过现有 Git 凭据管理器完成操作。

## 项目初始化与文件写入（已完成）

目标目录位于当前聊天默认可写根目录之外，因此创建文件、虚拟环境与 Git 写操作通过带授权的终端调用执行，没有绕过目录权限。

```powershell
uv init --app --python 3.13 --no-workspace --vcs git "E:\python workspace\mcp-start"
git -C "E:\python workspace\mcp-start" branch -M main
uv python pin 3.13.14 --project "E:\python workspace\mcp-start"
uv add 'mcp[cli]>=1.28,<2' --python 3.13.14 --project "E:\python workspace\mcp-start"
```

- `uv init` 创建 `pyproject.toml`、`.python-version`、`.gitignore`、`README.md`、`main.py` 与 Git 仓库。
- 将初始分支统一为 `main`。
- 已安装解释器中存在 Python 3.13.14、3.14.6；选择 3.13.14，不使用 3.14。
- 将 `requires-python` 从 `>=3.13` 收紧到 `>=3.13,<3.14`。
- MCP 安装成功：1.30.0，独立 `.venv` 中安装 38 个依赖包；详细版本与来源在 `uv.lock`。
- 安装时出现跨磁盘无法硬链接的提示，uv 自动回退复制，安装成功，没有关闭任何依赖校验。
- `--no-workspace` 提示未发现父工作区，为非错误提示。

本次创建或修改的文件如下；普通文本使用 PowerShell `Set-Content -LiteralPath ... -Encoding utf8` 写入，`.python-version` 由 `uv python pin` 更新，`uv.lock` 由 uv 生成：

| 文件 | 用途 |
| --- | --- |
| `pyproject.toml` | 项目元数据、Python 范围、MCP 依赖 |
| `.python-version` | 固定 Python 3.13.14 |
| `uv.lock` | 锁定全部依赖版本与哈希（由 uv 生成） |
| `.gitignore` | 忽略虚拟环境、真实环境变量、日志、抓包、运行产物 |
| `.env.example` | 仅说明环境变量模板，不包含任何真实密钥 |
| `main.py` | 打印环境就绪状态、Python 与 MCP 版本 |
| `.vscode/settings.json` | 默认使用本项目的虚拟环境解释器 |
| `README.md` | 中文使用方法、版本管理说明与参考资料 |
| `docs/SETUP_LOG.md` | 本操作记录 |

没有给 `my-agent` 安装或升级依赖，没有复制其 `.env`，没有修改其他项目文件。

## 依赖选择的来源核对（已完成）

使用网页工具访问：

1. https://github.com/modelcontextprotocol/python-sdk
2. https://pypi.org/project/mcp/
3. https://github.com/modelcontextprotocol/python-sdk/tree/v1.x
4. https://raw.githubusercontent.com/microsoft/mcp-for-beginners/main/03-GettingStarted/01-first-server/solution/python/server.py
5. 同示例目录的 `requirements.txt` 链接未成功取得，未将其当作已核验依据。

SDK 当前主线已是 2.x，教程所查看的基础服务器代码仍使用 `mcp.server.fastmcp.FastMCP`。官方 1.x 分支仍维护，并明确建议以 `<2` 限制版本。因此使用 `mcp[cli]>=1.28,<2`，实际锁定 1.30.0。此举与用户要求 Python 3.13 是两个独立的兼容性选择。

## GitHub 认证与仓库创建（已完成）

- 未安装或下载 gh；使用 Git 的 `manager` 凭据助手。
- 设置进程级 `GCM_INTERACTIVE=never`，通过 `git credential fill` 按 `https://github.com` 查询现有凭据。
- 凭据只存在于执行进程内存中，未输出、未写文件、未提交到 Git。文档不记录其值。
- 调用 `GET https://api.github.com/user`，确认账号为 `UIYGYU`。
- 调用 `GET /repos/UIYGYU/mcp-start`，确认最初不存在仓库。
- 经用户选择私有后，调用 `POST https://api.github.com/user/repos`，请求字段为 `name=mcp-start`、`private=true`、`auto_init=false`，描述为 Python 3.13 MCP learning exercises。
- 创建响应确认 `private=true`、默认分支 `main`。
- 仓库地址：https://github.com/UIYGYU/mcp-start 。
- 创建逻辑先查询再创建，重试不会主动覆盖、删除或重新初始化已有仓库；如发现同名公开仓库会停止发布。

## 验证、提交和发布

下文将在实际检查和推送后补充结果。最后用于封存本操作记录自身的提交和推送，会在本文件末尾记录执行步骤；自身提交 SHA 不写入自身内容，避免循环修改。

## 初始化验证结果（已完成）

执行并通过：

```powershell
uv lock --check
uv sync --locked
uv run --locked python main.py
```

结果：Python 3.13.14，MCP SDK 1.30.0，锁文件一致，38 个已安装依赖检查通过。

通过标准输入运行一次临时 Python 检查脚本（没有保存为练习文件）：

- 导入 `mcp.server.fastmcp.FastMCP` 成功。
- 定义临时 `add(a: int, b: int)` 工具，`await server.list_tools()` 返回 `add`。
- `await server.call_tool('add', {'a': 2, 'b': 3})` 返回 5。
- 检查解释器为 Python 3.13，SDK 为 1.x。
- 这是 SDK 内部注册/调用冒烟检查，没有宣称已验证 stdio、HTTP、Inspector 或 LLM 的端到端通信。

通过 `git check-ignore -v` 检查 `.env`、`.env.local`、`.env.production`、`.venv/probe.txt`、`logs/probe.log`、`capture.pcap`、`capture.pcapng`、`artifacts/probe.txt` 均命中忽略规则；这些 probe 名称仅用作规则检查，没有创建真实文件。

通过 `git check-ignore --quiet --no-index .env.example` 确认示例环境文件可被追踪。通过显式文件列表的 `git add --dry-run` 确认可提交文件共 9 个，没有 `.venv`、真实 `.env` 或运行产物。

## 补充工具与审查记录

- 调用 `collaboration.spawn_agent` 创建一个只读审查子代理 `review_mcp_init`，核对配置、忽略规则、文档与命令，不授权修改或联网，也不读取凭据。它使用的终端检查属于上表的 `functions.exec` / `tools.exec_command`。
- 本次实际调用的 MCP 工具为 `mcp__codex_app__open_in_codex`（Codex app MCP）。参数仅为本记录文件路径，用于在当前聊天面板展示文档；返回 `status=queued`。这只表示已排队打开，没有宣称用户界面已立即显示。
- 未调用其他 MCP 服务，也没有安装、启用任何额外 Codex 插件。


## 只读审查结论（已完成）

审查没有发现环境版本、依赖范围或敏感文件忽略问题。修正一处文档表述：`uv.lock` 由 uv 生成，不能笼统说成所有文件都由 `Set-Content` 写入。

子代理的首次 Git 只读检查遇到沙箱账号与仓库拥有者不同的安全检查；随后使用命令级 `git -c safe.directory=... --no-optional-locks` 完成读取，没有修改全局 safe.directory、仓库文件或凭据，也没有联网。

## Git 提交与首次推送结果（已完成）

```powershell
git remote add origin https://github.com/UIYGYU/mcp-start.git
git add -- .gitignore .python-version .env.example .vscode/settings.json pyproject.toml uv.lock main.py README.md docs/SETUP_LOG.md
git diff --cached --check
git diff --cached --stat
git commit -m "chore: initialize Python 3.13 MCP learning project"
git push -u origin main
```

- 实际配置 origin 前先检查已有 remote，若发现不同地址则停止，不覆盖其他远端。
- 暂存检查通过，共 9 个文件。
- Git 对文本提示将来可能进行 LF/CRLF 转换，属于换行符提示，没有提交失败。
- 初始化提交成功：`7a25c7e231e9191e259eba3502f0973f9b55f528`。
- 第一次普通推送失败：`TLS connect error / unexpected eof while reading`，代码提交已保存在本地。
- 未关闭 SSL/TLS 验证，未修改 Git 全局网络配置，未重新初始化仓库。

随后执行：

```powershell
git -c http.version=HTTP/1.1 push -u origin main
git status --short
git ls-remote --heads origin main
```

推送成功，`main` 已跟踪 `origin/main`；远程 main 指向初始化提交，工作区在当时干净。

## 操作记录封存与交付

为让后续在本仓库运行普通 `git push` 时也使用已成功的 HTTP/1.1，将仅设置本仓库的 `http.version`，HTTPS 和证书校验继续生效。该本地 Git 配置不写入全局配置，也不会随代码上传。

本记录最后的更新通过独立文档提交封存，固定执行步骤如下：

```powershell
git config --local http.version HTTP/1.1
git add -- docs/SETUP_LOG.md
git diff --cached --check
git commit -m "docs: record setup verification and GitHub publishing"
git push
git status --short
git rev-parse HEAD
git ls-remote --heads origin main
```

交付前还会通过相同的内存凭据流程只读调用 GitHub REST API，核对仓库仍为 `private=true`、默认分支为 `main`，并将远程分支 SHA 与本地 HEAD 比较。文档自身的封存提交 SHA 可从 `git log` 查询，不硬编码到本记录中。

本记录包含全部工具种类及实际执行的初始化、检查、写文件、GitHub 创建、失败重试、提交推送、审查和文档展示操作。重复读取/权限重试已合并说明；没有记录密钥或将完整认证响应保存到文档。后续任务若继续改动，请按日期追加工具、命令和结果。

## 2026-10-31：首次 Server 启动排查与验证

用户要求检查 FastMCP 导入失败、版本选择和首个 Server 的启动。沿用现有工作区，保留用户已修改的依赖清单与锁文件，没有提交或推送。

### 工具与检查

- `functions.exec` / `tools.exec_command`：读取项目配置、Git 差异、虚拟环境元数据与 SDK 源码，运行 uv 同步和临时 Python 客户端。
- `mcp__codex_app__list_threads` / `mcp__codex_app__read_thread`：只读查阅用户提到的另一个项目中的相关学习讨论。
- `collaboration.spawn_agent` / `collaboration.send_message`：委托只读核查 SDK 与微软教程当前版本资料。
- `tools.web__run`：核对微软教程、SDK 官方文档、PyPI、维护政策及 uv 同步说明。
- `tools.apply_patch`：修正当前 Server 的 API 用法，更新 README 和本记录。

默认沙箱内项目 Python 启动失败，uv 也无法使用其用户缓存；通过授权的沙箱外终端调用完成后续验证，没有重建或删除虚拟环境。

### 根因与处理

`pyproject.toml` 要求 `mcp[cli]>=1.28,<2`，`uv.lock` 锁定 `mcp==1.30.0`、`fastmcp==3.4.11`；但 `.venv` 实际为 `mcp==2.3.0`、`fastmcp==4.1.4`，安装器元数据均为 uv。独立框架的 `fastmcp-slim==4.1.4` 所选 extras 要求 `mcp>=2.3.0,<3`。没有证据确认此前具体执行了什么命令，因此不将某条历史安装命令认定为原因。

直接运行 `test-mcpserver.py`，复现了 SDK 2.x 的旧导入路径错误。该版本将 FastMCP 改为 `mcp.server.mcpserver.MCPServer`；`<2` 约束本身没有写错，实际环境偏离了项目配置。

先执行 `uv sync --locked --dry-run` 预览，再执行 `uv sync --locked`：恢复 `mcp==1.30.0`、`fastmcp==3.4.11` 及对应 slim 包，清理不属于锁文件的新版依赖。没有改动 `pyproject.toml` 或 `uv.lock`。

恢复后发现用户 Server 的两处 API 不兼容，做最小修正：

1. 移除官方 FastMCP 1.x 不接受的 `version="1.0.0"` 构造参数。
2. 将类实例方法注册改为 `mcp.add_tool(weather_tools.forecast)`；`mcp.tool()` 是装饰器工厂。
3. 顺手移除未使用的 `asyncio` 导入。工具与资源的业务实现保持现有练习内容。

### 实际通信验证

通过 PowerShell here-string 将临时脚本传给 `uv run --locked python -X utf8 -`。使用 `ClientSession`、`StdioServerParameters` 和 `stdio_client` 启动现有 Server 子进程，设置总超时和请求超时，结束后退出上下文并关闭进程。

- 初始化成功，协商协议版本为 `2025-11-25`。
- `tools/list` 返回 `add`、`forecast`、`get_weather`。
- `add(2, 3)` 返回 `5`；天气与两天预报均返回预期演示数据。
- `resources/templates/list` 返回 `greeting://{name}`。
- `resources/read` 读取 `greeting://Codex`，返回 `Hello, Codex!`。

第一次临时验证脚本错误地假定所有工具均返回 `structuredContent`，在天气结果上失败；随后修正检查脚本，兼容文本内容中的 JSON，所有验证通过。没有因此改写用户工具的返回类型。未添加正式测试文件或课程 Client 文件；未运行 Inspector、HTTP 或 LLM 接入验证。

另外运行 `uv run --locked mcp dev --help` 与 `uv lock --check`，均通过；确认 node 与 npx 已安装。检查 CLI 源码后，在 README 的 Inspector 命令中加入 `--with "mcp[cli]>=1.28,<2"`，明确约束其生成的 `uv run --with mcp ...` 子命令所用 SDK 系列。`git diff --check` 通过。

### 版本选择参考

- [微软首个 Server 中文课程](https://github.com/microsoft/mcp-for-beginners/blob/main/translations/zh-CN/03-GettingStarted/01-first-server/README.md)：仍包含 FastMCP 1.x 示例，应配合版本约束使用。
- [官方 SDK 1.x 文档](https://py.sdk.modelcontextprotocol.io/v1/) 与 [1.30.0 包说明](https://pypi.org/project/mcp/1.30.0/)。
- [官方 SDK 2.x 迁移文档](https://py.sdk.modelcontextprotocol.io/migration/)：改名之外还有其他 API 变化。
- [官方维护政策](https://github.com/modelcontextprotocol/python-sdk/security/policy)：最新 2.x 获得功能、修复和安全维护；最新 1.x 获得关键错误与安全修复。
- [uv 锁定与同步](https://docs.astral.sh/uv/concepts/projects/sync/)：项目声明、锁文件和实际安装环境是三个需要保持一致的状态。

建议先完成现有 Server／Client 和三类基础能力的闭环，再用稳定的 SDK 2.x 实现同等功能，不要求整套教程都在 1.x 完成。

## 2026-10-31：按用户选择直接使用 SDK 2.x

用户进一步明确选择：阅读现有教程学习概念，直接安装和编写 SDK 2.x 代码。此决定取代上一节先以 v1 完成入门闭环的建议；历史排查记录保留。

使用 `tools.apply_patch` 将依赖调整为 `mcp[cli]>=2.3,<3`，移除当前代码不使用的独立 `fastmcp`。通过授权的 `tools.exec_command` 执行 `uv sync`，由 uv 更新锁文件并同步环境，最终为 `mcp==2.3.0`、`mcp-types==2.3.0`，同时清理独立 FastMCP 框架及其专属依赖。Python 仍为 3.13.14。

对现有 Server 做最小迁移：导入改为 `from mcp.server import MCPServer`，实例使用 `MCPServer`，恢复用户最初希望声明的 `version="1.0.0"`（v2 已支持）。保留三个工具、问候资源与 stdio 入口，没有新增课程功能。

继续使用 `functions.exec` 编排文件读取和终端操作，使用 `tools.web__run` 核查官方首页与迁移指南，使用 `collaboration.followup_task` 委托只读核查 v2 客户端 API。API 探测时尝试查询不存在的 `Client.stdio`，随后根据官方文档与本地源码改用 `Client(StdioServerParameters(...))`，没有据此修改 SDK。

执行 `uv run --locked python main.py`，显示 Python 3.13.14、MCP SDK 2.3.0。再次通过 here-string 运行临时 v2 `Client`，使用绝对路径启动现有 Server，配置 20 秒总超时、10 秒请求超时；真实 stdio 通信验证通过：

- 服务标识为 `Weather MCP Server`，版本 `1.0.0`。
- 自动协商协议版本为 `2026-07-28`。
- 发现 `add`、`get_weather`、`forecast`；三个调用均成功，`add(2, 3)` 返回 `5`。
- 发现 `greeting://{name}`；读取 `greeting://Codex` 返回 `Hello, Codex!`。
- 使用 v2 snake_case 字段检查结果，退出客户端上下文后正常关闭 Server。

README 更新为直接使用 SDK 2.x 的路线与命令。尚未运行 Inspector 界面、HTTP 或 LLM 接入；没有保存临时客户端作业，没有执行提交或推送。

## 2026-10-31：第 3.3 章 LLM 客户端与 CLIProxy 配置

用户明确授权编写 LLM 客户端并使用新协议，随后选择 CLIProxy，要求创建 `.env` 供自行填写。项目已有空文件为 `llm-client.py`，沿用该文件名完成实现。没有改动用户的 `test-mcpclient.py` 或 Server 练习。

使用 `functions.exec` / `tools.exec_command` 读取项目和 SDK 源码、安装依赖、执行检查；`tools.web__run` 核查微软 3.3、MCP v2 客户端/协议版本和官方 OpenAI 工具调用文档。应用 `openai-docs` 技能核对 API 格式。通过 `functions.request_user_input_async` 确认模型服务，使用 `tools.apply_patch` 实现脚本和文档。通过 `collaboration.spawn_agent` / `collaboration.followup_task` 委托课程只读核查及隔离测试文件编写。

- 执行 `uv add openai python-dotenv`，更新依赖清单和锁文件；实际安装 `openai==3.42.0`、`python-dotenv==1.2.4`。MCP 保持 `2.3.0`，Python 保持 `3.13.14`。
- `llm-client.py` 使用 `Client(StdioServerParameters(...), mode="auto")` 启动现有 Server，通过发现后检查实际协议版本为 `2026-07-28`。
- 使用完整 `tool.input_schema` 转换 LLM 工具定义。通过异步 Chat Completions 请求处理模型选择、多个工具调用、对应 `tool_call_id` 的结果回传和最终回答，最多 8 轮。
- 保留文本和结构化 MCP 结果；参数格式、未知工具、MCP 错误可以交回模型修正。脚本打印学习用调用过程，不输出 API Key。
- `.env.example` 增加空值的 `LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL`。仅在 `.env` 不存在时复制模板创建，避免覆盖用户配置；`git check-ignore -- .env` 确认已忽略。未读取或复制其他项目的密钥。
- README 补充配置、启动、代码阅读顺序和验证方式。MCP 与 LLM API 是两条独立通信链路。

已完成验证：

1. `python llm-client.py --check-mcp`：真实 stdio 连接协商为 `2026-07-28`，发现 `get_weather`、`add`、`forecast`。
2. `python llm-client.py --help`：命令行入口正常。
3. `python -m unittest discover -s tests -p test_llm_client.py -v`：8 项全部通过，使用真实 MCP Server 和实际 AsyncOpenAI SDK，由 `httpx2.MockTransport` 模拟模型 HTTP 响应；覆盖工具结果回传、多工具、直接回答、坏 JSON/参数修正、未知工具、轮次上限、完整 Schema 和缺配置处理。
4. `uv lock --check`、`git diff --check` 通过。

没有读取真实 `.env` 进行测试，没有向真实 CLIProxy 或上游模型发送请求。真实模型服务仍待用户填写配置后验证；未执行 Git 提交或推送。

### 按用户要求精简为教程示例

将 `llm-client.py` 缩为 59 行、单个 `run()`：stdio 新协议连接 → 发现工具 → 一次模型选工具 → MCP 执行并打印。移除额外循环、错误恢复、命令行参数、自检及上一版测试文件，简化 README；配置仍由现有 `.env` 提供。只读复核与一次临时验证通过：真实 MCP 协议为 `2026-07-28`，模拟模型选择 `add(2, 20)` 后实际返回 `22`。未读取真实 `.env`、未调用 CLIProxy。

## 2026-11-01：安装本地 MQTT 通信诊断实验环境

用户授权安装配置现成服务器与客户端，供后续自行开发诊断助手。目标位置为本项目 `mqtt-lab/`，没有实现诊断 Agent 或 MCP 诊断服务器。

### 使用的工具

- `functions.exec`：编排独立读取、终端操作和官方资料查询。
- `tools.exec_command`：检查文件、Docker、端口与 Git 状态；在临时目录准备文件；经沙箱授权复制到项目、启动容器、执行验证和追加文档。
- `tools.write_stdin`：获取镜像下载及案例执行的最终结果。
- `tools.apply_patch`：在临时目录创建、修正配置、脚本及文档。
- `tools.web__run`：查询 Mosquitto 官方镜像、配置、认证和客户端文档。
- `collaboration.spawn_agent` / `collaboration.followup_task`：委托独立代理检查实验设计、编写 README 草稿并只读审查脚本。

这些操作使用平台工具，未调用已连接的 MCP 服务；此次安装的是 MQTT 服务，MQTT 与 MCP 是两个不同协议。

### 检查与安装操作

1. 读取本项目 README、pyproject.toml、忽略规则、历史记录和 Git 状态；检查上级及项目 AGENTS.md。保留项目当前 MCP 2.x 与 Python 3.13 环境、用户的现有修改。
2. 检查 Docker CLI 路径、运行状态、Compose 版本、镜像及容器列表，并检查 1883/1884 监听情况。Docker 不在当前终端 PATH，但已安装并运行；现有 Neo4j 保持原样。
3. 初次沙箱内执行 docker.exe 被拒绝，按要求经 `require_escalated` 重试成功。Docker Engine 29.9.1，Compose v5.6.0。
4. 执行 `docker pull eclipse-mosquitto:2`，首次现有镜像加速地址出现 EOF，重试成功；没有修改 Docker 全局网络设置。
5. 通过 `docker image inspect` 和临时容器 `mosquitto -h` 核实官方镜像实际为 Mosquitto 2.1.2。配置固定镜像摘要 `sha256:860aeb5d63ce509508f6dcfb2bc8a1c1dd2bc60555b562b45ce90e52d8dabb0f`。
6. 在系统临时目录 `codex-mqtt-lab-20261101` 准备文件，再通过授权命令复制到新建的 `mqtt-lab/`。没有覆盖已存在的学习源码。
7. 新增 `compose.yaml`、`config/mosquitto.conf`、`lab.py`、`.gitignore` 和 `README.md`。`lab.py` 只使用 Python 标准库，不修改 pyproject.toml 或 uv.lock。
8. 用短暂、无网络的官方镜像容器运行 `mosquitto_passwd`，生成公开演示账号的密码哈希到 `config/passwords`；该文件由 Git 忽略。凭据只用于本机练习，具体值见实验 README。
9. 执行 Python AST 语法检查、`docker compose config --quiet`，再执行 `python mqtt-lab/lab.py start`。启动独立 Compose 项目 `mcp-start-mqtt-lab`，服务器容器 `mcp-start-mqtt`；端口仅绑定 `127.0.0.1:1883`，restart 为 `no`，日志设有轮转。

### 真实运行验证与修正

执行 `python mqtt-lab/lab.py cases`，以官方 `mosquitto_pub` / `mosquitto_sub` 产生真实 MQTT v5 流量；客户端为容器内进程。订阅案例观察实际 SUBACK 日志后才发送，使用唯一主题、消息标记与有界等待。Windows 主机映射端口另通过 MQTT CONNECT/CONNACK 认证握手核对。

第一次案例运行中，正常收发、错误密码、主题不匹配及恢复对照通过；错误端口返回 `Error: Bad file descriptor`，未匹配初版脚本预期的 `refused` 字样。实际 `/proc/net/tcp` 和 tcp6 表确认容器内 1884 无监听、1883 有监听。修正检查为结合实际监听表、客户端错误与退出状态，避免仅依赖错误文本；增加容器内 `timeout`，并修正只向诊断模型提供 `cases/` 的提示。

重新执行全部案例：

- `case-01` 正常 QoS1 发布接收：PASS。
- `case-02` 客户端目标端口 1884、服务器监听 1883：PASS。
- `case-03` 错误密码被拒绝：PASS。
- `case-04` 发布主题与已确认订阅过滤器不同、订阅超时：PASS。
- 修正后的正常收发恢复对照：PASS。
- Windows 主机 `127.0.0.1:1883` 认证握手：PASS。

全部通过的证据目录：`mqtt-lab/artifacts/20261101-233654-3ed8b2/cases/`。同级 `answer_key.json`、`verification.json` 与 `verification/` 为独立核对材料，不提供给诊断 Agent。`artifacts/latest.txt` 记录最近一次全部检查通过的运行目录；初次失败运行保留为排查记录。

继续实际执行 `stop` → `start` → `status`，均通过；手动 `pub` 命令连接、发布及收到 PUBACK 正常（无匹配订阅时原因码为 16，不等于该消息已交付订阅端）。`mosquitto --test-config` 通过；Docker inspect 核对仅本机端口与无自动重启设置。服务器最终保持运行。现有 Neo4j 容器未修改。

配置与说明可纳入版本控制；生成的密码哈希、案例日志与运行输出由实验目录 `.gitignore` 忽略。本次没有执行 Git add、commit 或 push。

### 官方参考

- https://github.com/eclipse-mosquitto/mosquitto/blob/master/docker/generic/README.md
- https://mosquitto.org/documentation/authentication-methods/
- https://mosquitto.org/man/mosquitto_sub-1.html
- https://mosquitto.org/man/mosquitto_pub-1.html
- https://mosquitto.org/man/mosquitto-conf-5.html
### 最终进程回收与忽略规则检查

发现容器主进程直接为 Mosquitto 时，客户端 timeout 包装器可能留下已退出的子进程记录。为此在本实验 Compose 服务增加 `init: true`，交由 Docker 标准 init 回收子进程。重新启动并重跑四案例、恢复对照及主机握手，全部通过。最终通过的运行目录为 `mqtt-lab/artifacts/20261101-234127-6e54b4/`，`artifacts/latest.txt` 已更新。

`git check-ignore` 确认 `config/passwords`、`artifacts/latest.txt`、案例答案与产物被忽略。最终 Git 检查只出现预期的实验新增目录和 README/操作记录变更，保留原本已有的未提交修改；修正本次文档追加产生的末尾多余空行。
