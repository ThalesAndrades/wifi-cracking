#!/bin/bash
# setup-arsenal.sh — Install a complete, methodology-organized pentest arsenal.
#
# For AUTHORIZED security testing, labs and education ONLY. Installing tools is
# legal; USING them against systems you don't own or aren't authorized to test
# is not. See docs/ARSENAL.md for the methodology and usage.
#
# Usage:
#   ./setup-arsenal.sh [--list] [--yes] [PHASE ...]
#     PHASE   one or more of: recon scan web exploit password postex
#             wireless wordlists  (default: all)
#     --list  show what each phase installs, install nothing
#     --yes   don't prompt before installing
set -uo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; BLUE='\033[0;34m'; YEL='\033[0;33m'; BOLD='\033[1m'; RST='\033[0m'
log()  { echo -e "${BLUE}[arsenal]${RST} $*"; }
ok()   { echo -e "${GREEN}  ok${RST} $*"; }
warn() { echo -e "${YEL}  warn${RST} $*"; }
have() { command -v "$1" >/dev/null 2>&1; }

SUDO=""; [ "$(id -u)" -ne 0 ] && have sudo && SUDO="sudo"
export DEBIAN_FRONTEND=noninteractive
OPT="/opt/arsenal"

# --- helpers ---------------------------------------------------------------
apt_install() {  # apt_install pkg...
  have apt-get || { warn "apt-get not found; skipping: $*"; return; }
  if $SUDO apt-get install -y -qq "$@" 2>/dev/null; then
    for p in "$@"; do ok "$p"; done
  else
    for p in "$@"; do
      if $SUDO apt-get install -y -qq "$p" 2>/dev/null; then ok "$p"; else warn "could not install $p (apt)"; fi
    done
  fi
}
git_tool() {  # git_tool name repo|owner/repo [symlink-target]
  local name="$1" repo="$2" link="${3:-}"
  case "$repo" in http*|git@*|ssh://*) ;; *) repo="https://github.com/$repo.git" ;; esac
  have "$name" && { ok "$name (already)"; return; }
  [ -d "$OPT/$name" ] || $SUDO git clone --depth 1 "$repo" "$OPT/$name" >/dev/null 2>&1 \
    || { warn "git clone failed: $name"; return; }
  [ -n "$link" ] && [ -f "$OPT/$name/$link" ] && $SUDO ln -sf "$OPT/$name/$link" "/usr/local/bin/$name"
  ok "$name (git)"
}
gh_bin() {  # gh_bin name owner/repo asset-grep [unzip|tgz]
  local name="$1" repo="$2" pat="$3" kind="${4:-raw}"
  have "$name" && { ok "$name (already)"; return; }
  local tag url tmp
  tag="$(curl -sL --max-time 25 -o /dev/null -w '%{url_effective}' \
        "https://github.com/$repo/releases/latest" 2>/dev/null | grep -oP 'tag/\K[^/]+')"
  [ -n "$tag" ] || { warn "no release tag: $name"; return; }
  url="https://github.com/$repo/releases/download/$tag/$(printf '%s' "$pat" | sed "s/{tag}/${tag#v}/g; s/{TAG}/$tag/g")"
  tmp="$(mktemp -d)"
  if curl -fsSL --max-time 180 "$url" -o "$tmp/a"; then
    case "$kind" in
      zip) $SUDO unzip -o -q "$tmp/a" -d /usr/local/bin/ "$name" 2>/dev/null ;;
      gz)  gzip -cd "$tmp/a" > "$tmp/$name" 2>/dev/null && $SUDO install -m755 "$tmp/$name" /usr/local/bin/ ;;
      tgz) tar -xzf "$tmp/a" -C "$tmp" 2>/dev/null; $SUDO install -m755 "$(find "$tmp" -type f -name "$name" | head -1)" /usr/local/bin/ 2>/dev/null ;;
      raw) $SUDO install -m755 "$tmp/a" "/usr/local/bin/$name" ;;
    esac
    if have "$name"; then ok "$name ($tag)"; else warn "install failed: $name"; fi
  else warn "download failed: $name ($url)"; fi
  rm -rf "$tmp"
}
pipx_tool() {  # pipx_tool name [pipspec]  — prefers python3.12 (many tools need it)
  local name="$1" pkg="${2:-$1}" py
  have "$name" && { ok "$name (already)"; return; }
  have pipx || apt_install pipx
  py="$(command -v python3.12 || command -v python3)"
  # Pin PIPX_HOME/PIPX_BIN_DIR so the CLI symlink lands on PATH, and verify the
  # command is actually reachable before reporting success.
  if have pipx && [ -n "$py" ] &&
     $SUDO env PIPX_HOME="$OPT/pipx" PIPX_BIN_DIR=/usr/local/bin \
       pipx install --python "$py" "$pkg" >/dev/null 2>&1 &&
     have "$name"; then
    ok "$name (pipx)"
  else
    warn "pipx install failed or command not on PATH: $name"
  fi
}

