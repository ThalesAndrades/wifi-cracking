#!/bin/bash
# SessionStart hook for hackerEnv (Claude Code on the web).
# Installs the system dependencies the tool needs so it can be run and
# validated inside the remote session. Safe to run multiple times.
set -uo pipefail

# Only run inside the Claude Code remote/web environment.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

log() { echo "[session-start] $*"; }

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  command -v sudo >/dev/null 2>&1 && SUDO="sudo"
fi

export DEBIAN_FRONTEND=noninteractive

# --- Core runtime dependencies (all available in Ubuntu repos) -------------
# nmap      : port / vulnerability scanning
# hydra     : brute force (ssh/ftp/telnet)
# fping     : IP sweep
# pandoc    : HTML -> DOCX report conversion
# expect    : automated ftp/ssh/telnet login scripts
# tmux      : non-GUI terminal multiplexing used by the tool
# ncrack    : provides /usr/share/ncrack/default.usr user list
# net-tools : provides ifconfig (used for interface IP detection)
# iputils-ping : provides ping (host up/down check)
# iproute2  : provides `ip` (used by the IP sweep to find your address)
# nikto / whatweb / sslscan / dnsutils : used by tools/web-recon.sh
# (shellcheck is installed to statically lint the bash scripts)
APT_PKGS=(nmap hydra fping pandoc expect tmux ncrack net-tools iputils-ping iproute2
          nikto whatweb sslscan dnsutils shellcheck git curl wget unzip)

if command -v apt-get >/dev/null 2>&1; then
  log "Updating apt package index..."
  $SUDO apt-get update -qq || log "WARN: apt-get update failed (continuing)"

  log "Installing dependencies: ${APT_PKGS[*]}"
  if ! $SUDO apt-get install -y -qq "${APT_PKGS[@]}"; then
    log "WARN: bulk install failed, retrying packages individually..."
    for p in "${APT_PKGS[@]}"; do
      $SUDO apt-get install -y -qq "$p" || log "WARN: could not install $p"
    done
  fi
else
  log "WARN: apt-get not found; skipping system package install"
fi

# --- nmap NSE vulnerability scripts (best effort) --------------------------
NSE_DIR="/usr/share/nmap/scripts"
if [ -d "$NSE_DIR" ]; then
  if [ ! -d "$NSE_DIR/nmap-vulners" ]; then
    log "Cloning nmap-vulners..."
    $SUDO git clone --depth 1 https://github.com/vulnersCom/nmap-vulners.git \
      "$NSE_DIR/nmap-vulners" >/dev/null 2>&1 || log "WARN: nmap-vulners clone failed"
  fi
  if [ ! -d "$NSE_DIR/vulscan" ]; then
    log "Cloning vulscan..."
    $SUDO git clone --depth 1 https://github.com/scipag/vulscan.git \
      "$NSE_DIR/vulscan" >/dev/null 2>&1 || log "WARN: vulscan clone failed"
  fi
  if command -v nmap >/dev/null 2>&1; then
    $SUDO nmap --script-updatedb >/dev/null 2>&1 || true
  fi
fi

# --- Metasploit Framework (best effort; ~900 MB) ---------------------------
# Required by the SMB/FTP/Tomcat exploit modules (msfconsole). Not in the
# Ubuntu repos, so we use Rapid7's official installer, which adds their apt
# repository and installs the metasploit-framework package. Non-fatal: if it
# fails, the recon / brute-force / OpenFuck paths still work without it.
if command -v msfconsole >/dev/null 2>&1; then
  log "Metasploit already installed; skipping"
elif command -v curl >/dev/null 2>&1; then
  log "Installing Metasploit Framework (this can take a while)..."
  MSF_INSTALLER="$(mktemp)"
  if curl -fsSL https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb -o "$MSF_INSTALLER"; then
    chmod 755 "$MSF_INSTALLER"
    if $SUDO env DEBIAN_FRONTEND=noninteractive "$MSF_INSTALLER" >/dev/null 2>&1; then
      log "Metasploit installed"
    else
      log "WARN: Metasploit install failed (exploit modules will be unavailable)"
    fi
  else
    log "WARN: could not download the Metasploit installer"
  fi
  rm -f "$MSF_INSTALLER"
fi

# --- nuclei (best effort; not in the Ubuntu repos) -------------------------
# Templated, non-destructive web exposure/CVE scanner used by web-recon.sh.
# Installed from ProjectDiscovery's GitHub release binary.
if command -v nuclei >/dev/null 2>&1; then
  log "nuclei already installed; skipping"
elif command -v curl >/dev/null 2>&1 && command -v unzip >/dev/null 2>&1; then
  log "Installing nuclei..."
  NUC_VER="$(curl -sL --max-time 30 -o /dev/null -w '%{url_effective}' \
    https://github.com/projectdiscovery/nuclei/releases/latest 2>/dev/null \
    | grep -oP 'tag/v\K[0-9.]+')"
  if [ -n "$NUC_VER" ]; then
    NUC_ZIP="$(mktemp --suffix=.zip)"
    if curl -fsSL --max-time 180 \
      "https://github.com/projectdiscovery/nuclei/releases/download/v${NUC_VER}/nuclei_${NUC_VER}_linux_amd64.zip" \
      -o "$NUC_ZIP"; then
      if $SUDO unzip -o -q "$NUC_ZIP" -d /usr/local/bin/ nuclei && $SUDO chmod +x /usr/local/bin/nuclei; then
        log "nuclei ${NUC_VER} installed"
      else
        log "WARN: nuclei unpack failed"
      fi
    else
      log "WARN: nuclei download failed"
    fi
    rm -f "$NUC_ZIP"
  else
    log "WARN: could not resolve the latest nuclei version"
  fi
fi

# --- Make the tools executable ---------------------------------------------
if [ -f "$PROJECT_DIR/hackerEnv" ]; then
  chmod +x "$PROJECT_DIR/hackerEnv"
  log "hackerEnv marked executable"
fi
[ -f "$PROJECT_DIR/tools/web-recon.sh" ] && chmod +x "$PROJECT_DIR/tools/web-recon.sh"

# The rockyou wordlist (~130 MB) is intentionally NOT pre-fetched here; the
# tool's own dependencies() routine downloads it on demand when brute forcing.

log "Done."
exit 0
