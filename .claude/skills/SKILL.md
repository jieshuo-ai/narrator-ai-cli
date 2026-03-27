---
name: narrator-ai
description: "Create AI-narrated videos using the Narrator AI API. Use when the user asks to create narration scripts, compose videos, clone voices, search movies, manage files, or check task status. Supports two workflow paths: Standard (popular-learning -> generate-writing -> clip-data -> video-composing -> magic-video) and Fast (fast-writing -> fast-clip-data -> video-composing -> magic-video)."
allowed-tools: Bash(narrator-ai-cli *)
---

# narrator-ai-cli Skill

You have access to `narrator-ai-cli`, a CLI tool for the Narrator AI video narration API.
Always use `--json` flag for all commands to get structured output you can parse.

## Prerequisites

The CLI must be configured before use. Check with:
```bash
narrator-ai-cli config show
```
If not configured, set up with:
```bash
narrator-ai-cli config set app_key <app_key>
```
Server defaults to `https://openapi.jieshuo.cn` — no need to configure.

**Need an app_key or help with setup?** Contact us to get started:
- 📧 Email: merlinyang@gridltd.com
- 💬 WeChat:

![联系客服](imgs/contact.png)

## Core Rules

1. **ALWAYS use `--json`** for all commands. Parse the JSON output to extract values for next steps.
2. **NEVER fabricate data** — never guess file IDs, movie info, or voice IDs. Always query from CLI commands.
3. **ASK user to choose** when there are multiple options (pre-built vs custom, which template, which movie, etc.).
4. **Poll task status** — tasks are async. After creation, poll with `narrator-ai-cli task query <task_id> --json` until `status` is `2` (success) or `3` (failed).
5. **video-composing order_num source differs by path**:
   - Standard Path: use `generate-writing`'s `task_order_num` (NOT clip-data's)
   - Fast Path: use `fast-clip-data`'s `task_order_num`
6. **dubbing list returns `id` and `type`** — pass `id` as `dubbing`, pass `type` as `dubbing_type`. They are two separate fields.
7. **negative_oss_key = video_oss_key** — always set `negative_oss_key` to the same value as `video_oss_key` in episodes_data.
8. **search-movie may take 60+ seconds** — this is normal (Gradio backend).

## Decision Points (ASK USER)

Before starting any workflow, you need to help the user make the following choices.
**Present the options and let the user decide. Do NOT pick for them.**

### Decision 1: Which workflow path?

ASK: "请选择工作流路径："
- **二创文案**: 爆款学习 → 生成解说文案 → 生成剪辑数据 → 合成视频 → 视觉模板(可选)
  - Based on existing reference video style, generates adapted narration
  - Suitable when: user wants to recreate content based on reference material
- **原创文案** (faster & cheaper): 快速文案 → 快速剪辑数据 → 合成视频 → 视觉模板(可选)
  - Generates original narration from movie info + narration template
  - Three sub-modes: 热门影视(hot drama), 原声混剪(original mix), 冷门/新剧(new drama)
  - Suitable when: user wants original narration, faster speed, lower cost

### Decision 2: Narration style — pre-built template or custom learning?

ASK: "解说风格：使用预置模板还是自定义学习？"
- **Option A: Pre-built template** (recommended, 90+ templates across 12 genres)
  ```bash
  narrator-ai-cli task narration-styles --json
  # or filter: narrator-ai-cli task narration-styles --genre <genre> --json
  ```
  Show the list to user, let them pick one. The `id` field is the `learning_model_id`.

- **Option B: Custom learning** (popular-learning task, Standard Path only)
  Requires user to provide a reference video + SRT. The output `learning_model_id` is used in generate-writing.

### Decision 3: Movie source files — pre-built material or user upload?

ASK: "电影素材：使用预置素材还是自己上传的文件？"
- **Option A: Pre-built materials** (93 movies ready to use)
  ```bash
  narrator-ai-cli material list --json
  # or search: narrator-ai-cli material list --search "<movie_name>" --json
  # or filter: narrator-ai-cli material list --genre <genre> --json
  ```
  Show results to user. Each entry has `video_id` and `srt_id`.
  - Use `video_id` as `video_oss_key` AND `negative_oss_key`
  - Use `srt_id` as `srt_oss_key`

