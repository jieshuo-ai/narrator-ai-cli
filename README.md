# 🎬 Narrator AI CLI — Create Movie Narration Videos with Natural Language

[中文文档](README_CN.md)

> One command to install, one sentence to create videos. 93 built-in movies, 146 BGM tracks, 63 dubbing voices, 90+ narration templates — ready out of the box.

## What is this?

Narrator AI CLI is the command-line tool for [Narrator AI](https://ai.jieshuo.cn/), an AI-powered video narration platform. Once installed in your AI agent (OpenClaw, Windsurf, WorkBuddy, etc.), just say:

> "Create a movie narration video for Pegasus in a comedy style"

The AI handles everything automatically:

```
Select movie → Match narration style → Generate script → Compose video → Output download link
```

**No manual steps required. The AI completes the entire pipeline for you.**

### What it can do

- ✅ **Movie narration videos**: Input a movie name, get a complete narration video (script + voiceover + footage + BGM)
- ✅ **Multiple narration styles**: Action, Comedy, Thriller and more — 12 genres, 90+ templates
- ✅ **Multi-language voiceover**: 11 languages including English, Mandarin, Japanese, and 63 voice characters
- ✅ **Batch production**: Tell the AI "make 10 narration videos" and it will process them one by one
- ✅ **Run unattended**: Let the agent work while you sleep

---

## Quick Start

### Step 1: Install the CLI

Prerequisites: [Python 3.10+](https://www.python.org/downloads/) (check "Add to PATH"), [Git](https://git-scm.com/downloads)

**macOS / Linux**
```bash
curl -fsSL https://raw.githubusercontent.com/GridLtd-ProductDev/narrator-ai-cli/main/install.py | python3
```

**Windows (CMD / PowerShell)**
```bat
python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/GridLtd-ProductDev/narrator-ai-cli/main/install.py').read())"
```

Verify:
```bash
narrator-ai-cli --version
```

### Step 2: Get an API Key

> 📧 Email **merlinyang@gridltd.com** or scan the QR code below to get your API key.

![Contact us](./imgs/contact.png)

### Step 3: Configure

```bash
narrator-ai-cli config set app_key your_api_key
```

### Step 4: Start creating videos!

If using with an AI agent (OpenClaw, etc.), just use natural language:

> "Create a narration video for The Shawshank Redemption with an inspirational style"

For terminal usage, see Command Reference below.

---

## Using with AI Agents (Recommended)

This tool works best with AI agents. Install the Skill so the agent knows how to use these commands.

👉 **Install the Skill**: [narrator-ai-cli-skill](https://github.com/GridLtd-ProductDev/narrator-ai-cli-skill)

### Tested Platforms

| Platform | Setup | Experience |
|----------|-------|------------|
| **Windsurf** | CLI repo only | ⭐⭐⭐⭐⭐ Auto-understands |
| **WorkBuddy** (Tencent) | CLI + Skill repos | ⭐⭐⭐⭐⭐ Smooth |
| **Youdao Lobster** | CLI + Skill repos | ⭐⭐⭐⭐ Reliable |
| **QClaw** (Tencent) | CLI + Skill repos | ⭐⭐⭐⭐ Reliable |
| **Yuanqi AI** | CLI + Skill repos | ⭐⭐⭐ Functional |

> 💡 **Note**: Most domestic Chinese AI agents require both CLI and Skill repo URLs. Windsurf can work with just the CLI repo.

---

## Built-in Resources

No uploads needed — all of these are ready to use:

| Resource | Count | Command |
|----------|-------|---------|
| 🎬 Movie materials | 93 movies | `narrator-ai-cli material list` |
| 🎵 Background music | 146 tracks | `narrator-ai-cli bgm list` |
| 🎙️ Dubbing voices | 63 voices (11 languages) | `narrator-ai-cli dubbing list` |
| 📝 Narration templates | 90+ (12 genres) | `narrator-ai-cli task narration-styles` |

> 🔗 Preview all resources: [Feishu Docs](https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc)

---

## Two Workflow Paths

### Original Narration (Recommended — faster & cheaper)

```
Search movie → Fast writing → Fast clip data → Video composing → Magic video (optional)
```

3 modes:
- **Hot Drama**: Well-known movies with full info available
- **Original Mix**: Mix original audio with narration
- **New Drama**: Short dramas or movies without full info

### Adapted Narration

```
Popular learning → Generate writing → Clip data → Video composing → Magic video (optional)
```

---

## Command Reference

### Config

| Command | Description |
|---------|-------------|
| `config init` | Interactive setup (server URL + API key) |
| `config show` | Show current config (key masked) |
| `config set <key> <value>` | Set a config value |

### User

| Command | Description |
|---------|-------------|
| `user balance` | Query account balance |
| `user login` | Login with username/password |
| `user keys` | List sub API keys |
| `user create-key` | Create a sub API key |

### Task

| Command | Description |
|---------|-------------|
| `task types` | List task types (`-V` for details) |
| `task create <type> -d '{...}'` | Create a task |
| `task query <task_id>` | Query task status and results |
| `task list` | List tasks with filters |
| `task budget -d '{...}'` | Estimate credits consumption |
| `task verify -d '{...}'` | Verify materials before creation |
| `task search-movie "<name>"` | Search movie info |
| `task narration-styles` | List narration templates (90+) |
| `task templates` | List visual templates for magic-video |
| `task get-writing` | Retrieve generated script |
| `task save-writing -d '{...}'` | Save modified script |
| `task save-clip -d '{...}'` | Save modified clip data |

**Task Types:**

| Type | Workflow Position |
|------|-------------------|
| `popular-learning` | Adapted Narration Step 1 |
| `generate-writing` | Adapted Narration Step 2 |
| `fast-writing` | Original Narration Step 1 |
| `clip-data` | Adapted Narration Step 3 |
| `fast-clip-data` | Original Narration Step 2 |
| `video-composing` | Video composing (both paths) |
| `magic-video` | Optional final step (visual template) |
| `voice-clone` | Standalone |
| `tts` | Standalone |

### File

| Command | Description |
|---------|-------------|
| `file upload <path>` | Upload file (returns file_id) |
| `file transfer --link <url>` | Transfer remote file by link (HTTP / Baidu Netdisk / PikPak) |
| `file list` | List uploaded files |
| `file info <file_id>` | Get file details |
| `file download <file_id>` | Get presigned download URL |
| `file storage` | Show storage usage (3GB limit) |
| `file delete <file_id>` | Delete a file |

### Materials / BGM / Dubbing

| Command | Description |
|---------|-------------|
| `material list` | List 93 pre-built movies (`--genre`, `--search`) |
| `material genres` | List movie genres with counts |
| `bgm list` | List 146 BGM tracks (`--search`) |
| `dubbing list` | List 63 voices (`--lang`, `--tag`, `--search`) |
| `dubbing languages` | List supported languages |
| `dubbing tags` | List genre recommendation tags |

## Data Flow

```
                     file upload / file list / material list
                     -> video_file_id, srt_file_id
                     bgm list -> bgm_id
                     dubbing list -> dubbing, dubbing_type

    Adapted Narration                    Original Narration (faster)
    ─────────────────                    ────────────────────────────
    popular-learning (optional)          search-movie
    OUT: learning_model_id               OUT: confirmed_movie_json
      OR use pre-built template                  │
              │                          fast-writing (3 modes)
              ▼                          IN:  learning_model_id + movie_json
    generate-writing                     OUT: task_id, file_ids[0]
    IN:  learning_model_id, episodes              │
    OUT: task_order_num, file_ids[0]     fast-clip-data
              │                          IN:  task_id, file_id, episodes
              ▼                          OUT: task_order_num
    clip-data                                     │
    IN:  order_num, bgm, dubbing                  │
    OUT: file_ids[0]                              │
              │                                   │
              ▼                                   ▼
         video-composing
         IN:  order_num (from writing step), bgm, dubbing
         OUT: task_id, video URLs
                    │
                    ▼
         magic-video (optional)
         IN:  task_id or file_id + template_name
         OUT: rendered video URLs
```

## JSON Output

All commands support `--json` for structured output (recommended for AI agents):

```bash
narrator-ai-cli task list --json
narrator-ai-cli task query <task_id> --json
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `NARRATOR_SERVER` | API server URL |
| `NARRATOR_APP_KEY` | API key |
| `NARRATOR_TIMEOUT` | Timeout in seconds (default: 30) |

## AI Agent Integration

See [narrator-ai-cli-skill](https://github.com/GridLtd-ProductDev/narrator-ai-cli-skill) for the complete SKILL.md that teaches AI agents how to use this tool automatically.

## Contact

Need an API key or help? Reach out:

- 📧 Email: merlinyang@gridltd.com
- 💬 WeChat: Scan the QR code below

![Contact us](./imgs/contact.png)
