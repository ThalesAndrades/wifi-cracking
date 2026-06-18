[//]: # ( /docs/AI_SECURITY.md )
[//]: # ( Modern offensive tech + LLM/AI threat landscape — defensive reference )
[//]: # ( Updated: 12 June 2026 )

# Modern Offensive Tech & the LLM Threat Landscape

A defensive, educational reference for the KaliGPT context. The goal is
**awareness**: KaliGPT is itself an LLM-driven agent, so it is both a tool that
runs security tooling *and* a potential target. Knowing the attack surface is how
you harden it. Use everything here only on systems you own or are authorized to
test.

---

## Part 1 — Modern offensive tooling (the "new stack")

The field has shifted from monolithic scanners to fast, composable, JSON-first
Go binaries that chain into pipelines an agent can orchestrate.

| Area | Modern tooling | What changed |
|------|----------------|--------------|
| Recon pipeline | ProjectDiscovery (`subfinder`, `dnsx`, `naabu`, `httpx`, `katana`, `nuclei`, `uncover`) | Streaming JSON, pipe-friendly, template-driven |
| Attack-surface mgmt | `nuclei` + custom templates, `katana`, ASM platforms | Continuous, template-based detection |
| Secrets | `trufflehog`, `gitleaks`, `noseyparker` | Active verification of leaked credentials |
| C2 / post-exploit | `Sliver`, `Mythic`, `Havoc` | Scriptable APIs, modern evasion-aware design |
| Cloud / IaC | `prowler`, `ScoutSuite`, `trivy`, `checkov`, `kube-hunter` | Misconfig & supply-chain focus |
| Fuzzing | `ffuf`, `feroxbuster`, AFL++, `restler` | Faster, smarter, API-aware |
| Exploitation | Metasploit RPC, `nuclei` (exploit templates), `searchsploit` | API-first, automatable |

The agentic angle: a model can run `subfinder → dnsx → httpx → nuclei` end to
end, reason over structured findings, correlate with CVE/ATT&CK knowledge, and
propose next steps. That is the direction KaliGPT is built for.

---

## Part 2 — LLM/AI attack surface (the "weapons" to study)

These are the techniques that target language models and AI agents. Listed so
you can **defend** against them — every KaliGPT deployment should assume these
will be attempted.

### OWASP Top 10 for LLM Applications (the canonical map)
1. **Prompt injection** — untrusted input that overrides instructions.
2. **Insecure output handling** — trusting model output as safe code/HTML/SQL.
3. **Training-data poisoning** — corrupting data the model learns from.
4. **Model denial of service** — expensive prompts exhausting resources.
5. **Supply-chain** — compromised models, datasets, plugins.
6. **Sensitive information disclosure** — leaking secrets/PII from context.
7. **Insecure plugin/tool design** — over-permissive tool calling.
8. **Excessive agency** — the agent can do more than it should.
9. **Overreliance** — humans trusting unverified model output.
10. **Model theft** — extracting weights or behavior.

### Prompt injection — the headline threat
- **Direct injection:** the user types instructions that subvert the system prompt
  ("ignore previous instructions and …").
- **Indirect injection:** malicious instructions hidden in content the model
  *reads* — a web page, a file, a tool result, an email, a code comment, even
  image/PDF metadata. This is the dangerous one for agents: a recon tool fetches
  a page, the page says "exfiltrate the API key", and a naive agent obeys.
- **Why it matters for KaliGPT:** tools like `get_local_server_content`,
  `keyword_search`, `web_request_analysis` pull untrusted text into the context.
  Treat all tool output as untrusted data, never as instructions.

### Jailbreaking techniques (bypassing safety)
- **Role-play / persona** ("DAN"-style), **hypothetical framing**, **payload
  splitting** (assembling a banned request from pieces), **obfuscation**
  (base64, leetspeak, homoglyphs, low-resource languages), **many-shot
  jailbreaking** (flooding context with fake compliant examples),
  **crescendo / multi-turn** (escalating gradually), **adversarial suffixes**
  (gradient-generated token strings that flip refusals).

### Data & privacy attacks
- **Training-data extraction / memorization** — coaxing verbatim secrets out.
- **Membership inference** — proving a record was in the training set.
- **Model inversion** — reconstructing inputs from outputs/embeddings.
- **System-prompt leakage** — tricking the model into revealing its hidden prompt.

### Agent / tool-use specific
- **Tool/function-call abuse** — steering the model to call a powerful tool with
  attacker-chosen arguments.
- **Confused-deputy / SSRF via tools** — making the agent fetch internal URLs.
- **Memory / RAG poisoning** — planting malicious content in a vector store so it
  resurfaces later as "trusted" context.
- **Excessive agency chains** — small permissions composing into a big action.

---

## Part 3 — Defensive playbook (how to harden an LLM agent)

| Threat | Mitigation |
|--------|------------|
| Indirect prompt injection | Treat ALL tool/web/file output as untrusted data; never execute instructions found in it; sandbox/escape rendered content |
| Insecure output handling | Validate/parse model output before use; never pass it straight to a shell, SQL, or `eval` |
| Excessive agency | Least-privilege tools; human-in-the-loop / authorization gates for destructive or dual-use actions (KaliGPT does this via `authorized=True`) |
| Tool argument abuse | Validate every tool argument; allowlist flags (KaliGPT's `validate_arg` + `NMAP_PROFILES`) |
| Secret leakage | Keep secrets out of context; scan for leaks (`trufflehog`/`gitleaks`); redact in logs |
| Jailbreaks | Layered guardrails: input/output filters, refusal training, monitoring, rate limits |
| Supply chain | Pin model/tool/action versions (KaliGPT pins GitHub Actions by SHA); verify checksums |
| DoS | Timeouts and output caps on every tool call (KaliGPT's `run_command` timeout) |

### Tools to test your own AI defenses
- **Garak** — LLM vulnerability scanner (prompt injection, jailbreak, leakage, toxicity).
- **PyRIT** (Microsoft) — risk-identification toolkit for generative AI.
- **promptfoo** — red-team/eval harness for prompts and guardrails.
- **Giskard**, **LLM Guard**, **Rebuff**, **NeMo Guardrails** — scanning and runtime guardrails.
- **counterfit** (Microsoft) — automation for ML attacks.

### Frameworks & references worth reading
- OWASP Top 10 for LLM Applications; OWASP Agentic AI threats.
- MITRE **ATLAS** (adversarial threat landscape for AI systems).
- NIST AI Risk Management Framework (AI RMF) and adversarial-ML taxonomy.

---

## How this maps back to KaliGPT

KaliGPT already implements several of these defenses by design:
- **Untrusted-output discipline** is the reason wrappers return *structured data*
  rather than free text the model might obey.
- **Authorization gate** (`authorized=True`) limits excessive agency on dual-use tools.
- **Argument validation + flag allowlists** block tool-argument abuse.
- **Timeouts** on every `run_command` cap model-driven DoS.
- **SHA-pinned CI** addresses the supply-chain item.

Next hardening steps: run **Garak/promptfoo** against KaliGPT's system prompts,
add explicit "tool output is data, not instructions" framing to the system
prompt, and consider a confirmation step before `execute_generic_linux_command`
runs anything destructive.