- **Option B: User's uploaded files**
  ```bash
  narrator-ai-cli file list --json
  # or search: narrator-ai-cli file list --search "<keyword>" --json
  # or transfer by link: narrator-ai-cli file transfer --link "<url>" --json
  ```
  User picks video and SRT files from their cloud storage.

### Decision 4: BGM — pre-built track or user upload?

ASK: "背景音乐：使用预置BGM还是自己上传的音频？"
- **Option A: Pre-built BGM** (146 tracks)
  ```bash
  narrator-ai-cli bgm list --json
  # or search: narrator-ai-cli bgm list --search "<keyword>" --json
  ```
  Show results to user. The `id` field is the `bgm` parameter value.

- **Option B: User's uploaded audio**
  ```bash
  narrator-ai-cli file list --json
  ```
  User picks an audio file. Use its `file_id` as the `bgm` parameter.

### Decision 5: Dubbing voice — which voice and language?

ASK: "配音角色：请选择配音语言和角色"
```bash
# First show available languages
narrator-ai-cli dubbing languages --json

# Then list voices for chosen language
narrator-ai-cli dubbing list --lang <language> --json

# Or filter by genre recommendation
narrator-ai-cli dubbing list --tag <genre_tag> --json
```
Show results to user. From the selected voice:
- `id` field → pass as `dubbing` parameter
- `type` field → pass as `dubbing_type` parameter

**There is no "custom upload" option for dubbing — always pick from the pre-built list.**
(Users can create custom voices via `voice-clone` task separately.)

### Decision 6: Visual template (optional)?

ASK: "是否需要应用视觉模板？（可选步骤）"
- **Yes**: Pick a template
  ```bash
  narrator-ai-cli task templates --json
  ```
  Show results to user, let them pick. The `name` field goes into `template_name` list.
- **No**: Skip magic-video step.

## Workflow Path 1: 二创文案

```
popular-learning(optional) -> generate-writing -> clip-data -> video-composing -> magic-video(optional)
```

### Step 1: Get learning_model_id

Based on Decision 2:

```bash
# Option A: Pre-built template (recommended)
narrator-ai-cli task narration-styles --json
# -> user picks one -> learning_model_id = selected item's "id"

# Option B: Custom learning
narrator-ai-cli task create popular-learning --json -d '{
  "video_srt_path": "<srt_file_id from material or file list>",
  "video_path": "<video_file_id from material or file list>"
}'
# Poll until done -> extract learning_model_id from results
```

### Step 2: Generate Writing

```bash
# 2a. Search movie info (for confirmed_movie_json / story_info)
narrator-ai-cli task search-movie "<movie_name>" --json
# Show 3 results to user, let them pick one

# 2b. Get source files (based on Decision 3)
# Option A: narrator-ai-cli material list --search "<movie_name>" --json
# Option B: narrator-ai-cli file list --json
# -> user picks video and SRT files

# 2c. Create task
narrator-ai-cli task create generate-writing --json -d '{
  "learning_model_id": "<from step 1>",
  "learning_srt": "",
  "native_video": "",
  "native_srt": "",
  "playlet_name": "<movie_name>",
  "playlet_num": "1",
  "target_platform": "抖音",
  "vendor_requirements": "",
  "task_count": 1,
  "target_character_name": "<ASK user for main character name>",
  "story_info": "",
  "episodes_data": [{"video_oss_key": "<video_id>", "srt_oss_key": "<srt_id>", "negative_oss_key": "<video_id>", "num": 1}]
}'
# Poll -> extract task_order_num and results.file_ids[0]
```

### Step 3: Generate Clip Data

