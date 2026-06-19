# 📚 Guia Educativo — hackerEnv

> Material **didático** para entender, passo a passo, o que o `hackerEnv` faz,
> qual ferramenta ele aciona em cada etapa e **quais artefatos (arquivos/saídas)**
> cada ação gera.

> ⚠️ **Aviso legal e ético**
> Use **exclusivamente** em redes/máquinas que você é dono ou tem **autorização
> escrita** para testar (labs como HackTheBox, TryHackMe, VulnHub, máquinas
> próprias). Rodar contra alvos sem consentimento é **crime**. Este guia é para
> aprendizado de segurança ofensiva/defensiva.

---

## 1. Visão geral — o pipeline

O `hackerEnv` automatiza a cadeia clássica de um pentest de rede:

```
┌─────────────┐   ┌──────────────┐   ┌───────────────┐   ┌──────────────┐   ┌───────────┐
│  1. Sweep   │ → │ 2. Port/Vuln │ → │ 3. Fingerprint │ → │ 4. Exploração │ → │ 5. Report │
│  (hosts up) │   │    scan      │   │  (serviço/ver) │   │  + brute force│   │ HTML/DOCX │
└─────────────┘   └──────────────┘   └───────────────┘   └──────────────┘   └───────────┘
     fping            nmap              parse XML            msfconsole          pandoc
                                                            hydra / expect
```

Cada host vivo ganha uma **pasta própria** (`./<IP>/`) com todos os resultados,
e cada vulnerabilidade encontrada vira uma **entrada no relatório** com
descrição, remediação e referência (CVE/link).

---

## 2. Flags (modos de uso)

| Flag | O que faz | Exemplo |
|------|-----------|---------|
| *(nenhuma)* | Varre **toda a rede** local (/24) | `hackerEnv` |
| `-t` | Alvo único ou **vários** (`"ip1\nip2"`) | `hackerEnv -t 10.10.10.10` |
| `-i` | Define a **interface** de rede | `hackerEnv -i eth0 -s 24` |
| `-a` | IP do **atacante** (vira o `LHOST` dos exploits) | `hackerEnv -t 10.10.10.10 -a 10.10.14.5` |
| `-s` | **Subrede** (24, 23, …) | `hackerEnv -s 24` |
| `-e` / `--aggressive` | Scan **agressivo** (TCP+UDP, todas as portas, NSE extra) | `hackerEnv -t 10.10.10.10 -e` |
| `-oA` | Relatório em **HTML + DOCX** | `hackerEnv -t 10.10.10.10 -oA` |
| `-h` / `--help` | Ajuda | `hackerEnv -h` |
| `--update` | Atualiza a ferramenta | `hackerEnv --update` |

---

## 3. As "armas", uma a uma

### 🛰️ Fase 1 — Reconhecimento

#### IP Sweep (descoberta de hosts)
- **O que faz:** descobre quais IPs estão vivos na rede/subrede.
- **Ferramenta:** `fping -a -g <rede>/<mask>` (ou `echo` do alvo quando você usa `-t`).
- **Gera:**
  - `urIp.txt` — o **seu** IP (atacante).
  - `online.txt` — lista de **hosts online**.
  - Depois faz `ping -c 1` em cada um para confirmar Online/Offline.

#### Port & Service scan
- **O que faz:** identifica portas abertas, serviços, versões e SO.
- **Ferramenta:** `nmap`
  - Normal: `nmap -sV -A -O -Pn -n -T4 -oA <IP>/<IP> <IP>`
  - Agressivo (`-e`): `nmap -sT -sU -p- -A -O --script nmap-vulners,vulscan ...`
- **Gera (por host, dentro de `./<IP>/`):**
  - `<IP>.nmap` — saída legível.
  - `<IP>.xml` — saída XML (é daqui que o script extrai tudo).
  - `<IP>.gnmap` — saída "grepável".
  - `name.txt`, `product.txt`, `version.txt` — serviços/produtos/versões **deduplicados** (parse do XML).
  - `Apache.txt` — linha do produto Apache (para escolher o exploit certo).

