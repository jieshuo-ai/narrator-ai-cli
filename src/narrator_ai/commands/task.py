"""V2 Task commands - core workflow for Narrator AI.

Supports two workflow paths:

  Path 1 (Standard):
    popular-learning -> generate-writing -> clip-data -> video-composing -> magic-video(optional)

  Path 2 (Fast):
    fast-writing -> fast-clip-data -> video-composing -> magic-video(optional)
"""

import json as _json
from pathlib import Path
from typing import Optional

import typer

from narrator_ai.client import NarratorClient, NarratorAPIError
from narrator_ai.models.responses import (
    TASK_STATUS_INIT,
    TASK_STATUS_IN_PROGRESS,
    TASK_STATUS_SUCCESS,
    TASK_STATUS_FAILED,
    TASK_STATUS_CANCELLED,
)
from narrator_ai.output import (
    console,
    print_dict,
    print_error,
    print_json,
    print_sse_event,
    print_table,
    print_info,
)

app = typer.Typer(
    help=(
        "Task creation, query, and management.\n\n"
        "Workflow Path 1 (Standard):\n"
        "  popular-learning -> generate-writing -> clip-data -> video-composing -> magic-video\n\n"
        "Workflow Path 2 (Fast):\n"
        "  fast-writing -> fast-clip-data -> video-composing -> magic-video\n\n"
        "Use 'narrator-ai-cli task types' to list all available task types.\n"
        "Use 'narrator-ai-cli task create <type> --help' for creation details."
    ),
)

