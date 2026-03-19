# narrator-ai CLI Skill

CLI client for Narrator AI video narration API. Use this tool to create AI-narrated videos from source materials.

## Setup

```bash
narrator-ai-cli config set server <server_url>
narrator-ai-cli config set app_key <your_app_key>
```

Or via environment variables: `NARRATOR_SERVER`, `NARRATOR_APP_KEY`.

## Core Concepts

- **file_id**: UUID identifier for uploaded files. Obtain via `file upload` or from task results.
- **task_id**: UUID returned when creating a task. Use with `task query` to poll status.
- **task_order_num**: Assigned after task creation. Used as `order_num` input for downstream tasks.
- **file_ids**: List of output file IDs in completed task results. Used as input for next steps.
- **learning_model_id**: A narration style model. Can be obtained from popular-learning task, OR use a pre-built template (see below). When using a pre-built template, you do NOT need to provide `learning_srt` — the template already contains the style.
- **learning_srt**: Reference SRT file_id (a pre-existing narration style sample). Only needed when NOT using a `learning_model_id`.
- All commands support `--json` for structured output. Always use `--json` when parsing results programmatically.
- Pass request body via `-d '{"key": "value"}'` or `-d @file.json`.

## Pre-built Narration Templates

These templates provide ready-to-use narration styles. Use the `learning_model_id` directly in
`generate-writing` or `fast-writing` — no need for popular-learning or learning_srt.

List available templates via CLI:
```bash
narrator-ai-cli task narration-styles --json
```

Browse and choose templates from the full documentation:
**https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc**

Copy the `learning_model_id` of the template that best matches your movie's genre, then pass it
in the task creation request.

**Usage example** (fast-writing with pre-built template):
```bash
# 1. List templates to find the right one
narrator-ai-cli task narration-styles --json

# 2. Search movie info
narrator-ai-cli task search-movie "飞驰人生" --json

# 3. Create task with template ID + movie info
narrator-ai-cli task create fast-writing --json -d '{
  "learning_model_id": "narrator-20250916152104-DYsban",
  "target_mode": "1",
  "playlet_name": "飞驰人生",
  "confirmed_movie_json": <paste search-movie result>,
  "model": "flash"
}'
```

## Prerequisites Before Creating Tasks

### 1. Select Source Files

Video and SRT files needed for task creation come from the file list. Upload files first if needed,
then list and pick the file_ids.

```bash
# Upload a file (returns file_id)
narrator-ai-cli file upload ./movie.mp4 --json
narrator-ai-cli file upload ./subtitles.srt --json

# List available files to pick from
narrator-ai-cli file list --json

# Filter by filename
narrator-ai-cli file list --search "飞驰人生" --json
```

The `file_id` from the list is used as:
- `video_oss_key` / `video_path` — source video
- `srt_oss_key` / `video_srt_path` — subtitle file
- `learning_srt` — reference narration SRT (when not using pre-built template)
- `bgm` — background music file
- `audio_file_id` — voice clone audio sample

### 2. Search Movie Info

Before creating a fast-writing task with `target_mode=1` (Hot Drama), you MUST search for the movie first
and use one of the returned results as `confirmed_movie_json`. Do NOT fabricate movie info — it will produce
nonsensical narration content.

```bash
narrator-ai-cli task search-movie "<movie_name>" --json
```

**Output**: Returns up to 3 movie results, each containing:
```json
{
  "title": "Pegasus",
  "local_title": "飞驰人生",
  "original_title": "飞驰人生",
  "year": "2019",
  "director": "韩寒 (Han Han)",
  "stars": ["沈腾 (Shen Teng)", "黄景瑜 (Johnny Huang)", "尹正 (Yin Zheng)"],
  "genre": "喜剧, 运动",
  "summary": "曾经叱咤风云的拉力赛车手张驰因非法赛车被禁赛五年...",
  "poster_url": "https://...",
  "is_partial": false
}
```

**Usage**: Pick one result and pass it directly as `confirmed_movie_json` in the fast-writing request.
Note: This API call may take up to 60 seconds (Gradio backend). Results are cached for 24 hours.

