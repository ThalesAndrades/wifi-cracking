# 🌐 Guia — Recon Web Seguro (`tools/web-recon.sh`)

> Reconhecimento **não-destrutivo** para um site **seu** (VPS/servidor próprio).
> **Sem** brute force, **sem** fuzzing, **sem** DoS. Só coleta de informação e
> checagem de exposições conhecidas.

> ⚠️ **Autorização:** use **apenas** em sistemas que você é dono ou tem permissão
> escrita para testar. **Nunca** em hospedagem compartilhada (afeta vizinhos e
> viola os Termos de Serviço). Em cloud (AWS/GCP/Azure), confira a política de
> pentest do provedor — testes de DoS são sempre proibidos.

---

## Por que um script separado do hackerEnv?

O `hackerEnv` é focado em **infraestrutura/rede** (SMB, FTP, CVEs de Apache/Tomcat
antigos, brute force). Um **site moderno** precisa de outra abordagem: olhar a
**aplicação web** e a **configuração** sem quebrar nada. Por isso este script usa
ferramentas próprias para web e desliga tudo que é intrusivo.

---

## O que ele roda (e o que cada etapa gera)

| Etapa | Ferramenta | O que faz | Gera |
|------|-----------|-----------|------|
| 1 | **dig** | Resolve DNS (A, AAAA, MX) | `dns.txt` |
| 2 | **nmap** | Portas web + versão + **scripts de info** (`http-title`, `http-headers`, `http-server-header`, `ssl-cert`). Sem `-A`, sem scripts intrusivos | `nmap.txt` |
| 3 | **whatweb** | Fingerprint de tecnologias (CMS, framework, libs) | `whatweb.txt` |
| 4 | **sslscan** | Configuração TLS/SSL (protocolos, cifras, certificado) — só se houver HTTPS | `sslscan.txt` |
| 5 | **nikto** | Configurações inseguras e arquivos expostos. **Testes de DoS desligados** (`-Tuning x6`), com limite de tempo | `nikto.txt` |
| 6 | **nuclei** | Templates de exposições/CVEs conhecidas. Exclui `dos,intrusive,fuzz,brute-force`; com **rate-limit** | `nuclei.txt` |

Tudo é salvo em `webrecon-<host>-<timestamp>/` (ou na pasta que você passar com `-o`).

### Salvaguardas embutidas
- **Gate de autorização** — pede confirmação antes de escanear (pule com `-y`).
- **Sem brute force / sem fuzzing / sem DoS** — flags intrusivas explicitamente excluídas.
- **Rate-limit** no nuclei e **timeout** no nikto para não sobrecarregar o alvo.
- Degrada com elegância: se uma ferramenta não estiver instalada, pula com aviso.

---

## Como usar

```bash
# Forma básica (vai pedir confirmação de autorização)
./tools/web-recon.sh https://seu-dominio.com

# Sem o prompt (você já confirmou que é seu) e com pasta de saída custom
./tools/web-recon.sh https://seu-dominio.com -y -o recon-meusite

# Também aceita só o domínio (assume http://)
./tools/web-recon.sh seu-dominio.com
```

Saída de exemplo:
```
+ -- --=[ 2/6 Port & service scan (nmap, info scripts only) ]
443/tcp open https ...
|_http-title: Minha Loja
| http-headers: Server: nginx/1.24.0 ...
+ -- --=[ 5/6 Server config & exposed files (nikto) ]
+ The anti-clickjacking X-Frame-Options header is not present.
...
Done. Results in: webrecon-seu-dominio.com-20260612-0530/
```

---

## Como ler os resultados (o que importa)

- **Headers de segurança ausentes** (nikto/nmap): `X-Frame-Options`,
  `Content-Security-Policy`, `Strict-Transport-Security` → adicione no servidor.
- **Versões expostas** (`Server:` header, whatweb): esconda/atualize software
  desatualizado.
- **TLS fraco** (sslscan): desative SSLv3/TLS1.0/1.1 e cifras fracas.
- **Arquivos/painéis expostos** (nikto/nuclei): `/admin`, `.git/`, `.env`,
  backups → restrinja o acesso.
- **CVEs** (nuclei): atualize o componente afetado.

> Fluxo saudável: **escaneia → corrige → reescaneia** até o relatório ficar limpo.

---

## Dependências

`dig` (dnsutils), `nmap`, `whatweb`, `sslscan`, `nikto`, `nuclei`.

> 💡 No **Claude Code on the web**, todas são instaladas automaticamente pelo
> *SessionStart hook* (`.claude/hooks/session-start.sh`). Numa **VPS Kali/Parrot**,
> a maioria já vem instalada; instale o que faltar com `apt` (e o nuclei pela
> release do ProjectDiscovery).

---

## Quer ir além? (manual, com cuidado)

Para teste de **aplicação** mais profundo (SQLi, XSS, auth) — sempre no seu site:
- **OWASP ZAP** ou **Burp Suite** (proxy interativo, spider + scan ativo)
- **wpscan** se for WordPress
- **testssl.sh** para uma auditoria TLS completa

Essas ferramentas fazem testes ativos mais agressivos — rode em **homologação/staging**
quando possível, e nunca contra produção crítica sem janela de manutenção.