# --- Task type mapping ---
TASK_TYPES = {
    "popular-learning": {
        "path": "/v2/task/commentary/create_popular_learning",
        "name": "Popular Learning (Step 1 of Standard Path)",
        "help": (
            "Learn narration style from a reference video.\n"
            "Required: video_srt_path (srt file_id)\n"
            "Optional: video_path (video file_id), narrator_type, model_version\n"
            "Output: learning_model_id (used in generate-writing)\n"
            "Note: You can skip this step by using a pre-built template. See 'task narration-styles'."
        ),
    },
    "generate-writing": {
        "path": "/v2/task/commentary/create_generate_writing",
        "name": "Generate Writing (Step 2 of Standard Path)",
        "help": (
            "Generate narration script from learning model and video materials.\n"
            "Required: learning_model_id (from popular-learning OR pre-built template),\n"
            "          playlet_name, playlet_num, target_platform,\n"
            "          vendor_requirements, episodes_data[{video_oss_key, srt_oss_key, num}]\n"
            "Optional: target_character_name, story_info, task_count\n"
            "Output: task_id -> query for task_order_num, file_ids\n"
            "Tip: Use 'task narration-styles' to list pre-built learning_model_id values."
        ),
    },
    "fast-writing": {
        "path": "/v2/task/commentary/create_fast_generate_writing",
        "name": "Fast Generate Writing (Step 1 of Fast Path)",
        "help": (
            "Quickly generate narration script.\n"
            "Required: playlet_name, target_mode (1=hot drama, 2=original mix, 3=new drama)\n"
            "          learning_model_id (pre-built template, see 'task narration-styles')\n"
            "            OR learning_srt (reference srt file_id, when no template available)\n"
            "          confirmed_movie_json (when target_mode=1, MUST use 'task search-movie' result)\n"
            "          episodes_data (when target_mode=2,3): [{srt_oss_key, num}]\n"
            "Optional: model (pro/flash), language, perspective (first_person/third_person),\n"
            "          target_character_name (required when perspective=first_person)\n"
            "Output: task_id -> query for file_ids[0] (used in fast-clip-data)\n"
            "Tip: Use a pre-built template matching the movie genre for best results."
        ),
    },
    "clip-data": {
        "path": "/v2/task/commentary/create_generate_clip_data",
        "name": "Generate Clip Data (Step 3 of Standard Path)",
        "help": (
            "Generate editing timeline data from narration script.\n"
            "Required: order_num (from generate-writing task_order_num),\n"
            "          bgm (background music file_id), dubbing (voice id), dubbing_type\n"
            "Optional: custom_cover, subtitle_style, font_path\n"
            "Output: task_id -> query for task_order_num, file_ids"
        ),
    },
    "fast-clip-data": {
        "path": "/v2/task/commentary/create_generate_fast_writing_clip_data",
        "name": "Fast Writing Clip Data (Step 2 of Fast Path)",
        "help": (
            "Generate editing timeline from fast-writing results.\n"
            "Required: task_id (from fast-writing), file_id (from fast-writing file_ids[0]),\n"
            "          bgm (background music file_id), dubbing (voice id), dubbing_type,\n"
            "          episodes_data[{video_oss_key, srt_oss_key, num}]\n"
            "Optional: narration_script_file, custom_cover, subtitle_style, font_path\n"
            "Output: task_id -> query for task_order_num"
        ),
    },
    "video-composing": {
        "path": "/v2/task/commentary/create_video_composing",
        "name": "Video Composing (Step 4 Standard / Step 3 Fast)",
        "help": (
            "Compose final video from clip data.\n"
            "Required: order_num (from generate-writing task_order_num, NOT clip-data),\n"
            "          bgm (background music file_id), dubbing (voice id), dubbing_type\n"
            "  OR:     generate_task_id (gradio internal task id)\n"
            "Optional: custom_cover, subtitle_style, font_path\n"
            "Output: task_id -> query for results with video URLs"
        ),
    },
    "magic-video": {
        "path": "/v2/task/commentary/create_magic_video",
        "name": "Magic Video / Visual Template (Optional Final Step)",
        "help": (
            "Apply visual template to composed video.\n"
            "Mode 1 - one_stop: task_id (from video-composing) + template_name\n"
            "Mode 2 - staged:   file_id (clip data file_id) + template_name\n"
            "                    OR clip_data (JSON object) + template_name\n"
            "Required: template_name (list of template names, use 'narrator-ai-cli task templates' to list)\n"
            "Optional: template_params (per-template params dict), mode (one_stop/staged)\n"
            "Output: task_id, sub_tasks with rendering status"
        ),
    },
    "voice-clone": {
        "path": "/v2/task/voice_clone/create",
        "name": "Voice Clone",
        "help": (
            "Clone a voice from an audio sample.\n"
            "Required: audio_file_id\n"
            "Optional: clone_model (default: pro)\n"
            "Output: task_id, voice_id"
        ),
    },
    "tts": {
        "path": "/v2/task/text_to_speech/create",
        "name": "Text to Speech",
        "help": (
            "Convert text to speech using a cloned voice.\n"
            "Required: voice_id, audio_text\n"
            "Optional: clone_model (default: pro)\n"
            "Output: task_id with audio result"
        ),
    },
}

TASK_STATUS_MAP = {
    TASK_STATUS_INIT: "init",
    TASK_STATUS_IN_PROGRESS: "in_progress",
    TASK_STATUS_SUCCESS: "success",
    TASK_STATUS_FAILED: "failed",
    TASK_STATUS_CANCELLED: "cancelled",
}


def _client() -> NarratorClient:
    return NarratorClient()


