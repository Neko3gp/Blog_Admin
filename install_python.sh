#!/usr/bin/env bash
# Instala Python 3.12+ con Tcl/Tk 8.6 (necesario para CustomTkinter en macOS)
# y recrea el venv de python_devops.
set -euo pipefail

cd "$(dirname "$0")"
ROOT="$(pwd)/.python"
VENV="python_devops/.venv"

echo "==> Descargando CPython 3.12 (python-build-standalone, arm64/x86_64)..."
ARCH="$(uname -m)"
case "$ARCH" in
  arm64) TARGET="aarch64-apple-darwin" ;;
  x86_64) TARGET="x86_64-apple-darwin" ;;
  *) echo "Arquitectura no soportada: $ARCH"; exit 1 ;;
esac

TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

curl -fsSL "https://api.github.com/repos/astral-sh/python-build-standalone/releases/latest" \
  -o "$TMP/release.json"

python3 - "$TMP/release.json" "$TARGET" "$TMP/url.txt" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
target = sys.argv[2]
out = sys.argv[3]
cands = []
for a in data.get("assets") or []:
    n = a["name"]
    if (target in n and "cpython-3.12." in n and "install_only" in n
            and n.endswith(".tar.gz") and "stripped" not in n):
        cands.append(a)
if not cands:
    raise SystemExit("No se encontró asset CPython 3.12 install_only para " + target)
open(out, "w").write(cands[0]["browser_download_url"])
print("Asset:", cands[0]["name"])
PY

URL="$(cat "$TMP/url.txt")"
echo "==> URL: $URL"
curl -fL --retry 3 -o "$TMP/python.tar.gz" "$URL"

echo "==> Extrayendo en $ROOT ..."
rm -rf "$ROOT"
mkdir -p "$ROOT"
tar -xzf "$TMP/python.tar.gz" -C "$ROOT"

PYBIN="$(find "$ROOT" -type f -name 'python3.12' | head -1)"
if [ -z "$PYBIN" ]; then
  echo "No se encontró python3.12 dentro del tarball"
  find "$ROOT" -maxdepth 4 -type f -name 'python*' | head
  exit 1
fi

echo "==> Python: $PYBIN"
"$PYBIN" -c "import sys; print(sys.version)"
"$PYBIN" -c "import tkinter as tk; print('Tcl/Tk', tk.Tcl().eval('info patchlevel'))"

TCL="$("$PYBIN" -c "import tkinter as tk; print(tk.Tcl().eval('info patchlevel'))")"
case "$TCL" in
  8.5*) echo "ERROR: sigue siendo Tk 8.5 ($TCL). Abortando."; exit 1 ;;
esac

echo "==> Recreando venv en $VENV ..."
rm -rf "$VENV"
"$PYBIN" -m venv "$VENV"
"$VENV/bin/pip" install -U pip
"$VENV/bin/pip" install -r python_devops/requirements.txt customtkinter

echo "==> Verificación final:"
"$VENV/bin/python" -c "import tkinter as tk, customtkinter as ctk; print('Tcl', tk.Tcl().eval('info patchlevel')); print('ctk', ctk.__version__)"

echo ""
echo "Listo. Arranca la GUI con:"
echo "  cd python_devops"
echo "  TK_SILENCE_DEPRECATION=1 .venv/bin/python main_gui.py"