# --- phases ----------------------------------------------------------------
phase_recon() {
  log "Phase: RECON / OSINT  (footprinting, DNS, subdomains, WAF)"
  apt_install whois dnsutils dnsrecon dnsenum fierce wafw00f
  pipx_tool theHarvester "theHarvester @ git+https://github.com/laramies/theHarvester.git"
  gh_bin subfinder projectdiscovery/subfinder "subfinder_{tag}_linux_amd64.zip" zip
  # amass v5 ships no prebuilt zip — install via snap/go if you want it (see docs)
}
phase_scan() {
  log "Phase: SCANNING / ENUMERATION  (hosts, ports, SMB/SNMP/NetBIOS)"
  apt_install nmap masscan fping netdiscover arp-scan nbtscan onesixtyone \
              snmp smbmap smbclient ncrack
  git_tool enum4linux CiscoCXSecurity/enum4linux enum4linux.pl
}
phase_web() {
  log "Phase: WEB  (dirs, fuzzing, CMS, SQLi, exposures)"
  # sslscan is needed by web-recon.sh; build-essential + ruby-dev are needed to
  # compile wpscan's native gem extensions (nokogiri, yajl-ruby, ffi).
  apt_install nikto whatweb gobuster ffuf dirb wfuzz sqlmap sslscan \
              build-essential ruby-dev
  gh_bin nuclei projectdiscovery/nuclei "nuclei_{tag}_linux_amd64.zip" zip
  gh_bin feroxbuster epi052/feroxbuster "feroxbuster_{TAG}_x86_64-unknown-linux-gnu.zip" zip
  git_tool commix commixproject/commix commix.py
  git_tool joomscan OWASP/joomscan joomscan.pl
  if have gem; then
    if gem install --no-document wpscan >/dev/null 2>&1; then ok "wpscan (gem)"; else warn "wpscan gem failed"; fi
  else
    warn "gem not found; could not install wpscan"
  fi
}
phase_exploit() {
  log "Phase: EXPLOITATION  (framework + exploit search)"
  if have msfconsole; then ok "metasploit (already)"; else
    local i; i="$(mktemp)"
    if curl -fsSL https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb -o "$i" \
       && chmod 755 "$i" && $SUDO env DEBIAN_FRONTEND=noninteractive "$i" >/dev/null 2>&1; then
      ok "metasploit"
    else warn "metasploit install failed"; fi
    rm -f "$i"
  fi
  git_tool searchsploit https://gitlab.com/exploit-database/exploitdb.git searchsploit
}
phase_ad() {
  log "Phase: ACTIVE DIRECTORY  (enum, Kerberos, creds, lateral movement)"
  apt_install ldap-utils krb5-user smbclient
  pipx_tool secretsdump.py impacket            # impacket suite (secretsdump, GetUserSPNs, psexec, ntlmrelayx...)
  pipx_tool certipy certipy-ad                  # AD CS (ESC1-ESC8) abuse
  pipx_tool bloodhound-python bloodhound        # BloodHound collector (attack-path mapping)
  pipx_tool ldapdomaindump                      # full LDAP/domain dump
  gh_bin kerbrute ropnop/kerbrute "kerbrute_linux_amd64" raw
  git_tool Responder lgandx/Responder Responder.py
  if have gem; then
    if gem install --no-document evil-winrm >/dev/null 2>&1; then ok "evil-winrm (gem)"; else warn "evil-winrm gem failed"; fi
  fi
  log "  netexec (nxc) — install the 'password' phase — is your AD swiss-army knife."
}
phase_password() {
  log "Phase: PASSWORDS / CRACKING  (online + offline)"
  apt_install hydra john hashcat medusa ncrack cewl
  pipx_tool netexec   # modern crackmapexec successor (nxc)
}
phase_postex() {
  log "Phase: POST-EXPLOITATION / PIVOTING  (tunnels, proxies)"
  apt_install proxychains4 socat
  gh_bin chisel jpillora/chisel "chisel_{tag}_linux_amd64.gz" gz
  log "  target-side scripts (run ON the box you popped): linPEAS/winPEAS,"
  log "  pspy, LinEnum, PowerSploit — see docs/ARSENAL.md (Phase 6)."
}
phase_osint() {
  log "Phase: OSINT  (people, accounts, subdomains, leaked secrets)"
  apt_install sublist3r
  pipx_tool holehe
  pipx_tool maigret
  pipx_tool sherlock sherlock-project
  gh_bin trufflehog trufflesecurity/trufflehog "trufflehog_{tag}_linux_amd64.tar.gz" tgz
  log "  theHarvester (recon phase) + spiderfoot (pipx) complement this."
}
phase_cloud() {
  log "Phase: CLOUD  (AWS/Azure/GCP auditing & attack)"
  pipx_tool aws awscli
  pipx_tool scout scoutsuite
  pipx_tool prowler
  pipx_tool pacu
  git_tool cloud_enum initstring/cloud_enum cloud_enum.py
  log "  Azure: install 'az' CLI; GCP: 'gcloud' — from the vendor (see docs/CLOUD.md)."
}
phase_mobile() {
  log "Phase: MOBILE  (APK static & dynamic analysis)"
  apt_install apktool default-jdk
  pipx_tool frida frida-tools
  pipx_tool objection
  if have jadx; then ok "jadx (already)"; else
    local tag z; tag="$(curl -sL -o /dev/null -w '%{url_effective}' https://github.com/skylot/jadx/releases/latest 2>/dev/null | grep -oP 'tag/\K[^/]+')"
    if [ -n "$tag" ]; then
      z="$(mktemp --suffix=.zip)"
      if curl -fsSL --max-time 180 "https://github.com/skylot/jadx/releases/download/$tag/jadx-${tag#v}.zip" -o "$z"; then
        $SUDO rm -rf "$OPT/jadx"; $SUDO mkdir -p "$OPT/jadx"
        if $SUDO unzip -o -q "$z" -d "$OPT/jadx"; then
          $SUDO ln -sf "$OPT/jadx/bin/jadx" /usr/local/bin/jadx
          $SUDO ln -sf "$OPT/jadx/bin/jadx-gui" /usr/local/bin/jadx-gui
          ok "jadx ($tag)"
        else warn "jadx unpack failed"; fi
      else warn "jadx download failed"; fi
      rm -f "$z"
    else warn "jadx: no release tag"; fi
  fi
  log "  MobSF (full GUI analyzer) runs best via Docker — see docs/MOBILE.md."
}
phase_wireless() {
  log "Phase: WIRELESS  (needs a monitor-mode adapter; not for VPS/sandbox)"
  apt_install aircrack-ng reaver wifite
}
phase_wordlists() {
  log "Phase: WORDLISTS  (SecLists + rockyou)"
  if [ -d /usr/share/seclists ] || [ -d "$OPT/SecLists" ]; then ok "SecLists (already)"; else
    if $SUDO git clone --depth 1 https://github.com/danielmiessler/SecLists.git "$OPT/SecLists" >/dev/null 2>&1; then
      ok "SecLists (~1GB)"
    else warn "SecLists clone failed"; fi
  fi
  if [ ! -f /usr/share/wordlists/rockyou.txt ]; then
    $SUDO mkdir -p /usr/share/wordlists
    if [ -f /usr/share/wordlists/rockyou.txt.gz ]; then $SUDO gzip -d /usr/share/wordlists/rockyou.txt.gz
    else
      # Download to a temp file and only install it if non-empty, so a failed
      # download doesn't leave a zero-byte file that future runs treat as done.
      tmp_rockyou="$(mktemp)"
      if wget -q -O "$tmp_rockyou" \
        https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt 2>/dev/null &&
        [ -s "$tmp_rockyou" ]; then
        $SUDO install -m644 "$tmp_rockyou" /usr/share/wordlists/rockyou.txt
      fi
      rm -f "$tmp_rockyou"
    fi
    if [ -s /usr/share/wordlists/rockyou.txt ]; then ok "rockyou"; else warn "rockyou download failed"; fi
  else ok "rockyou (already)"; fi
}

