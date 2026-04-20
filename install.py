#!/usr/bin/env python3
"""
narrator-ai-cli universal installer
Works on Windows (CMD / PowerShell), macOS, and Linux — no shell-specific tools required.

Usage:
  macOS / Linux:
    curl -fsSL https://raw.githubusercontent.com/NarratorAI-Studio/narrator-ai-cli/main/install.py | python3

  Windows (CMD or PowerShell):
    python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/NarratorAI-Studio/narrator-ai-cli/main/install.py').read())"

Prerequisites: Python 3.10+, Git
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# ── Platform detection ────────────────────────────────────────────────────────
IS_WINDOWS = sys.platform == "win32"

# ── Config ────────────────────────────────────────────────────────────────────
REPO        = "https://github.com/NarratorAI-Studio/narrator-ai-cli.git"
HOME        = Path.home()
INSTALL_DIR = Path(os.environ.get("NARRATOR_INSTALL_DIR", HOME / ".narrator-ai-cli"))
VENV_DIR    = INSTALL_DIR / ".venv"

# ── Colored output (works on Windows 10+ and all Unix terminals) ──────────────
def _c(code: str, msg: str) -> str:
    """Wrap msg in ANSI color code if stdout is a tty."""
    if sys.stdout.isatty():
        return f"\033[{code}m{msg}\033[0m"
    return msg

def info(msg: str) -> None:
    print(_c("36", "[info]  ") + msg)

def ok(msg: str) -> None:
    print(_c("32", "[ok]    ") + msg)

def err(msg: str) -> None:
    print(_c("31", "[error] ") + msg, file=sys.stderr)
    sys.exit(1)

# ── Check Python version ──────────────────────────────────────────────────────
if sys.version_info < (3, 10):
    err(f"Python 3.10+ is required, but found {sys.version}.\n"
        "Install it from https://www.python.org/downloads/ and retry.")

# ── Check Git ─────────────────────────────────────────────────────────────────
if not shutil.which("git"):
    if IS_WINDOWS:
        err("Git is not found. Install Git for Windows from https://git-scm.com/download/win and retry.")
    else:
        err("Git is not found. Install it via your package manager (e.g. brew install git) and retry.")

# ── Check uv (optional fast installer, Unix only) ────────────────────────────
HAS_UV = not IS_WINDOWS and shutil.which("uv") is not None

info("Checking dependencies...")
ok(f"Python: {sys.version.split()[0]}" + (" | uv detected" if HAS_UV else ""))

# ── Clone or update repo ──────────────────────────────────────────────────────
if INSTALL_DIR.exists():
    info(f"Updating existing installation at {INSTALL_DIR} ...")
    result = subprocess.run(
        ["git", "-C", str(INSTALL_DIR), "pull", "--ff-only", "origin", "main"],
        capture_output=True,
    )
    if result.returncode != 0:
        subprocess.run(
            ["git", "-C", str(INSTALL_DIR), "pull", "--ff-only", "origin", "master"],
            capture_output=True,
        )
else:
    info(f"Cloning {REPO} ...")
    subprocess.run(["git", "clone", REPO, str(INSTALL_DIR)], check=True)

# ── Create virtual environment ────────────────────────────────────────────────
info("Creating virtual environment...")
subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)

# ── Install package ───────────────────────────────────────────────────────────
info("Installing narrator-ai-cli...")
if HAS_UV:
    venv_python = str(VENV_DIR / "bin" / "python")
    subprocess.run(
        ["uv", "pip", "install", "--python", venv_python, "-e", str(INSTALL_DIR)],
        check=True,
    )
elif IS_WINDOWS:
    pip_exe = VENV_DIR / "Scripts" / "pip.exe"
    result = subprocess.run([str(pip_exe), "install", "--quiet", "-e", str(INSTALL_DIR)])
    if result.returncode != 0:
        err("pip install failed.")
else:
    pip_exe = VENV_DIR / "bin" / "pip"
    subprocess.run([str(pip_exe), "install", "-e", str(INSTALL_DIR)], check=True)

ok("narrator-ai-cli installed.")

# ── Add to PATH ───────────────────────────────────────────────────────────────
if IS_WINDOWS:
    # Modify user PATH via Windows Registry (no PowerShell needed)
    scripts_dir = VENV_DIR / "Scripts"
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS
        )
        try:
            current_path, reg_type = winreg.QueryValueEx(key, "PATH")
        except FileNotFoundError:
            current_path, reg_type = "", winreg.REG_EXPAND_SZ

        if str(scripts_dir) not in current_path:
            new_path = f"{scripts_dir};{current_path}" if current_path else str(scripts_dir)
            winreg.SetValueEx(key, "PATH", 0, reg_type, new_path)
            # Also update the current process environment
            os.environ["PATH"] = f"{scripts_dir};{os.environ.get('PATH', '')}"
            info(f"Added {scripts_dir} to user PATH (takes effect in new terminals).")
        else:
            info(f"{scripts_dir} is already in PATH.")
        winreg.CloseKey(key)
    except Exception as e:
        info(f"Could not update PATH automatically: {e}")
        info(f"Manually add this to your PATH: {scripts_dir}")
else:
    # Create symlink in ~/.local/bin
    bin_dir = HOME / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    symlink = bin_dir / "narrator-ai-cli"
    if symlink.is_symlink() or symlink.exists():
        symlink.unlink()
    symlink.symlink_to(VENV_DIR / "bin" / "narrator-ai-cli")

    # Ensure ~/.local/bin is in PATH (write to shell RC if needed)
    current_path_dirs = os.environ.get("PATH", "").split(":")
    if str(bin_dir) not in current_path_dirs:
        shell_name = Path(os.environ.get("SHELL", "")).name
        rc_map = {"zsh": HOME / ".zshrc", "bash": HOME / ".bashrc"}
        shell_rc = rc_map.get(shell_name)
        export_line = f'export PATH="{bin_dir}:$PATH"'
        if shell_rc:
            rc_text = shell_rc.read_text() if shell_rc.exists() else ""
            if str(bin_dir) not in rc_text:
                with open(shell_rc, "a") as f:
                    f.write(f"\n# Added by narrator-ai-cli installer\n{export_line}\n")
                info(f"Added {bin_dir} to PATH in {shell_rc}")
        os.environ["PATH"] = f"{bin_dir}:{os.environ.get('PATH', '')}"
    else:
        info(f"{bin_dir} is already in PATH.")

# ── Install Claude Code skill ─────────────────────────────────────────────────
SKILL_SRC = INSTALL_DIR / ".claude" / "skills" / "SKILL.md"
SKILL_DST = HOME / ".claude" / "skills" / "narrator-ai" / "SKILL.md"
if SKILL_SRC.exists():
    SKILL_DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SKILL_SRC, SKILL_DST)
    imgs_src = SKILL_SRC.parent / "imgs"
    imgs_dst = SKILL_DST.parent / "imgs"
    if imgs_src.exists():
        if imgs_dst.exists():
            shutil.rmtree(imgs_dst)
        shutil.copytree(imgs_src, imgs_dst)
    ok(f"Claude Code skill installed at {SKILL_DST}")
else:
    info("Skill file not found, skipping Claude Code integration.")

# ── Done ──────────────────────────────────────────────────────────────────────
ok("narrator-ai-cli installed successfully!")
print()
info("Quick start:")
print("  narrator-ai-cli config init")
print("  narrator-ai-cli --help")
print()
if SKILL_DST.exists():
    info("Claude Code skill is available globally. Claude can now use narrator-ai-cli in any project.")
if IS_WINDOWS:
    info("Note: Open a new terminal for the PATH change to take effect.")
else:
    info("Note: Restart your shell or run: source ~/.zshrc (or ~/.bashrc) for PATH to take effect.")
