# 📱 Mobile — Análise de Apps Android (APK)

> Fase **`mobile`** (`./tools/setup-arsenal.sh mobile`). Análise **estática** e
> **dinâmica** de aplicativos Android.

> ⚠️ Analise **apps seus** ou que você tem autorização para testar. Engenharia
> reversa de software de terceiros pode violar termos de licença/leis.

| Ferramenta | Para quê |
|---|---|
| `apktool` | desmonta o APK (recursos, `AndroidManifest.xml`, smali) |
| `jadx` / `jadx-gui` | **decompila** DEX → Java legível |
| `frida` / `objection` | instrumentação **dinâmica** em runtime (hooking) |
| **MobSF** (Docker) | analisador completo com GUI (estático + dinâmico) |

## Estática
```bash
# Desmontar e ler o manifesto (permissões, exported components, debuggable)
apktool d app.apk -o app_src
grep -E 'permission|exported|debuggable|cleartext' app_src/AndroidManifest.xml

# Decompilar para Java e caçar segredos/endpoints
jadx -d app_java app.apk
grep -rniE 'api[_-]?key|secret|password|http://|firebase' app_java/ | head
```
**O que procurar:** chaves de API hardcoded, URLs de backend, `android:debuggable=true`,
`usesCleartextTraffic`, componentes `exported` sem proteção, armazenamento inseguro.

## Dinâmica (precisa de device/emulador com root + frida-server)
```bash
objection -g com.alvo.app explore           # SSL pinning bypass, dump de memória...
frida-ps -U                                  # processos no device
```

## MobSF (recomendado — GUI completa, via Docker)
```bash
docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf
# abra http://127.0.0.1:8000 e faça upload do APK
```

### Defesa (para quem desenvolve apps)
- Nunca hardcode segredos no APK; use backend + tokens de curta duração.
- `android:debuggable=false`, sem cleartext, certificate pinning, ofuscação
  (R8/ProGuard), e valide tudo no servidor (o cliente é sempre confiável demais).