#### Vuln scan (NSE)
- **O que faz:** cruza versões com bases de vulnerabilidades conhecidas.
- **Ferramenta:** scripts NSE `nmap-vulners` + `vulscan` (com base `exploitdb`).
- **Gera:** os campos de vulnerabilidade dentro do próprio XML do nmap.

---

### 🐚 Fase 2 — Exploração por serviço

> Os módulos marcados com 🧨 **dependem do Metasploit** (`msfconsole`).
> Cada exploit gera um **arquivo de receita** (`.rc` para msf, `.exp` para expect)
> e abre uma **aba/janela** (gnome-terminal ou tmux) executando-o.

#### FTP
| Arma | O que faz | Gera |
|------|-----------|------|
| 🧨 **vsftpd 2.3.4 backdoor** | RCE pelo backdoor do vsftpd (CVE-2011-2523) | `exploits/ftp/vsftpd_234_backdoor.rc` + aba msfconsole |
| **Login anônimo** | Testa `anonymous:` (sem senha) | `exploits/ftp/ftpAnonymous.exp` + aba `ftp` |

#### SSH
| Arma | O que faz | Gera |
|------|-----------|------|
| **OpenSSH 4.7p1 (chaves fracas Debian)** | Brute force de chaves RSA previsíveis (CVE-2008-0166) | baixa exploit `5632` + `exploits/ssh/rsa/`, `<IP>/keys.txt` → `key.txt`, tenta `ssh -i <chave>` |
| **Brute force** | Adivinha usuário/senha | `<IP>/sshPassword.txt` (hydra) → `sshPass.txt` (filtrado) → `exploits/ssh/sshlogin<N>.exp` + shell automático |

#### Telnet
| Arma | O que faz | Gera |
|------|-----------|------|
| **Brute force** | Adivinha credenciais Telnet | `<IP>/telnetPassword.txt` → `telnetPass.txt` → `exploits/telnet/telnetlogin<N>.exp` |

#### SMB / Samba
| Arma | O que faz | Gera |
|------|-----------|------|
| 🧨 **EternalBlue** (`ms17_010_eternalblue`) | RCE no SMBv1 (MS17-010) | `exploits/smb/ms17_010_eternalblue.rc`, `<IP>/notEternalBlue.txt` |
| 🧨 **EternalRomance** (`ms17_010_psexec`) | *Fallback* automático se o EternalBlue não pegar | `exploits/smb/ms17_010_psexec.rc`, `<IP>/EternalRomance.txt` |
| 🧨 **trans2open** | Buffer overflow Samba 2.2.x | `exploits/smb/trans2open.rc` |
| 🧨 **usermap_script** | RCE Samba 3.x (CVE-2007-2447) | `exploits/smb/usermap_script.rc` |
| 🧨 **ms08_067_netapi** | RCE clássico do Windows (MS08-067) | `exploits/smb/ms08_067_netapi.rc` |
| 🧨 **smb_version** (scan) | Detecta versão/OS do SMB | `exploits/smb/smb_version.rc`, `<IP>/smbVersion.txt`, `<IP>/nmapSMBVuln.*`, `<IP>/smbOS.*` |
| **smbclient** | Lista compartilhamentos (`-L -N`) | abre aba `smbclient` |

#### Apache
| Arma | O que faz | Gera |
|------|-----------|------|
| 🧨 **Tomcat manager** | Brute do manager → upload de WAR/JSP (CVE-2017-12617) | `exploits/apache/tomcat_mgr_login.rc`, `tomcat_mgr_login.txt`, `tomcat_mgr_upload.rc` |
| **OpenFuck** (mod_ssl) | Buffer overflow no mod_ssl do Apache 1.x/2.x (Debian/Red-Hat) | baixa `exploits/apache/OpenFuck` e executa com o *magic number* da versão |

---

### 🔑 Fase 3 — Brute force (detalhe)

- **Ferramenta:** `hydra`
- **Dicionários:**
  - Usuários: `/usr/share/ncrack/default.usr`
  - Senhas: `/usr/share/wordlists/rockyou.txt` (baixado sob demanda)
