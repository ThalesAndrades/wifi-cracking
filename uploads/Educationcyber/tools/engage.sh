#!/bin/bash
# engage.sh — run the safe web recon and consolidate everything into ONE HTML
# report. Non-destructive (delegates to web-recon.sh). Authorized targets only.
#
# Usage: ./engage.sh <url-or-domain> [-o OUTDIR] [-y]
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GREEN='\033[0;32m'; RED='\033[0;31m'; BOLD='\033[1m'; RST='\033[0m'

TARGET=""; OUTDIR=""; YES=0
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) echo "Usage: $0 <url-or-domain> [-o OUTDIR] [-y]"; exit 0 ;;
    -o) OUTDIR="${2:-}"; shift 2 ;;
    -y) YES=1; shift ;;
    *) TARGET="$1"; shift ;;
  esac
done
[ -n "$TARGET" ] || { echo -e "${RED}Missing target.${RST}"; exit 1; }
[[ "$TARGET" =~ ^https?:// ]] || TARGET="http://$TARGET"
HOST="$(printf '%s' "$TARGET" | sed -E 's#^https?://##; s#/.*$##; s#:.*$##')"
: "${OUTDIR:=engage-${HOST}-$(date +%Y%m%d-%H%M%S)}"

# Run the recon (it has its own authorization gate; pass -y through)
RECON_ARGS=("$TARGET" -o "$OUTDIR")
[ "$YES" -eq 1 ] && RECON_ARGS+=(-y)
"$HERE/web-recon.sh" "${RECON_ARGS[@]}" || { echo -e "${RED}recon aborted${RST}"; exit 1; }

# --- consolidate into a single HTML report ---------------------------------
REPORT="$OUTDIR/report.html"
esc() { sed -e 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g'; }
section() {  # section "Title" file
  local title="$1" file="$2"
  {
    printf '<h2>%s</h2>\n' "$title"
    if [ -s "$file" ]; then printf '<pre>'; esc < "$file"; printf '</pre>\n'
    else printf '<p class="empty">no data / not run</p>\n'; fi
  } >> "$REPORT"
}

cat > "$REPORT" <<HTML
<!DOCTYPE html><html><head><meta charset="utf-8"><title>Recon report — ${HOST}</title>
<style>
 body{background:#0f1115;color:#e6e6e6;font-family:"Courier New",monospace;margin:0 auto;max-width:1000px;padding:24px}
 h1{color:#4da3ff} h2{color:#7CFC00;border-bottom:1px solid #333;padding-top:18px}
 pre{background:#1b1e25;padding:12px;border-radius:6px;overflow:auto;font-size:13px;white-space:pre-wrap}
 .empty{color:#888} .meta{color:#aaa;font-size:13px} a{color:#4da3ff}
</style></head><body>
<h1>🔎 Recon Report</h1>
<p class="meta"><b>Target:</b> ${TARGET}<br><b>Host:</b> ${HOST}<br><b>Date:</b> $(date)</p>
<p class="meta">Non-destructive reconnaissance. Authorized testing only.</p>
HTML

section "DNS"                 "$OUTDIR/dns.txt"
section "Ports & services (nmap)" "$OUTDIR/nmap.txt"
section "Technology (whatweb)" "$OUTDIR/whatweb.txt"
section "TLS (sslscan)"       "$OUTDIR/sslscan.txt"
section "Server config (nikto)" "$OUTDIR/nikto.txt"
section "Exposures/CVEs (nuclei)" "$OUTDIR/nuclei.txt"

echo "</body></html>" >> "$REPORT"
echo -e "${GREEN}${BOLD}Consolidated report:${RST} ${BOLD}$REPORT${RST}"