ALL=(recon scan web exploit ad password postex osint cloud mobile wireless wordlists)

list_phases() {
  echo -e "${BOLD}Phases:${RST}"
  echo "  recon     whois dnsrecon dnsenum fierce wafw00f theHarvester subfinder"
  echo "  scan      nmap masscan fping netdiscover arp-scan nbtscan onesixtyone snmp smbmap enum4linux"
  echo "  web       nikto whatweb gobuster ffuf dirb wfuzz sqlmap nuclei feroxbuster commix joomscan wpscan"
  echo "  exploit   metasploit-framework searchsploit (exploitdb)"
  echo "  ad        impacket certipy bloodhound-python ldapdomaindump kerbrute Responder evil-winrm"
  echo "  password  hydra john hashcat medusa ncrack cewl netexec"
  echo "  postex    proxychains4 socat chisel (+ target-side scripts, see guide)"
  echo "  osint     sublist3r holehe maigret sherlock trufflehog"
  echo "  cloud     awscli scoutsuite prowler pacu cloud_enum"
  echo "  mobile    apktool default-jdk jadx frida-tools objection"
  echo "  wireless  aircrack-ng reaver wifite  (needs Wi-Fi adapter)"
  echo "  wordlists SecLists rockyou"
}

# --- main ------------------------------------------------------------------
PHASES=(); ASSUME=0; DOLIST=0
for a in "$@"; do
  case "$a" in
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//' | head -n 14; exit 0 ;;
    --list) DOLIST=1 ;;
    --yes|-y) ASSUME=1 ;;
    all) PHASES=("${ALL[@]}") ;;
    recon|scan|web|exploit|ad|password|postex|osint|cloud|mobile|wireless|wordlists) PHASES+=("$a") ;;
    *) echo "Unknown arg: $a" >&2; exit 1 ;;
  esac
done
[ "$DOLIST" -eq 1 ] && { list_phases; exit 0; }
[ "${#PHASES[@]}" -eq 0 ] && PHASES=("${ALL[@]}")

echo -e "${RED}${BOLD}For authorized testing / labs / education only.${RST}"
log "Phases to install: ${PHASES[*]}"
if [ "$ASSUME" -ne 1 ]; then
  read -r -p "Proceed with installation? [y/N]: " a; case "$a" in y|Y|yes) ;; *) echo "Aborted."; exit 1 ;; esac
fi
$SUDO mkdir -p "$OPT"
have apt-get && { log "apt update..."; $SUDO apt-get update -qq || warn "apt update failed"; }

for ph in "${PHASES[@]}"; do "phase_$ph"; done

echo -e "\n${GREEN}${BOLD}Arsenal ready.${RST} Methodology & usage: ${BOLD}docs/ARSENAL.md${RST}"
