#!/usr/bin/env bash
# narrator-ai-cli installer
# Usage: curl -fsSL https://raw.githubusercontent.com/jieshuo-ai/narrator-ai-cli/main/install.sh | bash
set -euo pipefail

REPO="https://github.com/jieshuo-ai/narrator-ai-cli.git"
INSTALL_DIR="${NARRATOR_INSTALL_DIR:-$HOME/.narrator-ai-cli}"

info()  { printf "\033[34m[info]\033[0m  %s\n" "$*"; }
ok()    { printf "\033[32m[ok]\033[0m    %s\n" "$*"; }
err()   { printf "\033[31m[error]\033[0m %s\n" "$*" >&2; exit 1; }

# Check Python 3.10+
check_python() {
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)
            major=$(echo "$ver" | cut -d. -f1)
            minor=$(echo "$ver" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
                PYTHON="$cmd"
                return 0
            fi
        fi
    done
    err "Python 3.10+ is required but not found. Install it first."
}

# Check for uv or pip
check_installer() {
    if command -v uv &>/dev/null; then
        INSTALLER="uv"
    elif command -v pip3 &>/dev/null; then
        INSTALLER="pip3"
    elif command -v pip &>/dev/null; then
        INSTALLER="pip"
    else
        err "Neither uv nor pip found. Install one first."
    fi
}

info "Checking dependencies..."
check_python
check_installer
ok "Python: $($PYTHON --version), Installer: $INSTALLER"

# Clone or update repo
if [ -d "$INSTALL_DIR" ]; then
    info "Updating existing installation at $INSTALL_DIR..."
    cd "$INSTALL_DIR"
    git pull --ff-only origin main 2>/dev/null || git pull --ff-only origin master 2>/dev/null || true
else
    info "Cloning $REPO..."
    git clone "$REPO" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Create venv and install
info "Creating virtual environment..."
$PYTHON -m venv "$INSTALL_DIR/.venv"

info "Installing narrator-ai-cli..."
if [ "$INSTALLER" = "uv" ]; then
    uv pip install --python "$INSTALL_DIR/.venv/bin/python" -e "$INSTALL_DIR"
else
    "$INSTALL_DIR/.venv/bin/pip" install -e "$INSTALL_DIR"
fi

# Create symlink in PATH
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
ln -sf "$INSTALL_DIR/.venv/bin/narrator-ai-cli" "$BIN_DIR/narrator-ai-cli"

# Check if BIN_DIR is in PATH
if ! echo "$PATH" | tr ':' '\n' | grep -qx "$BIN_DIR"; then
    SHELL_RC=""
    case "$(basename "$SHELL")" in
        zsh)  SHELL_RC="$HOME/.zshrc" ;;
        bash) SHELL_RC="$HOME/.bashrc" ;;
    esac
    if [ -n "$SHELL_RC" ]; then
        if ! grep -q "$BIN_DIR" "$SHELL_RC" 2>/dev/null; then
            echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_RC"
            info "Added $BIN_DIR to PATH in $SHELL_RC"
        fi
    fi
    export PATH="$BIN_DIR:$PATH"
fi

# Install Claude Code skill (global)
SKILL_SRC="$INSTALL_DIR/.claude/skills/narrator-ai/SKILL.md"
SKILL_DST="$HOME/.claude/skills/narrator-ai/SKILL.md"
if [ -f "$SKILL_SRC" ]; then
    mkdir -p "$(dirname "$SKILL_DST")"
    cp -f "$SKILL_SRC" "$SKILL_DST"
    ok "Claude Code skill installed at $SKILL_DST"
else
    info "Skill file not found, skipping Claude Code integration."
fi

ok "narrator-ai-cli installed successfully!"
echo ""
info "Quick start:"
echo "  narrator-ai-cli config init"
echo "  narrator-ai-cli --help"
echo ""
if [ -f "$SKILL_DST" ]; then
    info "Claude Code skill is available globally. Claude can now use narrator-ai-cli in any project."
fi
if ! echo "$PATH" | tr ':' '\n' | grep -qx "$BIN_DIR"; then
    info "Restart your shell or run: export PATH=\"$BIN_DIR:\$PATH\""
fi