@app.command("types")
def list_types(
    verbose: bool = typer.Option(False, "--verbose", "-V", help="Show detailed description for each type"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all available task types and their workflow position."""
    if json_mode:
        items = [{"type": k, "name": v["name"], "help": v.get("help", "")} for k, v in TASK_TYPES.items()]
        print_json(items)
        return

    if verbose:
        for key, info in TASK_TYPES.items():
            console.print(f"\n[bold cyan]{key}[/bold cyan]  [dim]{info['name']}[/dim]")
            if info.get("help"):
                for line in info["help"].split("\n"):
                    console.print(f"  {line}")
        console.print()
    else:
        items = [{"type": k, "name": v["name"]} for k, v in TASK_TYPES.items()]
        print_table(items, [("type", "Type"), ("name", "Name")], title="Task Types")


@app.command()
def create(
    task_type: str = typer.Argument(
        ...,
        help="Task type: popular-learning, generate-writing, fast-writing, clip-data, fast-clip-data, video-composing, magic-video, voice-clone, tts",
    ),
    data: str = typer.Option(
        ..., "-d", "--data",
        help="Request body as JSON string or @file.json reference",
    ),
    stream: bool = typer.Option(False, "--stream", "-s", help="Use SSE streaming for real-time progress"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON (recommended for agents)"),
):
    """Create a new task. Use 'task types -V' to see required params for each type.

    Examples:

      # Standard Path - Step 1: learn from reference video
      narrator-ai-cli task create popular-learning -d '{"video_srt_path": "<srt_file_id>"}'

      # Standard Path - Step 2: generate narration script
      narrator-ai-cli task create generate-writing -d '{"learning_model_id": "<id>", "playlet_name": "Movie", ...}'

      # Fast Path - Step 1: quick narration from movie info
      narrator-ai-cli task create fast-writing -d '{"learning_model_id": "<id>", "target_mode": "1", "playlet_name": "Movie", "confirmed_movie_json": {...}}'

      # Generate clip data (Standard Path Step 3)
      narrator-ai-cli task create clip-data -d '{"order_num": "<order_num>", "bgm": "<bgm_file_id>", "dubbing": "MiniMaxVoiceId20", "dubbing_type": "普通话"}'

      # Compose video (Step 4 Standard / Step 3 Fast)
      narrator-ai-cli task create video-composing -d '{"order_num": "<order_num>", "bgm": "<bgm_file_id>", "dubbing": "MiniMaxVoiceId20", "dubbing_type": "普通话"}'

      # Visual template (optional final step)
      narrator-ai-cli task create magic-video -d '{"task_id": "<video_composing_task_id>", "template_name": ["template"]}'

      # Voice clone
      narrator-ai-cli task create voice-clone -d '{"audio_file_id": "<file_id>"}'

      # Load params from file
      narrator-ai-cli task create fast-writing -d @params.json
    """
    if task_type not in TASK_TYPES:
        print_error(f"Unknown task type: {task_type}. Use 'narrator-ai-cli task types' to list.")
        raise typer.Exit(1)

    # Support @file.json syntax
    body = _load_json_data(data)
    type_info = TASK_TYPES[task_type]
    client = _client()

    try:
        if stream:
            print_info(f"Creating {type_info['name']} task (streaming)...")
            for event_type, event_data in client.post_sse(type_info["path"], json=body):
                print_sse_event(event_type, event_data, json_mode=json_mode)
        else:
            result = client.post(type_info["path"], json=body)
            print_dict(result, title=f"Task Created ({type_info['name']})", json_mode=json_mode)
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


@app.command()
def query(
    task_id: str = typer.Argument(..., help="Task ID (UUID) returned from task creation"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON (recommended for agents)"),
):
    """Query task status, results, and consumed points.

    Status codes: 0=init, 1=in_progress, 2=success, 3=failed, 4=cancelled.

    Key fields in response:
      task_order_num - used as 'order_num' input for downstream tasks
      results.file_ids - output file IDs for downstream tasks
      results.tasks - sub-task details with gradio results
      consumed_points - actual points consumed
    """
    try:
        data = _client().get(f"/v2/task/commentary/query/{task_id}")
        if not json_mode and isinstance(data, dict):
            status_code = data.get("status")
            data["status_name"] = TASK_STATUS_MAP.get(status_code, str(status_code))
        print_dict(data, title=f"Task {task_id}", json_mode=json_mode)
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


@app.command("list")
def list_tasks(
    page: int = typer.Option(1, help="Page number (starting from 1)"),
    limit: int = typer.Option(10, help="Items per page, max 100"),
    status: Optional[int] = typer.Option(None, help="Filter by status: 0=init, 1=in_progress, 2=success, 3=failed, 4=cancelled"),
    task_type: Optional[int] = typer.Option(
        None, "--type",
        help="Filter by type: 1=popular_learning, 2=generate_writing, 3=video_composing, "
             "4=voice_clone, 5=tts, 6=clip_data, 7=magic_video, 8=subsync, "
             "9=fast_writing, 10=fast_clip_data",
    ),
    category: Optional[str] = typer.Option(None, help="Filter by category: translate or commentary"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON (recommended for agents)"),
):
    """List tasks with pagination and optional filters."""
    params = {"page": page, "limit": limit}
    if status is not None:
        params["status"] = status
    if task_type is not None:
        params["type"] = task_type
    if category is not None:
        params["category"] = category

    try:
        data = _client().get("/v2/task/commentary/list", params=params)
        if json_mode:
            print_json(data)
        else:
            items = data.get("items", [])
            for item in items:
                s = item.get("status")
                item["status_name"] = TASK_STATUS_MAP.get(s, str(s))
            columns = [
                ("task_id", "Task ID"),
                ("type_name", "Type"),
                ("status_name", "Status"),
                ("consumed_points", "Points"),
                ("created_at", "Created"),
            ]
            print_table(
                items, columns,
                title=f"Tasks (page {data.get('page')}/{max(1, -(-data.get('total', 0) // limit))}, total: {data.get('total', 0)})",
            )
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


@app.command()
def budget(
    data: str = typer.Option(..., "-d", "--data", help="Estimation params as JSON or @file.json"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Estimate points consumption before creating tasks.

    Required fields depend on workflow:
      - learning_model_id OR learning_srt
      - native_video, native_srt (file IDs)
      - OR episodes_data for multi-episode

    Optional: model_version, narrator_type, refine_srt_gaps, template_names, text_model

    Returns breakdown: viral_learning_points, commentary_generation_points,
    video_synthesis_points, visual_template_points, total_consume_points.
    """
    body = _load_json_data(data)
    try:
        result = _client().post("/v2/task/commentary/consume_budget", json=body)
        print_dict(result, title="Budget Estimation", json_mode=json_mode)
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


@app.command()
def verify(
    data: str = typer.Option(..., "-d", "--data", help="Verification params as JSON or @file.json"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Verify materials (video, srt, bgm, dubbing) before creating tasks.

    Required: bgm (file_id), dubing_id (voice id)
    Conditional: native_video + native_srt (when episodes_data is empty),
                 learning_model_id OR learning_srt

    Returns: is_valid (bool), errors (list), warnings (list).
    """
    body = _load_json_data(data)
    try:
        result = _client().post("/v2/task/commentary/material_verification", json=body)
        print_dict(result, title="Material Verification", json_mode=json_mode)
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


@app.command("get-writing")
def get_writing(
    task_id: str = typer.Option(..., help="Task ID of the generate-writing or fast-writing task"),
    file_id: str = typer.Option(..., help="File ID from task results (file_ids[0])"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Retrieve generated narration script content for review or editing."""
    try:
        data = _client().get("/v2/task/commentary/get_generate_writed", params={
            "task_id": task_id,
            "file_id": file_id,
        })
        print_dict(data, title="Generated Writing", json_mode=json_mode)
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


@app.command("save-writing")
def save_writing(
    data: str = typer.Option(..., "-d", "--data", help="JSON: {task_id, file_id, content: [{type, text}, ...]}"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Save modified narration script content before composing video.

    The content field is a list of segments: [{type: "narration/original", text: "..."}, ...]
    """
    body = _load_json_data(data)
    try:
        result = _client().post("/v2/task/commentary/save_generate_writed", json=body)
        print_dict(result, title="Writing Saved", json_mode=json_mode)
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


@app.command("save-clip")
def save_clip(
    data: str = typer.Option(..., "-d", "--data", help="JSON: {task_id, file_id, clip_data: {...}}"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Save modified clip/editing data before composing video."""
    body = _load_json_data(data)
    try:
        result = _client().post("/v2/task/commentary/save_clip_data", json=body)
        print_dict(result, title="Clip Data Saved", json_mode=json_mode)
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


@app.command("search-movie")
def search_movie(
    query: str = typer.Argument(..., help="Movie/drama name to search"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Search movie/drama info for use in fast-writing's confirmed_movie_json.

    Returns up to 3 results. Pick one and pass it as confirmed_movie_json
    when creating a fast-writing task with target_mode=1.

    Example workflow:
      1. narrator-ai-cli task search-movie "飞驰人生" --json
      2. Pick a result from the list
      3. narrator-ai-cli task create fast-writing -d '{"confirmed_movie_json": <selected>, ...}'
    """
    try:
        client = NarratorClient(timeout=120)
        data = client.get("/v2/task/commentary/search_media_information", params={"query": query})
        if json_mode:
            print_json(data)
        else:
            results = data.get("data", data)
            if isinstance(results, list):
                for i, item in enumerate(results, 1):
                    console.print(f"\n[bold cyan]Result {i}[/bold cyan]")
                    print_dict(item)
            else:
                print_dict(data if isinstance(data, dict) else {"data": data}, title=f"Search: {query}")
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


NARRATION_TEMPLATES = [
    # 热血动作
    {"name": "热血动作-困兽之斗解说", "id": "narrator-20250916152104-DYsban", "genre": "热血动作"},
    {"name": "热血动作-战火祈愿解说", "id": "narrator-20251013135241-oscGNF", "genre": "热血动作"},
    {"name": "热血动作-亡命反杀解说", "id": "narrator-20251027094011-kvuJpH", "genre": "热血动作"},
    # 烧脑悬疑
    {"name": "烧脑悬疑-栽赃陷害解说", "id": "narrator-20250916152053-nBcHXC", "genre": "烧脑悬疑"},
    {"name": "烧脑悬疑-恶人成功解说", "id": "narrator-20250923153825-XjVolv", "genre": "烧脑悬疑"},
    {"name": "烧脑悬疑-女性犯罪解说", "id": "narrator-20250929165427-wNiGuu", "genre": "烧脑悬疑"},
    {"name": "烧脑悬疑-无间卧底解说", "id": "narrator-20250929180346-qZIrwc", "genre": "烧脑悬疑"},
    {"name": "烧脑悬疑-金蝉脱壳解说", "id": "narrator-20250930115028-baMeEb", "genre": "烧脑悬疑"},
    {"name": "烧脑悬疑-真相揭露解说", "id": "narrator-20250928113959-cceaBA", "genre": "烧脑悬疑"},
    {"name": "烧脑悬疑-密室求生解说", "id": "narrator-20251024180040-xtbSzv", "genre": "烧脑悬疑"},
    {"name": "烧脑悬疑-孤证追凶解说", "id": "narrator-20251027094241-FcEQRh", "genre": "烧脑悬疑"},
    {"name": "烧脑悬疑-迟到正义解说", "id": "narrator-20251110134448-Wnbqcq", "genre": "烧脑悬疑"},
    {"name": "烧脑悬疑-图灵测试解说", "id": "narrator-20251113154145-BHUwFE", "genre": "烧脑悬疑"},
    {"name": "烧脑悬疑-以恶制恶解说", "id": "narrator-20251202162015-vbNHYB", "genre": "烧脑悬疑"},
    # 励志成长
    {"name": "励志成长-师生情谊解说", "id": "narrator-20250918141539-NnpZlD", "genre": "励志成长"},
    {"name": "励志成长-职场逆袭解说", "id": "narrator-20250924181617-tdbfAK", "genre": "励志成长"},
    {"name": "励志成长-草根翻身解说", "id": "narrator-20250929165344-QhCZuq", "genre": "励志成长"},
    {"name": "励志成长-校园冒险解说", "id": "narrator-20250930115936-QUhgtx", "genre": "励志成长"},
    {"name": "励志成长-谎言揭露解说", "id": "narrator-20251027093930-ZjWryu", "genre": "励志成长"},
    # 爆笑喜剧
    {"name": "爆笑喜剧-乌龙伪装解说", "id": "narrator-20250918183013-ktylCA", "genre": "爆笑喜剧"},
    {"name": "爆笑喜剧-催泪反转解说", "id": "narrator-20250924170117-wDFCwI", "genre": "爆笑喜剧"},
    {"name": "爆笑喜剧-抗日整蛊解说", "id": "narrator-20250924170024-uzgpov", "genre": "爆笑喜剧"},
    {"name": "爆笑喜剧-人生互换解说", "id": "narrator-20250929171156-BrsDAQ", "genre": "爆笑喜剧"},
    {"name": "爆笑喜剧-欢喜冤家解说", "id": "narrator-20251020160131-vpQowB", "genre": "爆笑喜剧"},
    {"name": "爆笑喜剧-乌龙反转解说", "id": "narrator-20251015170653-OPraUg", "genre": "爆笑喜剧"},
    {"name": "爆笑喜剧-翁婿大战解说", "id": "narrator-20251208154841-PzYwtq", "genre": "爆笑喜剧"},
    # 灾难求生
    {"name": "灾难求生-绝境获救解说", "id": "narrator-20250919170450-ClVcgT", "genre": "灾难求生"},
    {"name": "灾难求生-绝境反杀解说", "id": "narrator-20250919170037-ARppif", "genre": "灾难求生"},
    {"name": "灾难求生-丧尸变异解说", "id": "narrator-20250929162226-vJHwms", "genre": "灾难求生"},
    {"name": "灾难求生-连锁困境解说", "id": "narrator-20250929163803-MSBmuw", "genre": "灾难求生"},
    {"name": "灾难求生-怪兽灭世解说", "id": "narrator-20250929181329-HkkCNd", "genre": "灾难求生"},
    {"name": "灾难求生-海洋求生解说", "id": "narrator-20251124153146-eTtang", "genre": "灾难求生"},
    {"name": "灾难求生-极限逃生解说", "id": "narrator-20251208135459-bQYqJl", "genre": "灾难求生"},
    # 悬疑惊悚 / 惊悚恐怖
    {"name": "悬疑惊悚-密室奇案解说", "id": "narrator-20250915161121-kwwIHs", "genre": "悬疑惊悚"},
    {"name": "惊悚恐怖-民俗鬼怪解说", "id": "narrator-20250922151737-YElQZc", "genre": "惊悚恐怖"},
    {"name": "惊悚恐怖-怨念起源解说", "id": "narrator-20250930113312-nEKWax", "genre": "惊悚恐怖"},
    {"name": "惊悚恐怖-无限轮回解说", "id": "narrator-20251124152521-BrEkBi", "genre": "惊悚恐怖"},
    {"name": "惊悚恐怖-新婚猎杀解说", "id": "narrator-20251124152748-jrljzu", "genre": "惊悚恐怖"},
    # 东方奇谈
    {"name": "东方奇谈-都市修仙解说", "id": "narrator-20250915154420-YVDLiW", "genre": "东方奇谈"},
    {"name": "东方奇谈-情蛊拉扯解说", "id": "narrator-20250919100408-vyXstO", "genre": "东方奇谈"},
    {"name": "东方奇谈-以善封神解说", "id": "narrator-20250929165601-LJlMZm", "genre": "东方奇谈"},
    {"name": "东方奇谈-志怪奇缘解说", "id": "narrator-20250929173453-PAPePO", "genre": "东方奇谈"},
    {"name": "东方奇谈-宫斗权谋解说", "id": "narrator-20251011164028-QdtnCh", "genre": "东方奇谈"},
    {"name": "东方奇谈-人狐情缘解说", "id": "narrator-20251020160213-vZhBdF", "genre": "东方奇谈"},
    # 家庭伦理
    {"name": "家庭伦理-偷听心声解说", "id": "narrator-20250915162937-zUrCtQ", "genre": "家庭伦理"},
    {"name": "家庭伦理-禁忌诱惑解说", "id": "narrator-20251013171543-hKWxyY", "genre": "家庭伦理"},
    # 情感人生
    {"name": "情感人生-亡命虐恋解说", "id": "narrator-20250926153249-iLajMr", "genre": "情感人生"},
    {"name": "情感人生-重返过去解说", "id": "narrator-20250929165350-MTiKrB", "genre": "情感人生"},
    {"name": "情感人生-宅斗权谋解说", "id": "narrator-20250929171320-lTlKVh", "genre": "情感人生"},
    {"name": "情感人生-亲情救赎解说", "id": "narrator-20250929173718-kXJmvj", "genre": "情感人生"},
    {"name": "情感人生-禁忌之恋解说", "id": "narrator-20250929180959-ErBYYg", "genre": "情感人生"},
    {"name": "情感人生-错过重逢解说", "id": "narrator-20250930113630-idjJQO", "genre": "情感人生"},
    {"name": "情感人生-隔代亲情解说", "id": "narrator-20250930114558-nbhPEa", "genre": "情感人生"},
    {"name": "情感人生-婚姻破裂解说", "id": "narrator-20250917165831-wGnJGP", "genre": "情感人生"},
    {"name": "情感人生-逆袭救场解说", "id": "narrator-20251016164408-DTSoSw", "genre": "情感人生"},
    {"name": "情感人生-宿命重逢解说", "id": "narrator-20251022114420-evOJCI", "genre": "情感人生"},
    {"name": "情感人生-赌局救赎解说", "id": "narrator-20251027094055-htirpB", "genre": "情感人生"},
    {"name": "情感人生-童年创伤解说", "id": "narrator-20251027094012-unpBYG", "genre": "情感人生"},
    {"name": "情感人生-初遇心动解说", "id": "narrator-20251027094054-KaFrWF", "genre": "情感人生"},
    {"name": "情感人生-宿敌相恋解说", "id": "narrator-20251030145038-mfCVGj", "genre": "情感人生"},
    {"name": "情感人生-为爱殉情解说", "id": "narrator-20251014165420-xPFhHA", "genre": "情感人生"},
    {"name": "情感人生-双向奔赴解说", "id": "narrator-20251106115918-wiEURB", "genre": "情感人生"},
    {"name": "情感人生-返乡救赎解说", "id": "narrator-20251113153731-DRupIR", "genre": "情感人生"},
    {"name": "情感人生-童话溯源解说", "id": "narrator-20251113154655-NnDifu", "genre": "情感人生"},
    {"name": "情感人生-绝命循环解说", "id": "narrator-20251124153657-ZBBwwL", "genre": "情感人生"},
    {"name": "情感人生-为爱搏命解说", "id": "narrator-20251124154511-hebvkH", "genre": "情感人生"},
    {"name": "情感人生-爱情复仇解说", "id": "narrator-20251009143826-RQIUFF", "genre": "情感人生"},
    {"name": "情感人生-商业联姻解说", "id": "narrator-20251009145048-CBygkT", "genre": "情感人生"},
    {"name": "情感人生-忘年之交解说", "id": "narrator-20251202160328-KhoIpc", "genre": "情感人生"},
    {"name": "情感人生-养老困境解说", "id": "narrator-20251202161600-Dvmdkf", "genre": "情感人生"},
    {"name": "情感人生-向阳而生解说", "id": "narrator-20251208134824-OYNnQX", "genre": "情感人生"},
    {"name": "情感人生-聋哑骗局解说", "id": "narrator-20251208135010-wLnfJr", "genre": "情感人生"},
    # 奇幻科幻
    {"name": "奇幻科幻-欲望深渊解说", "id": "narrator-20250922174548-khkyvU", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-异族重生解说", "id": "narrator-20250929173012-AptTKd", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-魔咒救赎解说", "id": "narrator-20250929180156-XqhhcL", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-异能人觉醒解说", "id": "narrator-20250930120652-AsoYAz", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-超级英雄解说", "id": "narrator-20250930172223-dWNzYw", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-上帝视角解说", "id": "narrator-20251016164239-wfMPqn", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-替身悲歌解说", "id": "narrator-20251016164259-uZELkl", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-力量诅咒解说", "id": "narrator-20251027094046-bCETIG", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-天选之人解说", "id": "narrator-20251027094101-SjLFeA", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-跌落神坛解说", "id": "narrator-20251027094142-SRepnG", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-局中局解说", "id": "narrator-20251016160421-ULNnBv", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-时空信件解说", "id": "narrator-20251110134239-aPENMc", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-拯救末日解说", "id": "narrator-20251113154508-QbYCwS", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-魔法家族解说", "id": "narrator-20251113154927-ASgxrL", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-智商开挂解说", "id": "narrator-20251202161012-GXhovQ", "genre": "奇幻科幻"},
    {"name": "奇幻科幻-逆天改命解说", "id": "narrator-20251202160957-VKVxtY", "genre": "奇幻科幻"},
    # 传奇人物
    {"name": "传奇人物-枭雄末路解说", "id": "narrator-20250929171126-ChYkGc", "genre": "传奇人物"},
    {"name": "传奇人物-人生抉择解说", "id": "narrator-20251124154053-aOUlJQ", "genre": "传奇人物"},
]


@app.command("narration-styles")
def list_narration_styles(
    genre: Optional[str] = typer.Option(None, "--genre", "-g", help="Filter by genre (e.g. 情感人生, 烧脑悬疑, 爆笑喜剧)"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List pre-built narration style templates (learning_model_id).

    Use these instead of running popular-learning. Pick the genre that best
    matches your movie, then pass the ID as learning_model_id in generate-writing
    or fast-writing.

    Available genres: 热血动作, 烧脑悬疑, 励志成长, 爆笑喜剧, 灾难求生,
    悬疑惊悚, 惊悚恐怖, 东方奇谈, 家庭伦理, 情感人生, 奇幻科幻, 传奇人物

    View template previews: https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc
    """
    items = NARRATION_TEMPLATES
    if genre:
        items = [t for t in items if genre in t["genre"]]
        if not items:
            genres = sorted(set(t["genre"] for t in NARRATION_TEMPLATES))
            print_error(f"No templates for genre '{genre}'. Available: {', '.join(genres)}")
            raise typer.Exit(1)
    if json_mode:
        print_json(items)
    else:
        title = f"Narration Styles - {genre}" if genre else f"Narration Styles ({len(items)} templates)"
        columns = [("name", "Template"), ("id", "learning_model_id"), ("genre", "Genre")]
        print_table(items, columns, title=title)
        console.print("\n[dim]View previews: https://ceex7z9m67.feishu.cn/wiki/WLPnwBysairenFkZDbicZOfKnbc[/dim]")


@app.command("templates")
def list_templates(
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List available visual templates for magic-video task."""
    try:
        data = _client().get("/v2/task/commentary/get_magic_templates")
        if json_mode:
            print_json(data)
        else:
            templates = data.get("templates", data.get("data", []))
            if isinstance(templates, list):
                items = [{"name": t.get("name", ""), "description": t.get("description", "")} for t in templates]
                print_table(items, [("name", "Name"), ("description", "Description")], title="Visual Templates")
            else:
                print_dict(data, title="Visual Templates")
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


def _load_json_data(data: str) -> dict:
    """Load JSON data from a string or @file reference."""
    try:
        if data.startswith("@"):
            file_path = Path(data[1:])
            if not file_path.exists():
                print_error(f"File not found: {file_path}")
                raise typer.Exit(1)
            return _json.loads(file_path.read_text())
        return _json.loads(data)
    except _json.JSONDecodeError as e:
        print_error(f"Invalid JSON: {e}")
        raise typer.Exit(1)
