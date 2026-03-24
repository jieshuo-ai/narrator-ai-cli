# narrator-ai-cli

[中文文档](README_CN.md)

CLI client for Narrator AI video narration API. Designed for AI Agents and developers.

Two workflow paths for creating AI-narrated videos:

- **Adapted Narration** (二创文案): popular-learning -> generate-writing -> clip-data -> video-composing -> magic-video
- **Original Narration** (原创文案, faster & cheaper): fast-writing -> fast-clip-data -> video-composing -> magic-video
  - 3 modes: Hot Drama / Original Mix / New Drama

## Installation

### One-line Install

Prerequisites: [Python 3.10+](https://www.python.org/downloads/), [Git](https://git-scm.com/downloads)

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/jieshuo-ai/narrator-ai-cli/main/install.py | python3
```

**Windows (CMD / PowerShell)**

```bat
python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/jieshuo-ai/narrator-ai-cli/main/install.py').read())"
```

The installer clones the repo, creates a virtualenv, installs the CLI, and adds it to your PATH — works on all platforms with no shell-specific tools.

### Manual Install

Requires Python 3.10+ and pip or uv.

```bash
git clone https://github.com/jieshuo-ai/narrator-ai-cli.git
cd narrator-ai-cli
pip install -e .
```

### Verify

```bash
narrator-ai-cli --version
```

## Quick Start

### 1. Configure

```bash
# Interactive setup
narrator-ai-cli config init

# Or set directly
narrator-ai-cli config set app_key your_api_key

# Verify
narrator-ai-cli config show
```

### 2. Check Account

```bash
narrator-ai-cli user balance
```

### 3. Create a Narrated Video (Original Narration Path)

```bash
# Step 1: Pick a narration style template
narrator-ai-cli task narration-styles

# Step 2: Search movie info
narrator-ai-cli task search-movie "Pegasus" --json

# Step 3: Create narration script
narrator-ai-cli task create fast-writing --json -d '{
  "learning_model_id": "narrator-20250916152104-DYsban",
  "target_mode": "1",
  "playlet_name": "Pegasus",
  "confirmed_movie_json": { ... },
  "model": "flash"
}'

# Step 4: Poll until done
narrator-ai-cli task query <task_id> --json

# Step 5: Continue with clip-data, video-composing, magic-video...
```

## Command Reference

### Config

| Command | Description |
|---------|-------------|
| `config init` | Interactive setup (server URL + app key) |
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
| `task budget -d '{...}'` | Estimate points consumption |
| `task verify -d '{...}'` | Verify materials before task creation |
| `task search-movie "<name>"` | Search movie info for original narration |
| `task narration-styles` | List pre-built narration templates (90+) |
| `task templates` | List visual templates for magic-video |
| `task get-writing` | Retrieve generated narration script |
| `task save-writing -d '{...}'` | Save modified narration script |
| `task save-clip -d '{...}'` | Save modified clip data |

**Task Types:**

| Type | Workflow Position |
|------|-------------------|
| `popular-learning` | Adapted Narration Step 1 |
| `generate-writing` | Adapted Narration Step 2 |
| `fast-writing` | Original Narration Step 1 |
| `clip-data` | Adapted Narration Step 3 |
| `fast-clip-data` | Original Narration Step 2 |
| `video-composing` | Adapted Step 4 / Original Step 3 |
| `magic-video` | Optional final step (visual template) |
| `voice-clone` | Standalone |
| `tts` | Standalone |

### File

| Command | Description |
|---------|-------------|
| `file upload <path>` | Upload file (returns file_id) |
| `file list` | List uploaded files |
| `file info <file_id>` | Get file details |
| `file download <file_id>` | Get presigned download URL |
| `file storage` | Show storage usage |
| `file delete <file_id>` | Delete a file |

### Material (Pre-built Movie Materials)

| Command | Description |
|---------|-------------|
| `material list` | List all 93 pre-built movies (`--genre`, `--search` filters) |
| `material genres` | List available movie genres with counts |

### BGM (Background Music)

| Command | Description |
|---------|-------------|
| `bgm list` | List all 146 BGM tracks (`--search` filter) |

### Dubbing (Voice)

| Command | Description |
|---------|-------------|
| `dubbing list` | List all 63 voices (`--lang`, `--tag`, `--search` filters) |
| `dubbing languages` | List available languages (dubbing_type values) |
| `dubbing tags` | List genre recommendation tags |

## Pre-built Resources

All resources can be previewed at: https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc

### Narration Templates (90+)

```bash
narrator-ai-cli task narration-styles                    # list all
narrator-ai-cli task narration-styles --genre Action     # filter by genre
```

12 genres available. Use `narrator-ai-cli task narration-styles --json` to see all.

### Movie Materials (93 movies)

```bash
narrator-ai-cli material list                            # list all
narrator-ai-cli material list --genre Comedy             # filter by genre
narrator-ai-cli material list --search "Pegasus"         # search by name
```

Each movie provides `video_id` and `srt_id` for use in `episodes_data`.

### BGM Tracks (146 tracks)

```bash
narrator-ai-cli bgm list                                 # list all
narrator-ai-cli bgm list --search "River"                # search by name
```

### Dubbing Voices (63 voices, 11 languages)

```bash
narrator-ai-cli dubbing list                             # list all
narrator-ai-cli dubbing list --lang English              # filter by language
narrator-ai-cli dubbing list --tag Comedy                # filter by genre tag
narrator-ai-cli dubbing languages                        # list languages
```

Languages: Mandarin (39), English (4), Japanese (3), Korean (2), Spanish (3), Portuguese (2), German (2), French (2), Arabic (2), Thai (2), Indonesian (2).

## Data Flow

```
                     file upload / file list / material list
                     -> video_file_id, srt_file_id
                     bgm list -> bgm_id
                     dubbing list -> dubbing, dubbing_type

    Adapted Narration                    Original Narration
    ─────────────────                    ──────────────────
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

All commands support `--json` for machine-readable output (recommended for AI agents):

```bash
narrator-ai-cli task list --json
narrator-ai-cli task query <task_id> --json
narrator-ai-cli file list --json
```

Request body can be passed as inline JSON or from a file:

```bash
narrator-ai-cli task create fast-writing -d '{"key": "value"}'
narrator-ai-cli task create fast-writing -d @params.json
```

## Environment Variables

Override config file values:

| Variable | Description |
|----------|-------------|
| `NARRATOR_SERVER` | API server URL |
| `NARRATOR_APP_KEY` | API key |
| `NARRATOR_TIMEOUT` | Request timeout in seconds (default: 30) |

## Project Structure

```
src/narrator_ai/
├── cli.py              # Main entry point
├── client.py           # HTTP client (httpx + SSE)
├── config.py           # Config management (~/.narrator-ai/config.yaml)
├── output.py           # Output formatting (JSON / Rich table)
├── commands/
│   ├── config_cmd.py   # config init/show/set
│   ├── user.py         # balance/login/keys
│   ├── task.py         # task workflow commands (90+ narration templates)
│   ├── file.py         # file upload/download/list
│   ├── materials.py    # 93 pre-built movie materials
│   ├── bgm.py          # 146 pre-built BGM tracks
│   └── dubbing.py      # 63 pre-built dubbing voices
└── models/
    └── responses.py    # API response code constants
```

## For AI Agents

See [SKILL.md](SKILL.md) for a comprehensive machine-readable guide including:
- Complete data flow mappings (which output feeds into which input)
- Full parameter references for each task type
- Step-by-step workflow examples with exact commands
- Error handling guidance
