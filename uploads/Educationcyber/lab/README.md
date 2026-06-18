# 🧪 Laboratório de Prática

Alvos **propositalmente vulneráveis** para você usar todo o arsenal de forma
**legal e segura**. Tudo roda via Docker, **preso ao `127.0.0.1`** (nunca exposto).

> ⚠️ Estas imagens são **cheias de falhas de propósito**. **Nunca** as exponha à
> internet nem a uma rede que você não controla. Pratique só na própria máquina.

## Subir / parar

```bash
cd lab
docker compose up -d            # sobe os alvos web (Juice Shop, DVWA, bWAPP)
docker compose --profile net up -d   # inclui o Metasploitable 2 (rede/infra)
docker compose ps               # ver status e portas
docker compose logs -f juice-shop
docker compose down             # parar e remover
```

## Alvos e portas

| Alvo | URL/porta local | Treina | Combina com |
|---|---|---|---|
| **OWASP Juice Shop** | http://127.0.0.1:3000 | vulns web modernas (XSS, SQLi, JWT, auth) | `web-recon.sh`, ffuf, nuclei, ZAP |
| **DVWA** | http://127.0.0.1:8080 | web clássico por nível (SQLi, XSS, upload) | sqlmap, hydra, gobuster |
| **bWAPP** | http://127.0.0.1:8081 | 100+ vulnerabilidades web | nikto, wfuzz, commix |
| **Metasploitable 2** *(profile `net`)* | 127.0.0.1: 2121/2222/8023/4445 | FTP/SSH/Telnet/SMB vulneráveis | **hackerEnv**, metasploit, hydra |

> DVWA: faça login (`admin`/`password`), clique em **Create / Reset Database**, e
> ajuste o nível de segurança em **DVWA Security**.

## Primeiros passos sugeridos

```bash
# Recon web seguro contra o Juice Shop
../tools/web-recon.sh http://127.0.0.1:3000 -y

# Brute de diretórios no DVWA
gobuster dir -u http://127.0.0.1:8080 -w /usr/share/wordlists/dirb/common.txt

# nuclei no bWAPP
nuclei -u http://127.0.0.1:8081 -exclude-tags dos,intrusive

# hackerEnv contra o Metasploitable 2 (profile net) — note as portas remapeadas
# (o hackerEnv assume portas padrão; para fidelidade total, rode o Metasploitable
#  como VM em rede host-only e use o IP dela)
```

O passo a passo completo está em [../docs/WALKTHROUGH.md](../docs/WALKTHROUGH.md).
