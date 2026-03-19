"""Config management commands."""

import typer

from narrator_ai.config import CONFIG_FILE, load_config, save_config
from narrator_ai.output import print_dict, print_success

app = typer.Typer(
    help=(
        "Manage CLI configuration.\n\n"
        "Config is stored in ~/.narrator-ai/config.yaml.\n"
        "Server defaults to https://openapi.jieshuo.cn. Only app_key is required.\n"
        "Environment variables NARRATOR_SERVER, NARRATOR_APP_KEY, NARRATOR_TIMEOUT override config values."
    ),
)


@app.command()
def init(
    app_key: str = typer.Option(..., prompt="App Key"),
    timeout: int = typer.Option(30, help="Request timeout in seconds"),
):
    """Initialize configuration. Only app_key is required (server is pre-configured)."""
    cfg = load_config()
    cfg["app_key"] = app_key
    cfg["timeout"] = timeout
    save_config(cfg)
    print_success(f"Config saved to {CONFIG_FILE}")


@app.command()
def show(
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show current configuration (app key is always masked)."""
    cfg = load_config()
    if cfg.get("app_key"):
        key = cfg["app_key"]
        if len(key) > 8:
            cfg["app_key"] = key[:4] + "****" + key[-4:]
        else:
            cfg["app_key"] = "****"
    print_dict(cfg, title="Configuration", json_mode=json)


@app.command("set")
def set_value(
    key: str = typer.Argument(..., help="Config key: server, app_key, timeout"),
    value: str = typer.Argument(..., help="Config value"),
):
    """Set a single configuration value.

    Examples:
      narrator-ai-cli config set app_key your_api_key
      narrator-ai-cli config set timeout 60
    """
    cfg = load_config()
    if key not in ("server", "app_key", "timeout"):
        raise typer.BadParameter(f"Unknown config key: {key}. Valid: server, app_key, timeout")
    if key == "timeout":
        cfg[key] = int(value)
    elif key == "server":
        cfg[key] = value.rstrip("/")
    else:
        cfg[key] = value
    save_config(cfg)
    print_success(f"Set {key} = {value}")
