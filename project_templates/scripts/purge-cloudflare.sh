#!/usr/bin/env bash
# purge-cloudflare.sh - Purge Cloudflare cache for the current repo/site.
#
# WHY: HTML behind Cloudflare can stay stale after a deploy even when asset URLs
# are cache-busted. Run this when a repo needs a selective or full cache purge.
#
# USAGE:
#   ./scripts/purge-cloudflare.sh --everything
#   ./scripts/purge-cloudflare.sh --url https://example.com/
#   ./scripts/purge-cloudflare.sh --url https://example.com/ --url https://example.com/about/
#   ./scripts/purge-cloudflare.sh --everything --repo-root /path/to/repo
#   ./scripts/purge-cloudflare.sh --everything --use-reserve-token
#
# READS (never printed), in order:
#   1. Explicit flags such as --api-token, --zone-id, --domain, --env-file
#   2. Repo .env (default: <repo>/.env, then <repo>/infra/.env)
#   3. Process environment variables
#   4. Reserve token file only when --use-reserve-token is passed
#
# Expected keys:
#   CLOUDFLARE_API_TOKEN   (required; aliases CF_API_TOKEN, CLOUDFLARE_TOKEN)
#   CLOUDFLARE_ZONE_ID     (optional; aliases CF_ZONE_ID, ZONE_ID)
#   SITE_DOMAIN            (optional; fallback from SITE_URL, BASE_URL, PUBLIC_BASE_URL)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE=""
DOMAIN=""
ZONE_ID=""
API_TOKEN=""
USE_RESERVE_TOKEN=0
RESERVE_TOKEN_FILE=""
EVERYTHING=0
URLS=()