## Workflow Path 1: Standard

```
popular-learning -> generate-writing -> clip-data -> video-composing -> magic-video(optional)
```

### Step 1: Popular Learning

Learn narration style from a reference video/srt.

```bash
narrator-ai-cli task create popular-learning --json -d '{
  "video_srt_path": "<srt_file_id>",
  "video_path": "<video_file_id>",
  "narrator_type": "movie",
  "model_version": "advanced"
}'
```

**Output**: `{"task_id": "..."}` -> Query until status=2, extract `learning_model_id` from results.

### Step 2: Search Movie + Generate Writing

First search for the movie, then generate narration script.

```bash
# 2a. Search movie info (for story_info)
narrator-ai-cli task search-movie "<movie_name>" --json

# 2b. Create writing task
narrator-ai-cli task create generate-writing --json -d '{
  "learning_model_id": "<from step 1 or pre-built template>",
  "learning_srt": "",
  "native_video": "",
  "native_srt": "",
  "playlet_name": "Movie Name",
  "playlet_num": "1",
  "target_platform": "抖音",
  "vendor_requirements": "",
  "task_count": 1,
  "target_character_name": "<main_character_name>",
  "story_info": "",
  "episodes_data": [{"video_oss_key": "<video_file_id>", "srt_oss_key": "<srt_file_id>", "negative_oss_key": "<video_file_id>", "num": 1}]
}'
```

**Output**: `{"task_id": "..."}` -> Query until status=2, extract:
- `task_order_num` -> used as `order_num` in step 3 AND step 4
- `results.file_ids[0]` -> narration script file_id

### Step 3: Generate Clip Data

Generate editing timeline from narration script.

```bash
narrator-ai-cli task create clip-data --json -d '{
  "order_num": "<task_order_num from step 2>",
  "bgm": "<bgm_file_id>",
  "dubbing": "<voice_id, e.g. MiniMaxVoiceId20>",
  "dubbing_type": "普通话"
}'
```

**Output**: `{"task_id": "..."}` -> Query until status=2, extract:
- `results.file_ids[0]` -> clip data file_id (for magic-video staged mode)

### Step 4: Video Composing

Compose final video. **IMPORTANT**: `order_num` comes from step 2 (generate-writing), NOT step 3.

```bash
narrator-ai-cli task create video-composing --json -d '{
  "order_num": "<task_order_num from step 2 (generate-writing)>",
  "bgm": "<bgm_file_id>",
  "dubbing": "<voice_id, e.g. MiniMaxVoiceId20>",
  "dubbing_type": "普通话"
}'
```

**Output**: `{"task_id": "..."}` -> Query until status=2, extract video URLs from results.

### Step 5 (Optional): Magic Video / Visual Template

Apply visual template to the composed video.

```bash
# List available templates first
narrator-ai-cli task templates --json

# One-stop mode (uses video-composing task_id)
narrator-ai-cli task create magic-video --json -d '{
  "task_id": "<task_id from step 4>",
  "template_name": ["template_name"]
}'

# Staged mode (uses clip data file_id from step 3)
narrator-ai-cli task create magic-video --json -d '{
  "file_id": "<file_id from step 3 results.file_ids[0]>",
  "template_name": ["template_name"]
}'
```

## Workflow Path 2: Fast

```
search-movie -> fast-writing -> fast-clip-data -> video-composing -> magic-video(optional)
```

### Step 0: Search Movie Info

**Required for target_mode=1.** Search the movie database to get accurate movie metadata.

```bash
narrator-ai-cli task search-movie "飞驰人生" --json
```

Pick one of the returned results (usually up to 3). The selected result will be passed as
`confirmed_movie_json` in the next step. Do NOT manually construct this data — always use the
search result to ensure accurate narration content.

### Step 1: Fast Writing

Quick narration generation. Uses `learning_model_id` or `learning_srt` (reference srt file_id).

