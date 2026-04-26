# 星奈 AI 虚拟主播系统

一个基于本地大语言模型的全自动 B 站 AI 虚拟主播，能够实时响应弹幕、记忆观众、点歌播放，并通过 Live2D 模型呈现完整的虚拟主播形象。

---

## 目录

- [项目简介](#项目简介)
- [系统架构](#系统架构)
- [功能特性](#功能特性)
- [环境要求](#环境要求)
- [安装步骤](#安装步骤)
- [配置说明](#配置说明)
- [启动流程](#启动流程)
- [项目结构](#项目结构)
- [核心模块说明](#核心模块说明)
- [常见问题](#常见问题)

---

## 项目简介

星奈是一个完全运行在本地的 AI 虚拟主播系统。观众在 B 站直播间发送弹幕，系统自动识别内容、生成回复、合成语音，并通过 Live2D 模型呈现口型同步的虚拟形象。

整个系统分为五层：**输入层 → 过滤层 → 生成层 → 音频层 → 输出层**，每层独立运行，通过异步队列连接，互不阻塞。

---

## 系统架构

```
B站直播间（弹幕/礼物）
        ↓
┌─────────────────────────────┐
│        弹幕预处理层          │
│  垃圾过滤 · 安全过滤 · 语义去重队列  │
└──────┬──────────────┬───────┘
       │              │
  普通弹幕          点歌弹幕《xxx》
       ↓              ↓
  弹幕队列        Spotify API
  （语义合并）    搜索/播放/音量控制
       ↓              ↓
┌─────────────┐   歌单显示页面
│   大模型层   │   (localhost:8889)
│  qwen3:4b   │◄── persona.yaml
│  Ollama本地 │◄── SQLite 用户记忆
│  think:True │◄── Qdrant 语义记忆
└──────┬──────┘
       ↓
┌─────────────────────┐
│     语音合成层       │
│  edge-tts · XiaoyiNeural  │
│  TTS播放队列（流水线）     │
└──────┬──────────────┘
       ↓
  VB-Cable 虚拟声卡
  ├── nizima LIVE（口型同步）
  └── 扬声器（主播听到）
       ↓
  B站直播姬 → B站直播间
```

---

## 功能特性

### 弹幕处理
- 垃圾弹幕自动过滤（纯符号、重复字符、广告关键词、同用户复读）
- 语义去重队列：意思相近的弹幕自动合并，避免重复回答
- 弹幕按序处理，大模型空闲时立即取下一条
- 点歌弹幕（`《歌名》` 格式）走独立通道，不占用大模型资源

### AI 回复
- 基于 qwen3 本地模型，完全离线运行
- 开启 thinking 模式，回复质量更高
- 流式输出，按逗号/句号分段播放，第一句话更快出现
- 人设通过 `persona.yaml` 配置，无需修改代码

### 语音合成
- edge-tts 在线合成，支持语速调节（当前 +30%）
- TTS 播放队列独立运行，不阻塞大模型处理下一条弹幕
- 流水线模式：播放句子1的同时生成句子2的音频，减少停顿

### 点歌系统
- 识别 `《歌名》`、`「歌名」`、`【歌名】`、`点歌 歌名` 等格式
- Spotify API 搜索，支持模糊匹配
- 歌单队列管理，按序播放
- 实时歌单页面（`http://localhost:8889/status`），可嵌入直播画面
- 回复 AI 时自动降低歌曲音量

### 记忆系统
- **SQLite**：存储用户档案、稳定事实（偏好、身份信息、重要事件）
- **Qdrant**：向量语义搜索，找出历史上相关的记忆片段
- 记忆写入策略：只写入有价值的信息，过滤水弹幕

### Live2D 形象
- nizima LIVE 加载 Live2D 模型
- VB-Cable 虚拟声卡驱动口型同步
- 支持通过 API 触发表情动作（需模型支持）

---

## 环境要求

### 硬件
- GPU：NVIDIA RTX 4060 8GB 或以上
- 内存：16GB 以上（推荐 32GB）
- 存储：100GB 以上可用空间

### 软件
- Windows 11
- Python 3.11（Anaconda 管理）
- [Ollama](https://ollama.com/)（本地模型运行）
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)（运行 Qdrant）
- [nizima LIVE](https://nizimalive.com/)（Live2D 渲染）
- [VB-Cable](https://vb-audio.com/Cable/)（虚拟声卡）
- B站直播姬（推流）
- [Spotify](https://www.spotify.com/)（点歌功能，需会员）

---

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/yourname/ai-vtuber.git
cd ai-vtuber
```

### 2. 创建 Python 环境

```bash
conda create -n aivtuber python=3.11 -y
conda activate aivtuber
pip install -r requirements.txt
```

### 3. 安装并启动 Ollama

从 [ollama.com](https://ollama.com/download/windows) 下载安装，然后拉取模型：

```bash
ollama pull qwen3:4b
# 或使用 8b 版本（效果更好但更慢）
ollama pull qwen3:8b
```

### 4. 启动 Qdrant

```bash
docker run -d -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant
# 设置开机自启
docker update --restart always qdrant
```

验证：访问 `http://localhost:6333/dashboard`

### 5. 配置 VB-Cable

1. 安装 VB-Cable 驱动
2. 控制面板 → 声音 → 录制 → CABLE Output → 侦听 → 勾选侦听此设备 → 选择你的扬声器
3. 音量合成器 → Python → 输出设备改为 CABLE Input

### 6. 配置 nizima LIVE

1. 打开 nizima LIVE，加载 Live2D 模型
2. 其他设置 → 口型同步 → 开启
3. 输入设备选择 CABLE Output

### 7. 配置 Spotify（可选）

1. 注册 [Spotify 开发者账号](https://developer.spotify.com/dashboard)
2. 创建 App，Redirect URI 填 `http://127.0.0.1:8888/callback`
3. 将 Client ID 和 Client Secret 填入 `music/spotify_client.py`
4. 获取设备 ID：

```bash
python tools/spotify_auth.py
```

---

## 配置说明

### `config.yaml`

```yaml
ollama:
  base_url: "http://localhost:11434"
  model: "qwen3:4b"        # 或 qwen3:8b
  temperature: 0.6         # 越低越稳定
  max_tokens: 120          # 单次最大输出 token 数
  num_ctx: 8192            # 上下文窗口大小

qdrant:
  host: "localhost"
  port: 6333
  collection: "vtuber_memory"

sqlite:
  path: "memory/vtuber.db"

tts:
  engine: "edge_tts"

persona:
  path: "persona/persona.yaml"
```

### `persona/persona.yaml`

定义 AI 主播的性格、说话方式、禁忌话题等。修改此文件无需重启，下次回复时自动生效。

```yaml
name: 星奈

identity:
  role: AI直播助手
  age_style: 温柔亲切的少女感
  background: 一个真心想帮助每一位观众的AI助手...

personality:
  core_traits:
    - 温柔耐心，认真对待每一个问题
    - ...
  forbidden_traits:
    - 政治相关话题
    - ...

speech_style:
  tone: 温柔亲切，自然轻松
  max_length: 通常2-3句话

core_philosophy: "认真对待每一个人，用心回答每一个问题"
```

### `live/bilibili_listener.py`

填入直播间号和 SESSDATA：

```python
ROOM_ID = 你的直播间号
SESSDATA = "你的SESSDATA"  # 从浏览器 Cookie 获取
```

获取 SESSDATA：浏览器打开 bilibili.com → F12 → 应用程序 → Cookie → SESSDATA

---

## 启动流程

每次开播按以下顺序启动：

```
1. 打开 Docker Desktop，等待鲸鱼图标变绿
2. 打开 Ollama（系统托盘确认运行中）
3. 打开 nizima LIVE，加载模型，确认口型同步已开启
4. 打开 B站直播姬，开始推流
5. 打开 Anaconda Prompt：
   conda activate aivtuber
   d:
   cd ai_vtuber
   python app.py
6. 看到"记忆系统就绪"和"开始监听B站弹幕"后正式开播
```

停止直播：在 Anaconda Prompt 中按 `Ctrl+C`，系统会自动清空队列并安全退出。

---

## 项目结构

```
ai_vtuber/
├── app.py                    # 主程序入口
├── config.yaml               # 全局配置
├── persona/
│   ├── persona.yaml          # AI 人设配置
│   └── safety.yaml           # 安全规则
├── memory/
│   ├── sqlite_store.py       # SQLite 用户记忆
│   ├── qdrant_store.py       # Qdrant 向量记忆
│   ├── memory_writer.py      # 记忆写入策略
│   └── memory_retriever.py   # 记忆检索
├── llm/
│   └── ollama_client.py      # 大模型调用（流式）
├── tts/
│   └── tts_router.py         # 语音合成 + 播放队列
├── live/
│   └── bilibili_listener.py  # B站弹幕监听（自动重连）
├── logic/
│   ├── danmu_filter.py       # 弹幕垃圾过滤
│   ├── danmu_queue.py        # 语义去重队列
│   ├── reply_policy.py       # 情绪推断
│   └── safety_filter.py      # 输出安全过滤
├── vtuber/
│   └── vts_client.py         # VTube Studio / nizima API
├── music/
│   ├── spotify_client.py     # Spotify 搜索播放
│   ├── song_queue.py         # 歌单队列管理
│   ├── song_server.py        # 歌单状态 HTTP 服务
│   └── songlist.html         # 歌单显示页面
└── tools/
    ├── spotify_auth.py       # Spotify 授权工具
    ├── list_voices.py        # TTS 音色列表
    ├── test_audio.py         # 音频测试
    └── reset_memory.py       # 重置记忆库
```

---

## 核心模块说明

### 弹幕处理流程

```
弹幕进入
  → danmu_filter.py 垃圾过滤（太短/纯符号/重复字符/同用户复读/广告词）
  → 点歌检测（《》格式）→ handle_song_request() 独立处理
  → safety_filter.py 安全过滤
  → danmu_queue.py 语义去重（BGE-M3 向量，相似度 > 0.85 合并）
  → process_next() 取队列第一条送给大模型
```

### 大模型调用

`ollama_client.py` 使用流式输出，按标点符号（逗号、句号等）分段 yield，每段立即送入 TTS 队列播放，不等整段回复生成完。

开启 `think:True` 让模型先思考再回答，thinking 内容被过滤不播出，只输出正式回复。

### TTS 播放队列

TTS 队列与大模型完全解耦：
- 大模型生成完成 → 立即处理队列下一条弹幕
- TTS 队列独立运行 → 按顺序播放，不重叠
- 流水线优化：播放第 N 句时，同步生成第 N+1 句的音频

### 点歌系统

点歌弹幕不进入普通弹幕队列，走独立异步协程：
1. 识别 `《》` 格式提取歌名
2. Spotify API 搜索（支持模糊匹配）
3. 找到 → 加入歌单队列 → 歌单页面更新
4. 未找到 → TTS 播报提示
5. 当前歌曲播完 → 自动播下一首

---

## 常见问题

**Q: 启动后弹幕没有回复**

检查：
- Ollama 是否在运行（`ollama serve`）
- Docker Desktop 是否启动，Qdrant 容器是否运行
- `bilibili_listener.py` 中的 SESSDATA 是否过期

**Q: 有回复但听不到声音**

检查：
- 音量合成器中 Python 的输出设备是否为 CABLE Input
- CABLE Output 的侦听是否开启并转发到扬声器

**Q: 口型不动**

检查：
- nizima LIVE 中口型同步是否开启
- 输入设备是否选择了 CABLE Output
- VoiceVolume 滑块在说话时是否有跳动

**Q: 第一条弹幕响应很慢**

正常现象，首次启动需要加载 BGE-M3 嵌入模型。之后已预热，响应正常。

**Q: 如何重置记忆库**

```bash
python tools/reset_memory.py
```

**Q: 如何修改 AI 性格**

编辑 `persona/persona.yaml`，修改 `core_traits`、`speech_style` 等字段，保存后下次回复自动生效，无需重启。

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 大语言模型 | qwen3:4b / qwen3:8b via Ollama |
| 嵌入模型 | BAAI/bge-m3 via sentence-transformers |
| 向量数据库 | Qdrant (Docker) |
| 结构化存储 | SQLite |
| 语音合成 | edge-tts (Microsoft) |
| 音频路由 | VB-Cable 虚拟声卡 |
| Live2D 渲染 | nizima LIVE |
| B站接入 | blivedm 1.1.5 |
| 音乐播放 | Spotify Web API via spotipy |
| 主程序 | Python 3.11 + asyncio |

---

## License

MIT
