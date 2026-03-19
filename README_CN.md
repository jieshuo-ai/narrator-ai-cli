# narrator-ai-cli

[English](README.md)

Narrator AI 视频解说 API 的命令行客户端，专为 AI Agent 和开发者设计。

支持两条工作流路径：

- **二创文案**：爆款学习 → 生成解说文案 → 生成剪辑数据 → 合成视频 → 视觉模板(可选)
- **原创文案**（速度更快，消耗更少）：快速文案 → 快速剪辑数据 → 合成视频 → 视觉模板(可选)
  - 3 种模式：热门影视 / 原声混剪 / 冷门新剧

## 安装

### 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/jieshuo-ai/narrator-ai-cli/main/install.sh | bash
```

自动克隆仓库、创建虚拟环境、安装 CLI 并添加到 PATH。

### 手动安装

需要 Python 3.10+ 和 pip 或 uv。

```bash
git clone https://github.com/jieshuo-ai/narrator-ai-cli.git
cd narrator-ai-cli
pip install -e .
```

### 验证安装

```bash
narrator-ai-cli --version
```

## 快速开始

### 1. 配置

```bash
# 交互式配置
narrator-ai-cli config init

# 或直接设置
narrator-ai-cli config set app_key your_api_key

# 查看配置
narrator-ai-cli config show
```

### 2. 查看账户

```bash
narrator-ai-cli user balance
```

### 3. 创建解说视频（原创文案路径）

```bash
# 第 1 步：选择解说风格模板
narrator-ai-cli task narration-styles

# 第 2 步：搜索电影信息
narrator-ai-cli task search-movie "飞驰人生" --json

# 第 3 步：创建解说文案
narrator-ai-cli task create fast-writing --json -d '{
  "learning_model_id": "narrator-20250916152104-DYsban",
  "target_mode": "1",
  "playlet_name": "飞驰人生",
  "confirmed_movie_json": { ... },
  "model": "flash"
}'

# 第 4 步：轮询任务状态直到完成
narrator-ai-cli task query <task_id> --json

# 第 5 步：继续创建剪辑数据、合成视频、视觉模板...
```

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
| `video-composing` | 二创文案 第 4 步 / 原创文案 第 3 步 |
| `magic-video` | 可选最终步骤（视觉模板） |
| `voice-clone` | 独立任务 |
| `tts` | 独立任务 |

### 文件管理

| 命令 | 说明 |
|------|------|
| `file upload <path>` | 上传文件（返回 file_id） |
| `file list` | 列出已上传文件 |
| `file info <file_id>` | 查看文件详情 |
| `file download <file_id>` | 获取预签名下载链接 |
| `file storage` | 查看存储用量 |
| `file delete <file_id>` | 删除文件 |

### 预置素材

| 命令 | 说明 |
|------|------|
| `material list` | 列出 93 部预置电影素材（`--genre`、`--search` 过滤） |
| `material genres` | 列出电影分类及数量 |

### 背景音乐

| 命令 | 说明 |
|------|------|
| `bgm list` | 列出 146 首预置 BGM（`--search` 过滤） |

### 配音

| 命令 | 说明 |
|------|------|
| `dubbing list` | 列出 63 个配音角色（`--lang`、`--tag`、`--search` 过滤） |
| `dubbing languages` | 列出支持的语言（即 dubbing_type 取值） |
| `dubbing tags` | 列出场景推荐标签 |

## 预置资源

所有资源均可在飞书文档中预览效果：https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc

### 解说风格模板（90+）

```bash
narrator-ai-cli task narration-styles                    # 列出全部
narrator-ai-cli task narration-styles --genre 爆笑喜剧   # 按风格筛选
```

12 种风格：热血动作、烧脑悬疑、励志成长、爆笑喜剧、灾难求生、悬疑惊悚、惊悚恐怖、东方奇谈、家庭伦理、情感人生、奇幻科幻、传奇人物

### 电影素材（93 部）

```bash
narrator-ai-cli material list                            # 列出全部
narrator-ai-cli material list --genre 喜剧片             # 按分类筛选
narrator-ai-cli material list --search "飞驰人生"         # 按名称搜索
```

每部电影提供 `video_id` 和 `srt_id`，直接用于 `episodes_data`。

### 背景音乐（146 首）

```bash
narrator-ai-cli bgm list                                 # 列出全部
narrator-ai-cli bgm list --search "单车"                 # 按名称搜索
```

### 配音角色（63 个，11 种语言）

```bash
narrator-ai-cli dubbing list                             # 列出全部
narrator-ai-cli dubbing list --lang 普通话               # 按语言筛选
narrator-ai-cli dubbing list --tag 喜剧                  # 按场景标签筛选
narrator-ai-cli dubbing languages                        # 列出支持语言
```

支持语言：普通话(39)、英语(4)、日语(3)、韩语(2)、西班牙语(3)、葡萄牙语(2)、德语(2)、法语(2)、阿拉伯语(2)、泰语(2)、印尼语(2)

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
narrator-ai-cli file list --json
```

请求体可以通过行内 JSON 或文件传入：

```bash
narrator-ai-cli task create fast-writing -d '{"key": "value"}'
narrator-ai-cli task create fast-writing -d @params.json
```

## 环境变量

通过环境变量覆盖配置文件：

| 变量 | 说明 |
|------|------|
| `NARRATOR_SERVER` | API 服务器地址 |
| `NARRATOR_APP_KEY` | API Key |
| `NARRATOR_TIMEOUT` | 请求超时时间（秒，默认 30） |

## 项目结构

```
src/narrator_ai/
├── cli.py              # 主入口
├── client.py           # HTTP 客户端（httpx + SSE）
├── config.py           # 配置管理（~/.narrator-ai/config.yaml）
├── output.py           # 输出格式化（JSON / Rich 表格）
├── commands/
│   ├── config_cmd.py   # 配置命令
│   ├── user.py         # 用户管理
│   ├── task.py         # 任务工作流（90+ 解说模板）
│   ├── file.py         # 文件管理
│   ├── materials.py    # 93 部预置电影素材
│   ├── bgm.py          # 146 首预置背景音乐
│   └── dubbing.py      # 63 个预置配音角色
└── models/
    └── responses.py    # API 响应码常量
```

## AI Agent 集成

详见 [SKILL.md](SKILL.md)，包含：
- 完整的数据流映射（每步的输出如何传入下一步）
- 每种任务类型的完整参数说明
- 逐步工作流示例（附完整命令）
- 6 个决策点说明（需要用户选择的地方）
- 错误处理指南
