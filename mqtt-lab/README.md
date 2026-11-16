# 本地 MQTT 诊断实验环境

这里提供现成的 Mosquitto 服务器及收发客户端，用于产生可复现的通信日志。你可以直接开始开发诊断助手，不需要实现 MQTT 协议或自行编写收发端。

实验目录：`E:\python workspace\mcp-start\mqtt-lab`。`lab.py` 使用 Python 标准库调用 Docker，不增加 Python 包依赖。服务器、`mosquitto_pub` 和 `mosquitto_sub` 均来自 Mosquitto 镜像，Windows 无需另行安装这些客户端。

## 启动与日常使用

先确保 Docker Desktop 已运行。在已激活 `mcp-start` 虚拟环境的 PowerShell 中执行：

```powershell
cd 'E:\python workspace\mcp-start'
python .\mqtt-lab\lab.py start
python .\mqtt-lab\lab.py status
```

服务器容器名为 `mcp-start-mqtt`，宿主机地址为 `127.0.0.1:1883`，仅供本机访问；容器不配置自动开机启动。实验账号为 `mqtt_lab`，密码为 `mqtt-lab-demo`。这组凭据公开用于本地练习，请勿复用于其他系统。

手动测试收发时，打开两个终端，均进入项目并使用其 Python 环境。先在终端一启动接收：

```powershell
python .\mqtt-lab\lab.py sub
```

再在终端二发送一条消息：

```powershell
python .\mqtt-lab\lab.py pub
```

默认主题为 `lab/demo`，默认发送内容为 `hello`。订阅端可用 Ctrl+C 结束。停止服务器：

```powershell
python .\mqtt-lab\lab.py stop
```

## 生成诊断案例

```powershell
python .\mqtt-lab\lab.py cases
```

案例包含正常通信 `normal`、错误端口 `wrong_port`、错误密码 `bad_password`、主题不匹配 `topic_mismatch`。输出位置为：

```text
mqtt-lab/artifacts/<runid>/
├── cases/
│   ├── case-01/
│   ├── case-02/
│   ├── case-03/
│   └── case-04/
├── answer_key.json
├── verification.json
└── verification/recovery/
```

后续诊断助手从 `cases` 下的证据开始分析，给出原因、引用证据和下一步检查建议。`answer_key.json` 保存真实故障条件，`verification.json` 保存实验检查结果；两者供你核对评估，不要提前提供给模型。

`artifacts/latest.txt` 记录最近一次全部检查通过的运行目录名。给模型时只选择该运行目录下的 `cases/`，其余文件与 `verification/` 都留作人工核对。每次生成新目录，不覆盖之前的日志。

使用 Docker 官方 Mosquitto 镜像，已固定下载摘要，当前为 2.1.2。配置、脚本和说明可以提交 Git；生成的密码哈希、日志和实验输出由本目录的 `.gitignore` 忽略。`cases` 的 PASS 表示真实故障按预期复现，不表示故障案例本身通信成功。

## 实验范围

案例中的收发客户端主要在容器内连接 `127.0.0.1`，此处指容器自身；Windows 的 `127.0.0.1:1883` 指宿主机映射端口，主机访问情况另做握手检查。这是同一台电脑上的真实软件进程实验，不能视为两台物理设备或单位内网环境的验证。

当前环境用于基本 MQTT 故障复现，暂未配置 TLS、持久化或抓包。先完成日志与配置诊断，再按需要扩展检查工具。

## 官方资料

- [Mosquitto 文档与现成服务器、客户端](https://mosquitto.org/documentation/)
- [Mosquitto 用户名密码认证](https://mosquitto.org/documentation/authentication-methods/)