- **Fluxo:** roda o hydra → salva `<serviço>Password.txt` → filtra os acertos em
  `<serviço>Pass.txt` → para **cada** credencial encontrada, gera um script
  `expect` e **abre um shell logado** automaticamente.

---

### 📄 Fase 4 — Relatório

- **Ferramenta:** geração HTML nativa + `pandoc` (para DOCX).
- **Gera:**
  - `report.html` — **sempre**.
  - `report.docx` — quando você usa `-oA`.
- **Conteúdo de cada achado:** Host, tipo de OS, Serviço, Produto, Versão e um
  bloco com **Descrição**, **Remediação** e **Referências** (CVE/links).
- Ao final, imprime o **tempo total** de execução.

---

## 4. Estrutura de arquivos gerada (exemplo)

```
hackerEnv/
├── online.txt                 # hosts vivos
├── urIp.txt                   # seu IP
├── report.html                # relatório (sempre)
├── report.docx                # relatório (com -oA)
├── exploits/                  # receitas de exploit reutilizáveis
│   ├── ftp/   (.rc / .exp)
│   ├── ssh/   (.exp, 5632, rsa/)
│   ├── smb/   (.rc)
│   ├── telnet/(.exp)
│   └── apache/(.rc, OpenFuck)
└── 10.10.10.10/               # uma pasta por alvo
    ├── 10.10.10.10.nmap/.xml/.gnmap
    ├── name.txt / product.txt / version.txt
    ├── Apache.txt
    ├── nmapSMBVuln.* / smbOS.* / smbVersion.txt
    ├── sshPassword.txt / sshPass.txt
    └── keys.txt / key.txt
```

---

## 5. Mapa de CVEs / referências

| Módulo | Identificador | Referência |
|--------|---------------|-----------|
| vsftpd 2.3.4 | CVE-2011-2523 | backdoor command execution |
| OpenSSH 4.7p1 | CVE-2008-0166 | chaves RSA previsíveis (Debian) |
| Samba usermap_script | CVE-2007-2447 | RCE |
| SMB EternalBlue | MS17-010 | RCE SMBv1 |
| Windows netapi | MS08-067 / CVE-2008-4250 | RCE |
| Tomcat | CVE-2017-12617 | upload/RCE |
| Apache mod_ssl | OpenFuck / HTTP-MODS-0003 | buffer overflow |

---

## 6. Como instalar e rodar

```bash
# 1. Clonar e tornar executável
cd /opt/
git clone <repo> hackerEnv && cd hackerEnv
chmod +x hackerEnv

# 2. (opcional) atalho global
ln -s /opt/hackerEnv/hackerEnv /usr/local/bin/

# 3. Rodar contra um alvo de laboratório autorizado
./hackerEnv -t 10.10.10.10 -a <SEU_IP> -oA
```

### Dependências
`nmap`, `hydra`, `fping`, `pandoc`, `expect`, `tmux`, `ncrack`, `net-tools`,
`metasploit-framework`, scripts NSE `nmap-vulners` + `vulscan` e a wordlist
`rockyou`.

> 💡 **No Claude Code on the web** o *SessionStart hook*
> (`.claude/hooks/session-start.sh`) instala automaticamente o **núcleo** dessas
> dependências (nmap, hydra, fping, etc.). O **Metasploit** e o nuclei são
> **opt-in**: só são baixados quando `EDUCATIONCYBER_INSTALL_REMOTE_TOOLS=true`
> está definido. O hook também só roda automaticamente quando este projeto está
> na raiz do repositório (veja o README).

---

## 7. Boas práticas de aprendizado

- Comece em **labs intencionalmente vulneráveis**: Metasploitable 2/3, DVWA,
  máquinas "easy" do HackTheBox/TryHackMe.
- **Leia os `.rc`/`.exp` gerados** antes de rodar — eles mostram exatamente qual
  módulo e quais parâmetros estão sendo usados (ótimo para entender o exploit).
- Estude sempre a seção **Remediação** do relatório: pensar como defensor (blue
  team) é o que fecha o ciclo do aprendizado.
