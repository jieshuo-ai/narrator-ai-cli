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
narrator-ai-cli config set server <server_url>
narrator-ai-cli config set app_key <app_key>
```

## Core Rules

1. **ALWAYS use `--json`** for all commands. Parse the JSON output to extract values for next steps.
2. **NEVER fabricate `confirmed_movie_json`** — always use `narrator-ai-cli task search-movie` result.
3. **NEVER guess file_ids** — always get them from `narrator-ai-cli file list --json`.
4. **Poll task status** — tasks are async. After creation, poll with `narrator-ai-cli task query <task_id> --json` until `status` is `2` (success) or `3` (failed).
5. **video-composing uses generate-writing's order_num**, NOT clip-data's.
6. **Prefer pre-built narration templates** — use `narrator-ai-cli task narration-styles --json` to list. Pick the genre matching the movie.
7. **search-movie may take 60+ seconds** — this is normal (Gradio backend).

## Workflow Path 1: Standard

```
popular-learning -> generate-writing -> clip-data -> video-composing -> magic-video(optional)
```

### Step 1: Popular Learning (or use pre-built template)

```bash
# Option A: Use pre-built template (recommended, skip to Step 2)
narrator-ai-cli task narration-styles --json
# Pick learning_model_id matching genre

# Option B: Learn from reference video
narrator-ai-cli task create popular-learning --json -d '{
  "video_srt_path": "<srt_file_id>",
  "video_path": "<video_file_id>"
}'
# Poll until done, extract learning_model_id from results
```

### Step 2: Generate Writing

```bash
# 2a. Search movie info
narrator-ai-cli task search-movie "<movie_name>" --json
# Pick one result -> use summary as story_info

# 2b. Get source files (use pre-built materials or uploaded files)
narrator-ai-cli material list --search "<movie_name>" --json
# OR: narrator-ai-cli file list --json
# Use video_id as video_oss_key & negative_oss_key, srt_id as srt_oss_key

# 2c. Create task
narrator-ai-cli task create generate-writing --json -d '{
  "learning_model_id": "<template_id or from step 1>",
  "learning_srt": "",
  "native_video": "",
  "native_srt": "",
  "playlet_name": "<movie_name>",
  "playlet_num": "1",
  "target_platform": "抖音",
  "vendor_requirements": "",
  "task_count": 1,
  "target_character_name": "<main_character_name>",
  "story_info": "",
  "episodes_data": [{"video_oss_key": "<video_file_id>", "srt_oss_key": "<srt_file_id>", "negative_oss_key": "<video_file_id>", "num": 1}]
}'
# Poll -> extract task_order_num and results.file_ids[0]
```

### Step 3: Generate Clip Data

```bash
narrator-ai-cli task create clip-data --json -d '{
  "order_num": "<task_order_num from step 2>",
  "bgm": "<bgm_file_id from file list>",
  "dubbing": "<voice_id, e.g. MiniMaxVoiceId20>",
  "dubbing_type": "普通话"
}'
# Poll -> extract results.file_ids[0]
```

### Step 4: Video Composing

**IMPORTANT**: `order_num` is from step 2 (generate-writing), NOT step 3.

```bash
narrator-ai-cli task create video-composing --json -d '{
  "order_num": "<task_order_num from step 2>",
  "bgm": "<bgm_file_id from file list>",
  "dubbing": "<voice_id, e.g. MiniMaxVoiceId20>",
  "dubbing_type": "普通话"
}'
# Poll -> extract video URLs from results
```

### Step 5 (Optional): Magic Video

```bash
# List available visual templates
narrator-ai-cli task templates --json

# Apply template
narrator-ai-cli task create magic-video --json -d '{
  "task_id": "<task_id from step 4>",
  "template_name": ["<template_name>"]
}'
```

## Workflow Path 2: Fast

```
search-movie -> fast-writing -> fast-clip-data -> video-composing -> magic-video(optional)
```

### Step 0: Prepare

```bash
# Get narration style template
narrator-ai-cli task narration-styles --json

# Search movie info (required for target_mode=1)
narrator-ai-cli task search-movie "<movie_name>" --json