usage() {
  cat <<'EOF'
Usage:
  purge-cloudflare.sh --everything [--repo-root PATH] [--env-file PATH]
  purge-cloudflare.sh --url URL [--url URL ...] [--repo-root PATH] [--env-file PATH]

Options:
  --everything              Purge everything in the zone.
  --url URL                 Purge one URL. Repeat for multiple URLs.
  --env-file PATH           Read repo values from a specific .env file.
  --repo-root PATH          Resolve .env relative to another repo root.
  --domain DOMAIN           Override SITE_DOMAIN.
  --zone-id ID              Override CLOUDFLARE_ZONE_ID.
  --api-token TOKEN         Override CLOUDFLARE_API_TOKEN.
  --use-reserve-token       Allow fallback to <OBSIDIAN_VAULT_PATH>/_keys/Cloudflare.md.
  --reserve-token-file PATH Override the reserve token file path.
  --help                    Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --everything)
      EVERYTHING=1
      shift
      ;;
    --url)
      [[ $# -ge 2 ]] || { echo "Missing value for --url." >&2; exit 1; }
      URLS+=("$2")
      shift 2
      ;;
    --env-file)
      [[ $# -ge 2 ]] || { echo "Missing value for --env-file." >&2; exit 1; }
      ENV_FILE="$2"
      shift 2
      ;;
    --repo-root)
      [[ $# -ge 2 ]] || { echo "Missing value for --repo-root." >&2; exit 1; }
      REPO_ROOT="$2"
      shift 2
      ;;
    --domain)
      [[ $# -ge 2 ]] || { echo "Missing value for --domain." >&2; exit 1; }
      DOMAIN="$2"
      shift 2
      ;;
    --zone-id)
      [[ $# -ge 2 ]] || { echo "Missing value for --zone-id." >&2; exit 1; }
      ZONE_ID="$2"
      shift 2
      ;;
    --api-token)
      [[ $# -ge 2 ]] || { echo "Missing value for --api-token." >&2; exit 1; }
      API_TOKEN="$2"
      shift 2
      ;;
    --use-reserve-token)
      USE_RESERVE_TOKEN=1
      shift
      ;;
    --reserve-token-file)
      [[ $# -ge 2 ]] || { echo "Missing value for --reserve-token-file." >&2; exit 1; }
      RESERVE_TOKEN_FILE="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ "$EVERYTHING" -eq 1 && "${#URLS[@]}" -gt 0 ]]; then
  echo "Choose either --everything or one or more --url flags." >&2
  exit 1
fi

if [[ "$EVERYTHING" -eq 0 && "${#URLS[@]}" -eq 0 ]]; then
  echo "Pass --everything or at least one --url flag." >&2
  exit 1
fi

read_key_file_value() {
  local file_path="$1"
  local key="$2"

  if [[ -z "$file_path" || ! -f "$file_path" ]]; then
    return 1
  fi

  grep -E "^[[:space:]]*${key}[[:space:]]*=" "$file_path" | tail -n1 | cut -d= -f2- \
    | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//"
}

get_config_value() {
  local explicit_value="$1"
  shift

  if [[ -n "$explicit_value" ]]; then
    printf '%s' "$explicit_value"
    return 0
  fi

  local key value
  for key in "$@"; do
    value="$(read_key_file_value "${ENV_FILE:-}" "$key" || true)"
    if [[ -n "$value" ]]; then
      printf '%s' "$value"
      return 0
    fi
  done

  for key in "$@"; do
    value="$(printenv "$key" 2>/dev/null || true)"
    if [[ -n "$value" ]]; then
      printf '%s' "$value"
      return 0
    fi
  done

  return 0
}

get_domain_from_url() {
  local value="$1"
  if [[ -z "$value" ]]; then
    return 0
  fi

  value="${value#http://}"
  value="${value#https://}"
  value="${value%%/*}"
  printf '%s' "$value"
}

if [[ -z "$ENV_FILE" ]]; then
  if [[ -f "$REPO_ROOT/.env" ]]; then
    ENV_FILE="$REPO_ROOT/.env"
  elif [[ -f "$REPO_ROOT/infra/.env" ]]; then
    ENV_FILE="$REPO_ROOT/infra/.env"
  elif [[ -f "$SCRIPT_DIR/.env" ]]; then
    ENV_FILE="$SCRIPT_DIR/.env"
  fi
fi

API_TOKEN="$(get_config_value "$API_TOKEN" CLOUDFLARE_API_TOKEN CF_API_TOKEN CLOUDFLARE_TOKEN)"
if [[ -z "$API_TOKEN" && "$USE_RESERVE_TOKEN" -eq 1 ]]; then
  if [[ -z "$RESERVE_TOKEN_FILE" ]]; then
    VAULT_PATH="$(get_config_value "" OBSIDIAN_VAULT_PATH)"
    if [[ -n "$VAULT_PATH" ]]; then
      RESERVE_TOKEN_FILE="$VAULT_PATH/_keys/Cloudflare.md"
    fi
  fi
  API_TOKEN="$(read_key_file_value "${RESERVE_TOKEN_FILE:-}" CLOUDFLARE_API_TOKEN || true)"
fi

DOMAIN="$(get_config_value "$DOMAIN" SITE_DOMAIN)"
if [[ -z "$DOMAIN" ]]; then
  for url_key in SITE_URL BASE_URL PUBLIC_BASE_URL; do
    candidate="$(get_config_value "" "$url_key")"
    DOMAIN="$(get_domain_from_url "$candidate")"
    [[ -n "$DOMAIN" ]] && break
  done
fi
ZONE_ID="$(get_config_value "$ZONE_ID" CLOUDFLARE_ZONE_ID CF_ZONE_ID ZONE_ID)"

if [[ -z "$DOMAIN" ]]; then
  echo "No domain found. Set SITE_DOMAIN in .env or pass --domain." >&2
  exit 1
fi

if [[ -z "$API_TOKEN" ]]; then
  echo "No Cloudflare API token found. Set CLOUDFLARE_API_TOKEN in repo .env, pass --api-token, or use --use-reserve-token." >&2
  exit 1
fi

AUTH="Authorization: Bearer $API_TOKEN"

if [[ -z "$ZONE_ID" ]]; then
  echo "Looking up zone id for $DOMAIN ..."
  RESP="$(curl -fsS -H "$AUTH" "https://api.cloudflare.com/client/v4/zones?name=$DOMAIN")"
  ZONE_ID="$(printf '%s' "$RESP" | grep -oE '"id":"[a-f0-9]{32}"' | head -n1 | cut -d'"' -f4)"
  if [[ -z "$ZONE_ID" ]]; then
    echo "Could not resolve zone for $DOMAIN. Set CLOUDFLARE_ZONE_ID in .env or pass --zone-id." >&2
    exit 1
  fi
fi

if [[ "$EVERYTHING" -eq 1 ]]; then
  BODY='{"purge_everything":true}'
  WHAT="EVERYTHING"
else
  escaped_urls=()
  for url in "${URLS[@]}"; do
    escaped_urls+=("\"${url//\"/\\\"}\"")
  done
  BODY="{\"files\":[$(IFS=,; echo "${escaped_urls[*]}")]}"
  WHAT="${#URLS[@]} URL(s)"
fi

echo "Purging $WHAT on zone $ZONE_ID ($DOMAIN) ..."
RESP="$(curl -fsS -X POST -H "$AUTH" -H "Content-Type: application/json" \
  --data "$BODY" "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache")"

if printf '%s' "$RESP" | grep -q '"success":true'; then
  echo "Cloudflare cache purge OK."
else
  echo "Cloudflare cache purge FAILED." >&2
  printf '%s\n' "$RESP" >&2
  exit 1
fi