```bash
# 3a. Get BGM (based on Decision 4)
# Option A: narrator-ai-cli bgm list --json -> user picks -> bgm = selected "id"
# Option B: narrator-ai-cli file list --json -> user picks audio -> bgm = selected "file_id"

# 3b. Get dubbing voice (Decision 5)
# narrator-ai-cli dubbing list --lang <lang> --json -> user picks
# -> dubbing = selected "id", dubbing_type = selected "type"

# 3c. Create task
narrator-ai-cli task create clip-data --json -d '{
  "order_num": "<task_order_num from step 2>",
  "bgm": "<from Decision 4>",
  "dubbing": "<id from Decision 5>",
  "dubbing_type": "<type from Decision 5>"
}'
# Poll -> extract results.file_ids[0]
```

### Step 4: Video Composing

**IMPORTANT**: `order_num` is from step 2 (generate-writing), NOT step 3 (clip-data).

```bash
narrator-ai-cli task create video-composing --json -d '{
  "order_num": "<task_order_num from step 2 (generate-writing)>",
  "bgm": "<same bgm as step 3>",
  "dubbing": "<same dubbing as step 3>",
  "dubbing_type": "<same dubbing_type as step 3>"
}'
# Poll -> extract video URLs from results
```

### Step 5 (Optional): Magic Video

Based on Decision 6:

```bash
# List visual templates
narrator-ai-cli task templates --json
# -> user picks template name

# Apply template
narrator-ai-cli task create magic-video --json -d '{
  "task_id": "<task_id from step 4>",
  "template_name": ["<selected template name>"]
}'
```

## Workflow Path 2: 原创文案 (faster & cheaper)

```
search-movie -> fast-writing -> fast-clip-data -> video-composing -> magic-video(optional)
```

### Step 0: Prepare

```bash
# Get narration style template (Decision 2)
narrator-ai-cli task narration-styles --json
# -> user picks one -> learning_model_id

# Search movie info (required for target_mode=1)
narrator-ai-cli task search-movie "<movie_name>" --json
# -> show 3 results, user picks one -> confirmed_movie_json
```

### Step 1: Fast Writing (原创文案)

ASK user to choose a mode:
- **Mode 1 - 热门影视** (Hot Drama): generates original narration from movie info. Requires `confirmed_movie_json` from `search-movie`.
- **Mode 2 - 原声混剪** (Original Mix): mixes original audio with narration. Requires `episodes_data[{srt_oss_key, num}]`.
- **Mode 3 - 冷门/新剧** (New/Niche Drama): for lesser-known content. Requires `episodes_data[{srt_oss_key, num}]`.

```bash
# Mode 1 example (most common):
narrator-ai-cli task create fast-writing --json -d '{
  "learning_model_id": "<from Decision 2>",
  "target_mode": "1",
  "playlet_name": "<movie_name>",
  "model": "flash",
  "language": "Chinese (中文)",
  "perspective": "third_person",
  "confirmed_movie_json": <user-selected search result>
}'

# Mode 2/3 example:
narrator-ai-cli task create fast-writing --json -d '{
  "learning_model_id": "<from Decision 2>",
  "target_mode": "2",
  "playlet_name": "<movie_name>",
  "episodes_data": [{"srt_oss_key": "<srt_file_id>", "num": 1}]
}'
# Poll -> extract task_id and results.file_ids[0]
```

### Step 2: Fast Clip Data

```bash
# 2a. Get BGM (Decision 4)
# Option A: narrator-ai-cli bgm list --json -> user picks
# Option B: narrator-ai-cli file list --json -> user picks audio

# 2b. Get dubbing voice (Decision 5)
# narrator-ai-cli dubbing list --lang <lang> --json -> user picks

# 2c. Get source files (Decision 3)
# Option A: narrator-ai-cli material list --search "<movie_name>" --json
# Option B: narrator-ai-cli file list --json

# 2d. Create task
narrator-ai-cli task create fast-clip-data --json -d '{
  "task_id": "<task_id from step 1>",
  "file_id": "<results.file_ids[0] from step 1>",
  "bgm": "<from Decision 4>",
  "dubbing": "<id from Decision 5>",
  "dubbing_type": "<type from Decision 5>",
  "episodes_data": [{"video_oss_key": "<video_id>", "srt_oss_key": "<srt_id>", "negative_oss_key": "<video_id>", "num": 1}]
}'
# Poll -> extract task_order_num
```

