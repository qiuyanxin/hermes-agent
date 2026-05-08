#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FLYCTL_BIN="${FLYCTL_BIN:-flyctl}"
FLY_CONFIG_PATH="${FLY_CONFIG_PATH:-$ROOT_DIR/fly.toml}"
FLY_REGION="${FLY_REGION:-nrt}"
FLY_VOLUME_NAME="${FLY_VOLUME_NAME:-hermes_data}"
FLY_VOLUME_SIZE_GB="${FLY_VOLUME_SIZE_GB:-10}"
FLY_ORG="${FLY_ORG:-}"

if ! command -v "$FLYCTL_BIN" >/dev/null 2>&1; then
  echo "Error: flyctl not found in PATH."
  exit 1
fi

if [[ ! -f "$FLY_CONFIG_PATH" ]]; then
  echo "Error: fly config not found at $FLY_CONFIG_PATH"
  exit 1
fi

APP_NAME="${FLY_APP_NAME:-$(python - <<'PY' "$FLY_CONFIG_PATH"
from pathlib import Path
import sys

for line in Path(sys.argv[1]).read_text().splitlines():
    stripped = line.strip()
    if stripped.startswith("app ="):
        value = stripped.split("=", 1)[1].strip().strip('"').strip("'")
        if value:
            print(value)
            break
else:
    raise SystemExit("Unable to determine app name from fly.toml")
PY
)}"

load_dotenv_value() {
  local key="$1"
  python - <<'PY' "$ROOT_DIR/.env" "$key"
from pathlib import Path
import sys

env_path = Path(sys.argv[1])
target = sys.argv[2]

if not env_path.exists():
    raise SystemExit(1)

for raw_line in env_path.read_text(errors="ignore").splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, value = line.split("=", 1)
    if key.strip() != target:
        continue
    value = value.strip().strip('"').strip("'")
    print(value)
    break
else:
    raise SystemExit(1)
PY
}

OPENROUTER_API_KEY_VALUE="${OPENROUTER_API_KEY:-}"
if [[ -z "$OPENROUTER_API_KEY_VALUE" ]]; then
  OPENROUTER_API_KEY_VALUE="$(load_dotenv_value OPENROUTER_API_KEY || true)"
fi

if [[ -z "$OPENROUTER_API_KEY_VALUE" ]]; then
  echo "Error: OPENROUTER_API_KEY is required. Export it or add it to $ROOT_DIR/.env"
  exit 1
fi

API_SERVER_KEY_VALUE="${API_SERVER_KEY:-$(python - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
)}"

echo "Using Fly app: $APP_NAME"
echo "Using region: $FLY_REGION"

if ! "$FLYCTL_BIN" apps show "$APP_NAME" >/dev/null 2>&1; then
  echo "Creating Fly app..."
  if [[ -n "$FLY_ORG" ]]; then
    "$FLYCTL_BIN" apps create "$APP_NAME" --org "$FLY_ORG"
  else
    "$FLYCTL_BIN" apps create "$APP_NAME"
  fi
fi

if ! "$FLYCTL_BIN" volumes list -a "$APP_NAME" | awk 'NR>1 {print $1}' | grep -qx "$FLY_VOLUME_NAME"; then
  echo "Creating Fly volume..."
  "$FLYCTL_BIN" volumes create "$FLY_VOLUME_NAME" \
    --region "$FLY_REGION" \
    --size "$FLY_VOLUME_SIZE_GB" \
    --yes \
    -a "$APP_NAME"
fi

echo "Setting Fly secrets..."
"$FLYCTL_BIN" secrets set \
  OPENROUTER_API_KEY="$OPENROUTER_API_KEY_VALUE" \
  API_SERVER_KEY="$API_SERVER_KEY_VALUE" \
  -a "$APP_NAME"

echo
echo "API_SERVER_KEY for clients:"
echo "$API_SERVER_KEY_VALUE"
echo

echo "Deploying..."
"$FLYCTL_BIN" deploy --config "$FLY_CONFIG_PATH" -a "$APP_NAME" --yes
