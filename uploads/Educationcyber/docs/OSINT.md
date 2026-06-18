# 🕵️ OSINT — Inteligência de Fontes Abertas

> Fase **`osint`** (`./tools/setup-arsenal.sh osint`). Coleta passiva de informação
> sobre pessoas, contas, domínios e segredos vazados — **sem tocar o alvo**.

> ⚠️ OSINT é passivo, mas respeite **privacidade e leis** (LGPD/GDPR). Só para
> engajamentos autorizados, pesquisa de superfície da **sua** organização, ou estudo.

| Ferramenta | Para quê |
|---|---|
| `theHarvester` | e-mails, hosts e subdomínios de fontes públicas |
| `subfinder` / `sublist3r` | enumeração de subdomínios |
| `holehe` | descobre em quais sites um **e-mail** está registrado |
| `maigret` / `sherlock` | encontra um **username** em centenas de plataformas |
| `trufflehog` | varre repositórios git por **segredos/chaves vazadas** |

```bash
# Superfície de um domínio
theHarvester -d empresa.com -b bing,duckduckgo,crtsh
subfinder -d empresa.com -silent | tee subs.txt

# Footprint de identidade (em investigação autorizada)
holehe alvo@email.com
sherlock usuario_alvo
maigret usuario_alvo

# Segredos vazados num repositório (faça no SEU código!)
trufflehog git https://github.com/sua-org/seu-repo --only-verified
trufflehog filesystem ./meu-projeto
```

### Onde isso entra no pentest
OSINT alimenta as fases seguintes: e-mails viram **listas de usuário** para spray
(AD), subdomínios viram **alvos web**, e segredos vazados viram **acesso direto**.

### Defesa
- Monitore seus próprios repositórios com `trufflehog` (CI) — **rotacione** qualquer chave commitada.
- Reduza a superfície: subdomínios órfãos, metadados em documentos públicos, e-mails expostos.
