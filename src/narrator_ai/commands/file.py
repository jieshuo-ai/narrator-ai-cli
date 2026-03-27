"""File management commands."""

import mimetypes
from pathlib import Path
from typing import Optional

import typer

from narrator_ai.client import NarratorClient, NarratorAPIError
from narrator_ai.output import (
    print_dict,
    print_error,
    print_info,
    print_json,
    print_success,
    print_table,
)

app = typer.Typer(
    help=(
        "File upload, download, and management.\n\n"
        "Supported formats: .mp4, .mkv, .mov, .mp3, .m4a, .wav, .srt, .jpg, .jpeg, .png\n\n"
        "Upload returns a file_id that can be used as input for task creation."
    ),
)

CATEGORY_MAP = {
    1: "video",
    2: "audio",
    3: "image",
    4: "doc",
    5: "torrent",
    6: "other",
}


def _client() -> NarratorClient:
    return NarratorClient()


@app.command()
def upload(
    file_path: str = typer.Argument(..., help="Local file path to upload"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Upload a local file to cloud storage via presigned URL.

    Three-step process: request presigned URL -> upload to OSS -> confirm callback.
    Returns file_id for use in task creation params (e.g. video_oss_key, srt_oss_key, bgm).
    """
    path = Path(file_path)
    if not path.exists():
        print_error(f"File not found: {file_path}")
        raise typer.Exit(1)

    file_name = path.name
    file_size = path.stat().st_size
    content_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
    client = _client()

    try:
        # Step 1: Get presigned upload URL
        print_info(f"Requesting upload URL for {file_name} ({file_size:,} bytes)...")
        presigned = client.post("/v2/files/upload/presigned-url", json={
            "file_name": file_name,
            "file_size": file_size,
            "content_type": content_type,
        })

        # Step 2: Upload to OSS
        upload_url = presigned["upload_url"]
        print_info("Uploading...")
        client.upload_file(upload_url, str(path), content_type)

        # Step 3: Confirm callback
        print_info("Confirming upload...")
        result = client.post("/v2/files/upload/callback", json={
            "file_id": presigned["file_id"],
            "object_key": presigned["object_key"],
            "upload_status": "success",
            "file_size": file_size,
        })

        output = {
            "file_id": presigned["file_id"],
            "file_name": file_name,
            "file_size": file_size,
            "status": "uploaded",
        }
        print_dict(output, title="Upload Complete", json_mode=json_mode)

    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


@app.command()
def transfer(
    link: Optional[str] = typer.Option(None, help="File link (HTTP URL, Baidu Netdisk share link, or PikPak link)"),
    upload_id: Optional[str] = typer.Option(None, help="Upload ID associated with the file being transferred"),
    type: Optional[str] = typer.Option(None, help="Link type: url=HTTP, baidu=Baidu Netdisk, pikpak=PikPak (auto-detected if omitted)"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Transfer a remote file to cloud storage by link (HTTP, Baidu Netdisk, or PikPak).

    Provide --link to start a transfer. --upload-id and --type are optional.
    Returns upload_id, file_name, file_size, link_type, and error_info.
    """
    if not link and not upload_id:
        print_error("Provide --link to start a transfer.")
        raise typer.Exit(1)

    payload: dict = {}
    if link:
        payload["link"] = link
    if upload_id:
        payload["upload_id"] = upload_id
    if type:
        payload["type"] = type

    try:
        data = _client().post("/v2/files/upload", json=payload)
        if json_mode:
            print_json(data)
        else:
            output = {
                "upload_id": data.get("upload_id", ""),
                "file_name": data.get("file_name", ""),
                "file_size": _format_size(int(data.get("file_size", 0))),
                "link_type": data.get("link_type", ""),
            }
            if data.get("error_info"):
                output["error_info"] = data["error_info"]
            print_dict(output, title="Transfer Status", json_mode=False)
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


@app.command()
def download(
    file_id: str = typer.Argument(..., help="File ID to get download URL for"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Get a presigned download URL for a file. URL expires after a limited time."""
    try:
        data = _client().post("/v2/files/download/presigned-url", json={
            "file_id": file_id,
        })
        if json_mode:
            print_json(data)
        else:
            print_dict({
                "file_id": data.get("file_id"),
                "file_name": data.get("file_name"),
                "download_url": data.get("download_url"),
                "expires_in": f"{data.get('expires_in', 0)} seconds",
            }, title="Download URL")
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


@app.command("list")
def list_files(
    page: int = typer.Option(1, help="Page number"),
    page_size: int = typer.Option(10, help="Items per page"),
    search: Optional[str] = typer.Option(None, help="Filter by filename (substring match)"),
    order_by: str = typer.Option("completed_time", help="Sort field: completed_time, created_at, file_size"),
    order: str = typer.Option("desc", help="Sort order: asc or desc"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List uploaded files with pagination and search."""
    params = {
        "page": page,
        "page_size": page_size,
        "order_by": order_by,
        "order": order,
    }
    if search:
        params["search"] = search

    try:
        data = _client().get("/v2/files/user/filelist", params=params)
        if json_mode:
            print_json(data)
        else:
            items = data.get("data", data.get("items", []))
            for item in items:
                cat = item.get("category")
                item["category_name"] = CATEGORY_MAP.get(cat, str(cat))
                size = int(item.get("file_size", 0))
                item["size_display"] = _format_size(size)
            total = data.get("total", 0)
            per_page = data.get("limit", data.get("page_size", page_size))
            total_pages = max(1, -(-total // per_page))
            columns = [
                ("file_id", "File ID"),
                ("file_name", "Name"),
                ("size_display", "Size"),
                ("category_name", "Type"),
                ("created_at", "Created"),
            ]
            print_table(items, columns, title=f"Files (page {page}/{total_pages}, total: {total})")
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


@app.command()
def info(
    file_id: str = typer.Argument(..., help="File ID to inspect"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Get detailed file information: name, path, size, category, status, timestamps."""
    try:
        data = _client().get("/v2/files/get_file_information", params={"file_id": file_id})
        print_dict(data, title="File Info", json_mode=json_mode)
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


@app.command()
def storage(
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show storage usage: used size, max size, file count, usage percentage."""
    try:
        data = _client().get("/v2/files/user/storage_usage")
        if not json_mode and isinstance(data, dict):
            data["used_display"] = _format_size(data.get("used_size", 0))
            data["max_display"] = _format_size(data.get("max_size", 0))
            data["usage_display"] = f"{data.get('usage_percentage', 0):.1f}%"
        print_dict(data, title="Storage Usage", json_mode=json_mode)
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


@app.command("delete")
def delete_file(
    file_id: str = typer.Argument(..., help="File ID to delete"),
    json_mode: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Delete a file from cloud storage. This action is irreversible."""
    try:
        data = _client().delete(f"/v2/files/user/files/{file_id}")
        if json_mode:
            print_json(data or {"status": "deleted", "file_id": file_id})
        else:
            print_success(f"File {file_id} deleted.")
    except NarratorAPIError as e:
        print_error(e.message, e.code)
        raise typer.Exit(1)


def _format_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
