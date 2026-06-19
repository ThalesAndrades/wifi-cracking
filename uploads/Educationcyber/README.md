# 🛡️ Educationcyber

Kit **educativo** de segurança ofensiva/defensiva — três ferramentas que cobrem
o ciclo de um pentest, com **guias didáticos** e **gates de autorização**.

```diff
- USO AUTORIZADO APENAS. Rodar contra sistemas que você não possui ou não tem
- permissão escrita para testar é CRIME. Pratique em labs ou no seu próprio VPS.
- Os autores não se responsabilizam por uso indevido.
```

---

## 🧰 As três ferramentas

| Ferramenta | Foco | Guia |
|---|---|---|
| **`hackerEnv`** | Rede/infra: IP sweep, port/vuln scan, exploração (SMB/FTP/Tomcat/Apache) e relatório HTML/DOCX. Automatizado. | [docs/GUIA-EDUCATIVO.md](docs/GUIA-EDUCATIVO.md) |
| **`tools/web-recon.sh`** | Web **não-destrutivo**: dig, nmap, whatweb, sslscan, nikto, nuclei. Sem brute/DoS. | [docs/GUIA-WEB-RECON.md](docs/GUIA-WEB-RECON.md) |
| **`tools/setup-arsenal.sh`** | Instala o **arsenal completo** por fase (recon, web, exploit, **AD**, **cloud**, **mobile**, **OSINT**…). Opt-in. | [docs/ARSENAL.md](docs/ARSENAL.md) |
| **`tools/engage.sh`** | Orquestra o recon e gera um **relatório HTML único** consolidado. | — |

➕ **Laboratório de prática** (alvos vulneráveis legais via Docker): [lab/](lab/) ·
**Walkthrough guiado** ponta-a-ponta: [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md)

---

## 🚀 Início rápido

```bash
# 1. hackerEnv (rede) — contra um alvo de lab/autorizado
chmod +x hackerEnv
./hackerEnv -t <IP_ALVO> -a <SEU_IP> -oA

# 2. Recon web seguro do SEU site (VPS)
./tools/web-recon.sh https://seu-dominio.com

# 3. Instalar o arsenal completo (ou por fase)
./tools/setup-arsenal.sh --list
./tools/setup-arsenal.sh            # tudo

# 4. Subir o laboratório de prática
cd lab && docker compose up -d
```

---

## ☁️ Claude Code on the web

O **SessionStart hook** (`.claude/hooks/session-start.sh`) instala o núcleo de
dependências (nmap, hydra, fping, nikto, etc.) automaticamente no início de uma
sessão web — **mas só funciona quando este diretório está na raiz do repositório**
(o hook é descoberto via `.claude/` na raiz). Se o projeto estiver aninhado (por
exemplo dentro de `uploads/`), o hook **não** roda automaticamente; nesse caso
instale manualmente:

```bash
# a partir da pasta deste projeto:
bash .claude/hooks/session-start.sh          # núcleo via apt
./tools/setup-arsenal.sh --list              # ver fases do arsenal completo
```

Os instaladores remotos pesados (Metasploit ~900 MB, nuclei) são **opt-in**: o
hook só os baixa quando `EDUCATIONCYBER_INSTALL_REMOTE_TOOLS=true` está definido.
O arsenal completo (`setup-arsenal.sh`) também é separado/opt-in por ser pesado.

---

## 📚 Documentação

- [Guia Educativo do hackerEnv](docs/GUIA-EDUCATIVO.md) — o que cada módulo faz e o que gera
- [Guia de Recon Web Seguro](docs/GUIA-WEB-RECON.md) — como auditar seu site sem quebrar nada
- [Arsenal por Fase (metodologia)](docs/ARSENAL.md) — toolkit completo + comandos
- [Active Directory (metodologia)](docs/AD.md) — ataque a redes Windows/AD
- [OSINT](docs/OSINT.md) · [Cloud (AWS/Azure/GCP)](docs/CLOUD.md) · [Mobile (APK)](docs/MOBILE.md)
- [Walkthrough guiado](docs/WALKTHROUGH.md) — do recon ao relatório, passo a passo
- [Guia de Ferramentas do Kali](docs/GUIA-KALI-TOOLS.md) — referência compacta (o que é + comando) por ferramenta
- [Laboratório de prática](lab/README.md) — alvos vulneráveis legais

---

## 🙏 Créditos & licença

Baseado no **[hackerEnv](https://github.com/abdulr7mann/hackerEnv)** de
[@abdulr7mann](https://github.com/abdulr7mann). As ferramentas `web-recon.sh`,
`setup-arsenal.sh`, o laboratório e os guias educativos foram adicionados neste fork.

Licenciado sob **GNU GPL v3.0** (veja [LICENSE](LICENSE)).

### Aviso
Ferramenta fornecida "como está", sem garantias. Destinada a uso **legal e
autorizado**. O mau uso pode resultar em responsabilização criminal. Use por sua conta e risco.