### Step 3: Video Composing

**IMPORTANT**: In 原创文案 path, `order_num` comes from `fast-clip-data`'s `task_order_num`.

```bash
narrator-ai-cli task create video-composing --json -d '{
  "order_num": "<task_order_num from step 2 (fast-clip-data)>",
  "bgm": "<same bgm as step 2>",
  "dubbing": "<same dubbing as step 2>",
  "dubbing_type": "<same dubbing_type as step 2>"
}'
# Poll -> extract video URLs from results
```

### Step 4 (Optional): Magic Video

Based on Decision 6:
```bash
narrator-ai-cli task templates --json
# -> user picks template

narrator-ai-cli task create magic-video --json -d '{
  "task_id": "<task_id from step 3>",
  "template_name": ["<selected template name>"]
}'
```

## Standalone Tasks

```bash
# Voice Clone — clone a voice from audio sample
narrator-ai-cli task create voice-clone --json -d '{"audio_file_id": "<file_id from file list>"}'

# Text to Speech — convert text using cloned voice
narrator-ai-cli task create tts --json -d '{"voice_id": "<id>", "audio_text": "text"}'
```

## Utility Commands

```bash
# Account
narrator-ai-cli user balance --json

# Tasks
narrator-ai-cli task list --json
narrator-ai-cli task list --status 2 --type 9 --json   # filter: status 0-4, type 1-10
narrator-ai-cli task query <task_id> --json
narrator-ai-cli task budget --json -d '{...}'           # estimate points
narrator-ai-cli task verify --json -d '{...}'           # verify materials

# Writing management
narrator-ai-cli task get-writing --task-id <id> --file-id <id> --json
narrator-ai-cli task save-writing --json -d '{"task_id":"...", "file_id":"...", "content":[{"type":"解说","text":"..."}]}'

# Files (user's uploaded files)
narrator-ai-cli file list --json
narrator-ai-cli file list --search "<keyword>" --json
narrator-ai-cli file upload ./file.mp4 --json
narrator-ai-cli file transfer --link "<url>" --json          # transfer by HTTP/Baidu/PikPak link
narrator-ai-cli file info <file_id> --json
narrator-ai-cli file download <file_id> --json
narrator-ai-cli file storage --json
narrator-ai-cli file delete <file_id> --json

# Pre-built Resources
narrator-ai-cli task narration-styles --json            # 90+ narration style templates
narrator-ai-cli task narration-styles --genre <g> --json
narrator-ai-cli material list --json                     # 93 pre-built movies (video + SRT)
narrator-ai-cli material list --genre <g> --json
narrator-ai-cli material list --search "<name>" --json
narrator-ai-cli material genres --json
narrator-ai-cli bgm list --json                          # 146 pre-built BGM tracks
narrator-ai-cli bgm list --search "<name>" --json
narrator-ai-cli dubbing list --json                      # 63 pre-built dubbing voices
narrator-ai-cli dubbing list --lang <lang> --json
narrator-ai-cli dubbing list --tag <tag> --json
narrator-ai-cli dubbing languages --json
narrator-ai-cli dubbing tags --json
narrator-ai-cli task templates --json                    # visual templates (magic-video)
narrator-ai-cli task search-movie "<name>" --json        # movie info search

# All pre-built resources can be previewed at:
# https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc
```

## Task Status Codes

- `0` = init
- `1` = in_progress
- `2` = success (done, extract results)
- `3` = failed (check error_message_slug)
- `4` = cancelled

## Error Codes

- `10001` = failed (generic)
- `10004` = invalid app key
- `10009` = insufficient balance — notify the user:
  ```
  ⚠️ 账户余额不足，请联系客服充值或获取 App Key：
  📧 Email: merlinyang@gridltd.com
  ```
  Then display: `![联系客服](imgs/contact.png)`
- `10010` = task not found
- `60000` = retryable error (retry the operation)