# Get source files (pre-built materials or uploaded)
narrator-ai-cli material list --search "<movie_name>" --json
# OR: narrator-ai-cli file list --json
```

### Step 1: Fast Writing

```bash
narrator-ai-cli task create fast-writing --json -d '{
  "learning_model_id": "<template_id>",
  "target_mode": "1",
  "playlet_name": "<movie_name>",
  "model": "flash",
  "language": "Chinese (中文)",
  "perspective": "third_person",
  "confirmed_movie_json": <search_result_object>
}'
# Poll -> extract task_id and results.file_ids[0]
```

target_mode: "1"=Hot Drama (needs confirmed_movie_json), "2"=Original Mix (needs episodes_data), "3"=New Drama (needs episodes_data)

### Step 2: Fast Clip Data

```bash
narrator-ai-cli task create fast-clip-data --json -d '{
  "task_id": "<task_id from step 1>",
  "file_id": "<results.file_ids[0] from step 1>",
  "bgm": "<bgm_file_id from file list>",
  "dubbing": "<voice_id, e.g. MiniMaxVoiceId20>",
  "dubbing_type": "普通话",
  "episodes_data": [{"video_oss_key": "<video_file_id>", "srt_oss_key": "<srt_file_id>", "negative_oss_key": "<video_file_id>", "num": 1}]
}'
# Poll -> extract task_order_num
```

### Step 3-4: Same as Standard Path Steps 4-5

## Standalone Tasks

```bash
# Voice Clone
narrator-ai-cli task create voice-clone --json -d '{"audio_file_id": "<file_id>"}'

# Text to Speech
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

# Files
narrator-ai-cli file list --json
narrator-ai-cli file list --search "<keyword>" --json
narrator-ai-cli file upload ./file.mp4 --json
narrator-ai-cli file info <file_id> --json
narrator-ai-cli file download <file_id> --json
narrator-ai-cli file storage --json
narrator-ai-cli file delete <file_id> --json

# Templates & Materials
narrator-ai-cli task narration-styles --json            # pre-built narration models (90+)
narrator-ai-cli task narration-styles --genre 情感人生 --json  # filter by genre
narrator-ai-cli task templates --json                    # visual templates for magic-video
narrator-ai-cli task search-movie "<name>" --json        # movie info for fast-writing

# Pre-built Movie Materials (93 movies with video + SRT)
narrator-ai-cli material list --json                     # list all movies
narrator-ai-cli material list --genre 喜剧片 --json      # filter by genre
narrator-ai-cli material list --search "飞驰" --json     # search by name
narrator-ai-cli material genres --json                   # list available genres

# Pre-built BGM Tracks (146 tracks)
narrator-ai-cli bgm list --json                          # list all BGM
narrator-ai-cli bgm list --search "单车" --json          # search by name

# Pre-built Dubbing Voices (63 voices, 11 languages)
narrator-ai-cli dubbing list --json                      # list all voices
narrator-ai-cli dubbing list --lang 普通话 --json        # filter by language (= dubbing_type)
narrator-ai-cli dubbing list --tag 喜剧 --json           # filter by genre tag
narrator-ai-cli dubbing list --search "沈腾" --json      # search by name
narrator-ai-cli dubbing languages --json                 # list languages
narrator-ai-cli dubbing tags --json                      # list genre tags
# IMPORTANT: the voice 'type' field IS the 'dubbing_type' value for task creation
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
- `10009` = insufficient balance
- `10010` = task not found
- `60000` = retryable error (retry the operation)

## Pre-built Narration Templates (90+ templates)

90+ templates across 12 genres. Always use the CLI to get the full list:

```bash
# List all templates
narrator-ai-cli task narration-styles --json

# Filter by genre
narrator-ai-cli task narration-styles --genre 情感人生 --json
narrator-ai-cli task narration-styles --genre 烧脑悬疑 --json
```

Available genres: 热血动作, 烧脑悬疑, 励志成长, 爆笑喜剧, 灾难求生, 悬疑惊悚, 惊悚恐怖, 东方奇谈, 家庭伦理, 情感人生, 奇幻科幻, 传奇人物

View template previews and effects: https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc
