# 🎬 Narrator AI CLI — 用自然语言，让 AI 帮你做电影解说视频

[English](README.md)

> 一行命令安装，一句话生成视频。93 部内置电影素材、146 首 BGM、63 个配音角色、90+ 解说风格模板，开箱即用。

## 这是什么？

Narrator AI CLI 是 [AI 解说大师](https://ai.jieshuo.cn/) 的命令行工具。安装到 AI Agent（小龙虾 OpenClaw、Windsurf、WorkBuddy 等）后，你只需用自然语言告诉 AI「帮我做一个飞驰人生的电影解说视频」，它就会自动完成全部流程：

```
选择电影 → 匹配解说风格 → 生成解说文案 → 合成视频 → 输出下载链接
```

**全程无需手动操作，AI 替你完成所有步骤。**

### 它能做什么

- ✅ **电影解说视频**：输入片名，自动生成完整的解说视频（文案 + 配音 + 画面 + BGM）
- ✅ **多种解说风格**：热血动作、爆笑喜剧、烧脑悬疑等 12 大类、90+ 种模板
- ✅ **多语种配音**：支持普通话、英语、日语等 11 种语言、63 个配音角色
- ✅ **批量生产**：告诉 AI「帮我做 10 条解说视频」，它会逐条完成
- ✅ **非工作时间运行**：让小龙虾在你睡觉时自动跑任务

---

## 快速开始

### 第 1 步：安装 CLI

前置条件：[Python 3.10+](https://www.python.org/downloads/)（安装时勾选 **Add to PATH**）、[Git](https://git-scm.com/downloads)

**macOS / Linux**
```bash
curl -fsSL https://raw.githubusercontent.com/NarratorAI-Studio/narrator-ai-cli/main/install.py | python3
```

**Windows（CMD / PowerShell 均可）**
```bat
python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/NarratorAI-Studio/narrator-ai-cli/main/install.py').read())"
```

验证安装：
```bash
narrator-ai-cli --version
```

### 第 2 步：获取 API Key

> 📧 发送邮件至 **merlinyang@gridltd.com** 或扫描下方二维码添加微信，即可获取 API Key。

![联系客服](./imgs/contact.png)

### 第 3 步：配置 API Key

```bash
narrator-ai-cli config set app_key 你的API_Key
```

### 第 4 步：开始做视频！

如果你在 AI Agent（小龙虾等）中使用，直接用自然语言：

> 「帮我做一个飞驰人生的电影解说视频，用喜剧风格」

如果你在终端中使用，参考下方的命令参考。

---

## 搭配 AI Agent 使用（推荐）

本工具搭配 AI Agent 使用效果最佳。安装 Skill 后，AI 就能理解如何使用这些命令。

👉 **安装 Skill**：[narrator-ai-cli-skill](https://github.com/NarratorAI-Studio/narrator-ai-cli-skill)

### 已测试的 Agent 平台

| 平台 | 安装方式 | 体验 |
|------|---------|------|
| **WorkBuddy**（腾讯） | 需要 CLI + Skill 两个仓库 | ⭐⭐⭐⭐⭐ 体验流畅 |
| **Windsurf** | 只需 CLI 仓库即可 | ⭐⭐⭐⭐⭐ 自动理解 |
| **有道龙虾** | 需要 CLI + Skill 两个仓库 | ⭐⭐⭐⭐ 稳定可用 |
| **QClaw**（腾讯） | 需要 CLI + Skill 两个仓库 | ⭐⭐⭐⭐ 稳定可用 |
| **元气 AI** | 需要 CLI + Skill 两个仓库 | ⭐⭐⭐ 基本可用 |

> 💡 **提示**：大部分国内 Agent 平台需要同时提供 CLI 和 Skill 两个仓库地址。海外的 Windsurf 只需要 CLI 仓库就能自动理解。

---

## 内置资源一览

无需上传任何素材，以下资源全部开箱即用：

| 资源类型 | 数量 | 查看命令 |
|---------|------|---------|
| 🎬 电影素材 | 93 部 | `narrator-ai-cli material list` |
| 🎵 背景音乐 | 146 首 | `narrator-ai-cli bgm list` |
| 🎙️ 配音角色 | 63 个（11 种语言） | `narrator-ai-cli dubbing list` |
| 📝 解说风格模板 | 90+ 个（12 大类） | `narrator-ai-cli task narration-styles` |

> 🔗 所有资源可在飞书文档中预览效果：[点击查看](https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc)

---

## 两条工作流路径

### 原创文案（推荐，速度更快、消耗更少）

```
搜索电影 → 快速文案 → 快速剪辑数据 → 合成视频 → 视觉模板(可选)
```

3 种模式：
- **热门影视**：知名电影，有完整影片信息
- **原声混剪**：使用原声片段混合解说
- **冷门新剧**：短剧或搜不到信息的影片

### 二创文案

```
爆款学习 → 生成解说文案 → 生成剪辑数据 → 合成视频 → 视觉模板(可选)
```

---

## 命令参考

### 配置管理

| 命令 | 说明 |
|------|------|
| `config init` | 交互式配置（服务器地址 + API Key） |
| `config show` | 查看当前配置（Key 已脱敏） |
| `config set <key> <value>` | 设置单个配置项 |

### 用户管理

| 命令 | 说明 |
|------|------|
| `user balance` | 查询账户余额 |
| `user login` | 用户名密码登录 |
| `user keys` | 列出子 API Key |
| `user create-key` | 创建子 API Key |

### 任务管理

| 命令 | 说明 |
|------|------|
| `task types` | 列出任务类型（`-V` 查看详情） |
| `task create <type> -d '{...}'` | 创建任务 |
| `task query <task_id>` | 查询任务状态和结果 |
| `task list` | 列出任务（支持过滤） |
| `task budget -d '{...}'` | 预估点数消耗 |
| `task verify -d '{...}'` | 创建任务前验证素材 |
| `task search-movie "<name>"` | 搜索电影信息（用于原创文案） |
| `task narration-styles` | 列出预置解说风格模板（90+） |
| `task templates` | 列出视觉模板（用于 magic-video） |
| `task get-writing` | 获取生成的解说文案 |
| `task save-writing -d '{...}'` | 保存修改后的解说文案 |
| `task save-clip -d '{...}'` | 保存修改后的剪辑数据 |

**任务类型：**

| 类型 | 工作流位置 |
|------|-----------|
| `popular-learning` | 二创文案 第 1 步 |
| `generate-writing` | 二创文案 第 2 步 |
| `fast-writing` | 原创文案 第 1 步 |
| `clip-data` | 二创文案 第 3 步 |
| `fast-clip-data` | 原创文案 第 2 步 |
| `video-composing` | 二创/原创 合成视频 |
| `magic-video` | 可选最终步骤（视觉模板） |
| `voice-clone` | 独立任务 |
| `tts` | 独立任务 |

### 文件管理

| 命令 | 说明 |
|------|------|
| `file upload <path>` | 上传文件（返回 file_id） |
| `file transfer --link <url>` | 通过链接转存远程文件（支持 HTTP / 百度网盘 / PikPak） |
| `file list` | 列出已上传文件 |
| `file info <file_id>` | 查看文件详情 |
| `file download <file_id>` | 获取预签名下载链接 |
| `file storage` | 查看存储用量（上限 3GB） |
| `file delete <file_id>` | 删除文件 |

### 预置素材 / BGM / 配音

| 命令 | 说明 |
|------|------|
| `material list` | 列出 93 部预置电影素材（`--genre`、`--search` 过滤） |
| `material genres` | 列出电影分类及数量 |
| `bgm list` | 列出 146 首预置 BGM（`--search` 过滤） |
| `dubbing list` | 列出 63 个配音角色（`--lang`、`--tag`、`--search` 过滤） |
| `dubbing languages` | 列出支持的语言 |
| `dubbing tags` | 列出场景推荐标签 |

## 数据流

```
                     文件上传 / 文件列表 / 预置素材
                     -> video_file_id, srt_file_id
                     BGM 列表 -> bgm_id
                     配音列表 -> dubbing, dubbing_type

    二创文案                              原创文案（更快、更省）
    ────────                              ────────────────────
    爆款学习 (可选)                        搜索电影
    输出: learning_model_id               输出: confirmed_movie_json
      或使用预置模板                              │
              │                           快速文案 (3种模式)
              ▼                           输入: learning_model_id + 电影信息
    生成解说文案                           输出: task_id, file_ids[0]
    输入: learning_model_id, 剧集数据              │
    输出: task_order_num, file_ids[0]     快速剪辑数据
              │                           输入: task_id, file_id, 剧集数据
              ▼                           输出: task_order_num
    生成剪辑数据                                   │
    输入: order_num, bgm, dubbing                  │
    输出: file_ids[0]                              │
              │                                    │
              ▼                                    ▼
         合成视频
         输入: order_num (来自文案步骤), bgm, dubbing
         输出: task_id, 视频 URL
                    │
                    ▼
         视觉模板 (可选)
         输入: task_id 或 file_id + template_name
         输出: 渲染后的视频 URL
```

## JSON 输出

所有命令均支持 `--json` 参数输出结构化数据（推荐 AI Agent 使用）：

```bash
narrator-ai-cli task list --json
narrator-ai-cli task query <task_id> --json
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `NARRATOR_SERVER` | API 服务器地址 |
| `NARRATOR_APP_KEY` | API Key |
| `NARRATOR_TIMEOUT` | 请求超时时间（秒，默认 30） |

## AI Agent 集成

详见 [narrator-ai-cli-skill](https://github.com/NarratorAI-Studio/narrator-ai-cli-skill)，包含完整的 SKILL.md 文件，让 AI Agent 自动理解如何使用本工具。

## 联系我们

需要 API Key 或使用帮助？欢迎联系：

- 📧 邮箱：merlinyang@gridltd.com
- 💬 微信：扫描下方二维码

![联系客服](./imgs/contact.png)
