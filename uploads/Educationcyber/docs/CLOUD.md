# ☁️ Cloud — Auditoria e Ataque (AWS / Azure / GCP)

> Fase **`cloud`** (`./tools/setup-arsenal.sh cloud`). Auditoria de postura e
> exploração de configurações inseguras em ambientes cloud.

> ⚠️ **Só na SUA conta/assinatura** ou com autorização escrita. Provedores
> permitem testar seus próprios recursos, mas **proíbem DoS/stress**. Use
> credenciais de teste e nunca toque recursos de outros tenants.

| Ferramenta | Para quê |
|---|---|
| `awscli` (`aws`) | interação base com AWS |
| `scoutsuite` (`scout`) | auditoria multi-cloud de postura de segurança (relatório HTML) |
| `prowler` | benchmarks (CIS) e centenas de checagens AWS/Azure/GCP |
| `pacu` | framework de **exploração** AWS (pós-credencial) |
| `cloud_enum` | enumeração de buckets/recursos públicos (S3, Azure blobs, GCP) |

```bash
# Postura de segurança (read-only) — precisa de credenciais configuradas
aws configure                                  # suas chaves de teste
scout aws                                       # gera relatório HTML navegável
prowler aws -M html -S                          # CIS benchmark + severidade

# Enumeração de recursos públicos (sem credencial)
cloud_enum -k suaempresa -k suaempresa-prod     # busca buckets/blobs expostos

# Exploração pós-credencial (lab/autorizado)
pacu                                            # framework interativo
  > import_keys --all
  > run iam__enum_permissions
```

> **Azure:** instale a `az` CLI (`curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash`) +
> use o **ScoutSuite/Prowler azure**. **GCP:** instale o `gcloud` SDK.

### O que procurar
- Buckets/blobs **públicos**, chaves IAM excessivamente permissivas, MFA ausente,
  logging (CloudTrail) desligado, security groups abertos (0.0.0.0/0), segredos em
  variáveis de ambiente/metadata.

### Defesa
- Rode `prowler`/`scoutsuite` no **seu** ambiente periodicamente (ou em CI).
- Princípio do menor privilégio, MFA obrigatório, criptografia, e alertas no
  CloudTrail/Activity Log.