```bash
narrator-ai-cli task create fast-writing --json -d '{
  "learning_srt": "<reference_srt_file_id>",
  "target_mode": "1",
  "playlet_name": "飞驰人生",
  "model": "flash",
  "language": "Chinese (中文)",
  "perspective": "third_person",
  "confirmed_movie_json": <paste the selected search result here>
}'
```

**Full parameter reference:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `learning_model_id` | str | One of two | - | Learning model ID (from popular-learning) |
| `learning_srt` | str | One of two | - | Reference SRT file_id (pre-existing narration sample) |
| `target_mode` | str | Yes | - | "1"=Hot Drama, "2"=Original Mix, "3"=New Drama |
| `playlet_name` | str | Yes | - | Movie/drama name |
| `confirmed_movie_json` | object | mode=1 | - | Movie info from `search-movie` (MUST use search result) |
| `episodes_data` | list | mode=2,3 | - | [{srt_oss_key, num}] for original/new drama |
| `model` | str | No | "pro" | "pro" (higher quality, 15pts/char) or "flash" (faster, 5pts/char) |
| `language` | str | No | "Chinese (中文)" | Output language |
| `perspective` | str | No | "third_person" | "first_person" or "third_person" |
| `target_character_name` | str | 1st person | - | Required when perspective=first_person |
| `custom_script_result_path` | str | No | - | Custom script result path |
| `webhook_url` | str | No | - | Callback URL for async notification |
| `webhook_token` | str | No | - | Callback authentication token |
| `webhook_data` | str | No | - | Passthrough data for callback |

`target_mode` details:
- `"1"` (Hot Drama): requires `confirmed_movie_json` from `search-movie`. Uses `learning_model_id` or `learning_srt` as narration style reference.
- `"2"` (Original Mix): requires `episodes_data[{srt_oss_key, num}]`. Mixes original audio with narration.
- `"3"` (New/Niche Drama): requires `episodes_data[{srt_oss_key, num}]`. For lesser-known or new content.

**Output**: `{"task_id": "..."}` -> Query until status=2, extract:
- `task_id` -> used in step 2
- `results.file_ids[0]` -> narration script file_id, used in step 2

### Step 2: Fast Clip Data

Generate editing timeline from fast-writing results.

```bash
narrator-ai-cli task create fast-clip-data --json -d '{
  "task_id": "<task_id from step 1>",
  "file_id": "<results.file_ids[0] from step 1>",
  "bgm": "<bgm_file_id>",
  "dubbing": "<voice_id, e.g. MiniMaxVoiceId20>",
  "dubbing_type": "普通话",
  "episodes_data": [{"video_oss_key": "<video_file_id>", "srt_oss_key": "<srt_file_id>", "negative_oss_key": "<video_file_id>", "num": 1}]
}'
```

**Output**: `{"task_id": "..."}` -> Query until status=2, extract `task_order_num`.

### Step 3-4: Same as Standard Path Steps 4-5

Use the `order_num` from fast-clip-data for video-composing, then optionally magic-video.

## Standalone Tasks

### Voice Clone

```bash
narrator-ai-cli task create voice-clone --json -d '{"audio_file_id": "<file_id>"}'
```

### Text to Speech

```bash
narrator-ai-cli task create tts --json -d '{"voice_id": "<voice_id>", "audio_text": "Text to speak"}'
```

## Utility Commands

### List Narration Style Templates

```bash
narrator-ai-cli task narration-styles --json
```

Full docs: https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc

### Search Movie Info

Search the movie database for use in fast-writing. Always use this before creating a fast-writing task
with target_mode=1 to ensure quality narration.

```bash
narrator-ai-cli task search-movie "<movie_name>" --json
```

### Query Task Status

```bash
narrator-ai-cli task query <task_id> --json
```

Status values: `0`=init, `1`=in_progress, `2`=success, `3`=failed, `4`=cancelled.
Poll until status is `2` (success) or `3` (failed).

### List Tasks

```bash
narrator-ai-cli task list --json
narrator-ai-cli task list --status 2 --type 9 --json  # completed fast-writing tasks
```

Type values: 1=popular_learning, 2=generate_writing, 3=video_composing, 4=voice_clone, 5=tts, 6=clip_data, 7=magic_video, 9=fast_writing, 10=fast_clip_data.

