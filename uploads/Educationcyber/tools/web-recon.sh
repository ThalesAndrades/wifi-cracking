#!/bin/bash
# web-recon.sh — Safe, NON-destructive web reconnaissance for a site YOU own.
#
# Orchestrates passive/light tools only:
#   dig · nmap (info scripts) · whatweb · sslscan · nikto · nuclei
#
# It deliberately does NOT brute force, NOT fuzz, NOT run DoS/intrusive
# checks. Use ONLY against systems you own or are explicitly authorized to
# test (a VPS/dedicated server of yours — never shared hosting).
#
# Usage:
#   ./web-recon.sh <url-or-domain> [-o OUTDIR] [-y]
#     -o OUTDIR   output directory (default: webrecon-<host>-<timestamp>)
#     -y          skip the authorization confirmation prompt
set -uo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; BLUE='\033[0;34m'; BOLD='\033[1m'; RST='\033[0m'

usage() { grep '^#' "$0" | sed 's/^# \{0,1\}//' | head -n 17; exit "${1:-0}"; }

# --- parse args ------------------------------------------------------------
TARGET=""; OUTDIR=""; ASSUME_YES=0
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage 0 ;;
    -o)
      [ $# -ge 2 ] && [ -n "${2:-}" ] || { echo "Option -o requires a value." >&2; usage 1; }
      OUTDIR="$2"; shift 2 ;;
    -y) ASSUME_YES=1; shift ;;
    -*) echo "Unknown option: $1" >&2; usage 1 ;;
    *)  TARGET="$1"; shift ;;
  esac
done
[ -n "$TARGET" ] || { echo -e "${RED}Missing target.${RST}"; usage 1; }

# --- normalize target ------------------------------------------------------
# HOST = bare hostname/IP ; URL = full http(s) URL
if [[ "$TARGET" =~ ^https?:// ]]; then
  URL="$TARGET"
else
  URL="http://$TARGET"
fi
# Keep host and (optional) explicit port separate so we can scan the real port.
# Handle bracketed IPv6 ([::1]:8080) as well as host:port, and validate the port.
AUTHORITY="$(printf '%s' "$URL" | sed -E 's#^https?://##; s#/.*$##')"
HOST=""; PORT=""
if [[ "$AUTHORITY" =~ ^\[([0-9A-Fa-f:]+)\](:([0-9]{1,5}))?$ ]]; then
  HOST="${BASH_REMATCH[1]}"; PORT="${BASH_REMATCH[3]}"
elif [[ "$AUTHORITY" =~ ^([^:]+)(:([0-9]{1,5}))?$ ]]; then
  HOST="${BASH_REMATCH[1]}"; PORT="${BASH_REMATCH[3]}"
else
  echo -e "${RED}Invalid target URL authority: ${AUTHORITY}${RST}" >&2; usage 1
fi
if [ -n "$PORT" ] && { [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; }; then
  echo -e "${RED}Invalid port in URL: ${PORT}${RST}" >&2; usage 1
fi
SCHEME="$(printf '%s' "$URL" | grep -oP '^https?')"

: "${OUTDIR:=webrecon-${HOST}-$(date +%Y%m%d-%H%M%S)}"

# --- authorization gate ----------------------------------------------------
echo -e "${BOLD}Target:${RST} $URL   ${BOLD}Host:${RST} $HOST"
echo -e "${BOLD}Output:${RST} $OUTDIR"
if [ "$ASSUME_YES" -ne 1 ]; then
  echo -e "${RED}Only scan systems you own or are authorized to test.${RST}"
  read -r -p "Do you confirm you are authorized to scan ${HOST}? [y/N]: " ans
  case "$ans" in y|Y|yes|YES) ;; *) echo "Aborted."; exit 1 ;; esac
fi
mkdir -p "$OUTDIR"

have() { command -v "$1" >/dev/null 2>&1; }
step() { echo -e "\n${BLUE}+ -- --=[ $* ]${RST}"; }
skip() { echo -e "${RED}skipped: $1 not installed${RST}"; }

# --- 1. DNS ----------------------------------------------------------------
step "1/6 DNS resolution (dig)"
if have dig; then
  dig +noall +answer "$HOST" A "$HOST" AAAA "$HOST" MX | tee "$OUTDIR/dns.txt"
else skip dig; fi

# --- 2. nmap (service detection + SAFE http info scripts) ------------------
step "2/6 Port & service scan (nmap, info scripts only)"
PORTS="80,443,8080,8443,8000,8888"
[ -n "$PORT" ] && PORTS="$PORT,$PORTS"
if have nmap; then
  nmap -Pn -sV -T3 \
    --script http-title,http-headers,http-server-header,ssl-cert \
    -p "$PORTS" \
    -oN "$OUTDIR/nmap.txt" "$HOST" | tail -n +1
else skip nmap; fi

# --- 3. whatweb (technology fingerprint) -----------------------------------
step "3/6 Technology fingerprint (whatweb)"
if have whatweb; then
  if whatweb -a 3 --color=never "$URL" >"$OUTDIR/whatweb.txt" 2>"$OUTDIR/whatweb.err"; then
    cat "$OUTDIR/whatweb.txt"
  else
    echo "whatweb could not run in this environment (see $OUTDIR/whatweb.err)"
  fi
else skip whatweb; fi

# --- 4. sslscan (TLS configuration) ----------------------------------------
TLS_PORT="${PORT:-443}"
if [ "$SCHEME" = "https" ] || { have nc && nc -z -w2 "$HOST" "$TLS_PORT" 2>/dev/null; }; then
  step "4/6 TLS configuration (sslscan)"
  if have sslscan; then
    sslscan --no-colour "${HOST}:${TLS_PORT}" | tee "$OUTDIR/sslscan.txt"
  else skip sslscan; fi
else
  step "4/6 TLS configuration"; echo "no HTTPS detected, skipping"
fi

# --- 5. nikto (server config / exposed files, non-destructive) -------------
step "5/6 Server config & exposed files (nikto, DoS tests disabled)"
if have nikto; then
  # -Tuning x6 disables the DoS test category
  nikto -h "$URL" -Tuning x6 -maxtime 180s -nointeractive \
    -o "$OUTDIR/nikto.txt" 2>&1 | tail -n 20
else skip nikto; fi

# --- 6. nuclei (templated checks; no fuzzing/DoS/brute) --------------------
step "6/6 Known exposures & CVEs (nuclei, safe template set)"
if have nuclei; then
  nuclei -target "$URL" \
    -exclude-tags dos,intrusive,fuzz,fuzzing,brute-force \
    -rate-limit 50 -concurrency 25 -timeout 10 \
    -silent -o "$OUTDIR/nuclei.txt" 2>/dev/null
  if [ -s "$OUTDIR/nuclei.txt" ]; then cat "$OUTDIR/nuclei.txt"; else echo "no findings"; fi
else skip nuclei; fi

# --- summary ---------------------------------------------------------------
echo -e "\n${GREEN}${BOLD}Done.${RST} Results in: ${BOLD}$OUTDIR/${RST}"
find "$OUTDIR" -maxdepth 1 -type f -printf '  - %f\n' | sort
echo -e "${BLUE}Tip:${RST} review findings, fix, then re-run to confirm."