### List Visual Templates

```bash
narrator-ai-cli task templates --json
```

### Estimate Budget

```bash
narrator-ai-cli task budget --json -d '{
  "learning_model_id": "<id>",
  "native_video": "<file_id>",
  "native_srt": "<file_id>"
}'
```

### File Operations

```bash
narrator-ai-cli file upload ./video.mp4 --json       # Returns file_id
narrator-ai-cli file list --json                       # List uploaded files
narrator-ai-cli file info <file_id> --json             # File details
narrator-ai-cli file download <file_id> --json         # Get download URL
narrator-ai-cli file storage --json                    # Storage usage
narrator-ai-cli file delete <file_id> --json           # Delete file
```

### Check Balance

```bash
narrator-ai-cli user balance --json
```

## Data Flow Summary

```
                        ┌─────────────────────────────────────────┐
                        │   file upload / file list                │
                        │   -> video_file_id, srt_file_id, bgm_id │
                        │   (pick file_ids from file list)         │
                        └──────────────┬──────────────────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         │ Standard Path               │                Fast Path    │
         ▼                             │                             ▼
  popular-learning (optional)          │               ┌──► search-movie
  IN:  video_srt_path                  │               │    IN:  movie name
  OUT: learning_model_id               │               │    OUT: confirmed_movie_json
    OR use pre-built template          │               │             │
    (see narration-styles)             │               │             ▼
         │                             │               └─── fast-writing
         ▼                             │                   IN:  learning_model_id (pre-built OR from learning)
  generate-writing                     │                        OR learning_srt (when no template)
  IN:  learning_model_id               │
       episodes_data                   │                        target_mode, playlet_name
  OUT: task_order_num ─────────┐       │                        confirmed_movie_json (from search)
       file_ids[0]             │       │                   OUT: task_id, file_ids[0]
         │                     │       │                             │
         ▼                     │       │                             ▼
  clip-data                    │       │                   fast-clip-data
  IN:  order_num ◄─────────────┘       │                   IN:  task_id, file_id (from above)
       bgm, dubbing                    │                        episodes_data, bgm, dubbing
  OUT: file_ids[0]                     │                   OUT: task_order_num
         │                     │       │                             │
         │                     ▼       │                             ▼
         │              video-composing◄─────────────────────────────┘
         │              IN:  order_num (from generate-writing / fast-clip-data)
         │                   bgm, dubbing
         │              OUT: task_id, video URLs
         │                     │
         ▼                     ▼
  magic-video (optional)
  IN:  task_id (one_stop) OR file_id (staged)
       template_name (from 'task templates')
  OUT: sub_tasks with rendered video URLs
```

## Error Handling

- API errors return `{"code": <int>, "message": "<string>"}`.
- Common codes: `10001`=failed, `10004`=invalid app key, `10009`=insufficient balance, `10010`=task not found, `60000`=retryable error.
- CLI exits with code 1 on any error and prints the error message to stderr.
- On code `60000`, the operation can be retried.

## Important Notes

1. **Always use `search-movie` before fast-writing with target_mode=1.** Do NOT fabricate `confirmed_movie_json` — use the search API result directly. Fake movie info produces meaningless narration.
2. **Source files come from `file list`.** Video, SRT, BGM file_ids used in task creation are all obtained via `file list --json` or `file upload`. Do NOT guess file_ids.
3. **Poll task status until completion.** Tasks are async. Create returns `task_id`, then poll with `task query <task_id> --json` until `status` is `2` (success) or `3` (failed).
4. **The `search-movie` API may take up to 60+ seconds** due to Gradio backend. Results are cached for 24 hours.
5. **video-composing uses generate-writing's order_num**, not clip-data's. This is a common mistake.
6. **Use `--json` for all programmatic access.** Human-readable table output is for interactive use only.
7. **Prefer pre-built narration templates** over running popular-learning. Use `task narration-styles` to list, or browse https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc for details. Copy the `learning_model_id` and pass it directly.
