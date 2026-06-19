# 🛠️ Guia de Uso — Ferramentas do Kali Linux

Referência **compacta** das ferramentas do Kali Linux (catálogo de
<https://www.kali.org/tools/all-tools/>). Para cada ferramenta: **o que é** +
**um comando típico**.

```diff
- USO AUTORIZADO / EDUCATIVO APENAS. Rodar estas ferramentas contra sistemas que
- você não possui ou não tem permissão escrita para testar é CRIME. Pratique em
- labs (ver ../lab/) ou em alvos próprios. Os autores não se responsabilizam por
- uso indevido.
```

> Nota: a lista oficial do Kali tem 600+ pacotes e muda a cada release. Este guia
> cobre as ferramentas reais e relevantes do catálogo, agrupadas por letra.
> Sempre confirme a sintaxe com `man <ferramenta>` ou `<ferramenta> -h`, pois
> flags mudam entre versões.

---

## Índice
[0-9](#0-9) · [A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) ·
[G](#g) · [H](#h) · [I](#i) · [J](#j) · [K](#k) · [L](#l) · [M](#m) · [N](#n) ·
[O](#o) · [P](#p) · [Q](#q) · [R](#r) · [S](#s) · [T](#t) · [U](#u) · [V](#v) ·
[W](#w) · [X](#x) · [Y](#y) · [Z](#z)

---

## 0-9

- **0trace** — traceroute furtivo dentro de uma conexão TCP já estabelecida (evade firewalls). `0trace.sh eth0 <IP> 80`
- **7zip (7z)** — compactador/extrator multiplataforma; útil em forense e wordlists. `7z x arquivo.7z`

## A

- **aesfix / aeskeyfind** — recuperam chaves AES de dumps de memória (forense/cold-boot). `aeskeyfind memoria.dump`
- **afflib-tools** — manipula imagens forenses no formato AFF. `affinfo imagem.aff`
- **aircrack-ng** — suíte de auditoria Wi-Fi (captura + quebra WEP/WPA). `aircrack-ng -w wordlist.txt captura.cap`
- **airgeddon** — script all-in-one de ataques Wi-Fi (handshake, evil twin, WPS). `bash airgeddon.sh`
- **altdns** — gera/permuta subdomínios para descoberta por brute. `altdns -i subs.txt -o perm.txt -w palavras.txt`
- **amap** — fingerprint de aplicações/serviços em portas abertas. `amap -bqv <IP> 80`
- **amass** — mapeamento de superfície de ataque/enumeração de subdomínios (OWASP). `amass enum -d alvo.com`
- **apache-users** — enumera usuários de um servidor Apache (mod_userdir). `apache-users -h <IP> -l users.txt -p 80`
- **apktool** — desmonta/recompila APKs Android (recursos + smali). `apktool d app.apk`
- **apple-bleee** — sniffer de tráfego BLE de dispositivos Apple (AirDrop/Handoff). `python3 ble_read_state.py`
- **arjun** — descobre parâmetros HTTP ocultos em endpoints. `arjun -u https://alvo.com/api`
- **armitage** — GUI colaborativa para o Metasploit. `armitage`
- **arp-scan** — descobre hosts na LAN via ARP. `arp-scan --localnet`
- **arping** — ping em nível ARP (camada 2). `arping -c 3 <IP>`
- **arpwatch** — monitora pares IP/MAC e alerta mudanças (anti-spoofing). `arpwatch -i eth0`
- **asleap** — quebra LEAP/PPTP da Cisco capturando challenge/response. `asleap -r captura.dump -w wordlist`
- **assetfinder** — encontra domínios/subdomínios relacionados a um alvo. `assetfinder alvo.com`
- **atftp** — cliente/servidor TFTP (transferência de firmware/configs). `atftp --get -r config.bin <IP>`
- **autopsy** — plataforma gráfica de análise forense (sobre o Sleuth Kit). `autopsy`
- **autorecon** — recon multi-thread que orquestra nmap e ferramentas web. `autorecon <IP>`
- **axel** — acelerador de download multi-conexão. `axel -n 10 <URL>`
- **azurehound** — coleta dados do Azure AD para análise no BloodHound. `azurehound list --tenant <id> -o saida.json`

## B

- **bed** — fuzzer de protocolos (HTTP, FTP, SMTP…) para achar overflows. `bed -s HTTP -t <IP>`
- **beef-xss** — framework de exploração de navegador via hook XSS. `beef-xss`
- **berate-ap** — cria access point malicioso (rogue AP) script-driven. `berate_ap wlan0 eth0 RedeFalsa`
- **bettercap** — canivete suíço de MITM/recon de rede e Wi-Fi/BLE. `bettercap -iface eth0`
- **bind9 (dig/nslookup)** — servidor/utilitários DNS. `dig A alvo.com @8.8.8.8`
- **bing-ip2hosts** — descobre hostnames hospedados num IP via Bing. `bing-ip2hosts <IP>`
- **binwalk** — analisa/extrai firmware e arquivos embutidos. `binwalk -e firmware.bin`
- **bloodhound** — mapeia caminhos de ataque em Active Directory (grafo). `bloodhound`
- **bloodhound.py / bloodhound-ce-python** — ingestor Python (coleta sem agente Windows). `bloodhound-python -d dominio -u user -p senha -c All`
- **bloodyad** — explora/edita objetos do AD via LDAP. `bloodyAD -u user -p senha -d dominio --host <DC> get writable`
- **blue-hydra** — descoberta e rastreamento de dispositivos Bluetooth. `blue_hydra`
- **bluelog** — scanner/logger de dispositivos Bluetooth próximos. `bluelog -i hci0`
- **blueranger** — localiza rádios Bluetooth via variação de sinal (l2cap ping). `blueranger.sh hci0 <MAC>`
- **bluesnarfer** — extrai dados (agenda/chamadas) de celulares Bluetooth vulneráveis. `bluesnarfer -b <MAC> -r 1-100`
- **bluez (hcitool/l2ping)** — pilha Bluetooth e utilitários. `hcitool scan`
- **bopscrk** — gera wordlists inteligentes a partir de OSINT do alvo. `bopscrk -i`
- **braa** — força bruta de community strings SNMP em massa. `braa public@<IP>:.1.3.6.*`
- **bruteforce-luks** — quebra senha de volumes LUKS por dicionário. `bruteforce-luks -f wordlist.txt /dev/sdb1`
- **bruteforce-salted-openssl** — quebra arquivos cifrados com OpenSSL. `bruteforce-salted-openssl -f wordlist.txt arquivo.enc`
- **bruteforce-wallet** — força bruta de carteiras de criptomoeda. `bruteforce-wallet -f wordlist.txt wallet.dat`
- **bruteshark** — análise forense de rede a partir de PCAP (credenciais, sessões). `bruteshark`
- **brutespray** — spray de credenciais usando saída do nmap (via hydra/medusa). `brutespray --file nmap.gnmap`
- **btscanner** — varre e coleta info de dispositivos Bluetooth (ncurses). `btscanner`
- **bulk-extractor** — extrai e-mails, cartões, URLs de imagens/discos sem montar. `bulk_extractor -o saida/ imagem.dd`
- **bully** — ataque de força bruta a WPS (PIN). `bully wlan0mon -b <BSSID>`
- **burpsuite** — proxy de interceptação e teste de aplicações web. `burpsuite`

## C

- **cabextract** — extrai arquivos .cab (Microsoft). `cabextract arquivo.cab`
- **cadaver** — cliente WebDAV de linha de comando. `cadaver http://alvo/webdav/`
- **caido / caido-cli** — proxy moderno de teste web (alternativa ao Burp). `caido`
- **caldera** — plataforma de emulação de adversário (MITRE). `python3 server.py`
- **capstone** — engine de disassembly multi-arquitetura (lib/CLI). `cstool x86 "4889e5"`
- **ccrypt** — cifra/decifra arquivos (substituto do `crypt`). `ccrypt arquivo.txt`
- **certgraph** — mapeia domínios cruzando campos SAN de certificados TLS. `certgraph alvo.com`
- **certipy-ad** — enumera e explora AD CS (ESC1-ESC8). `certipy find -u user@dominio -p senha -dc-ip <IP>`
- **cewl** — gera wordlist raspando palavras de um site. `cewl -d 2 -w lista.txt https://alvo.com`
- **chainsaw** — caça rápida em logs de eventos do Windows (.evtx). `chainsaw hunt evtx/ -r regras/`
- **changeme** — testa credenciais padrão em serviços/web. `changeme <IP>`
- **chntpw** — reseta/edita senhas de contas locais do Windows (SAM). `chntpw -u Administrator SAM`
- **chirp** — programa rádios amadores (CHIRP). `chirp`
- **chisel** — túnel TCP/UDP sobre HTTP (pivoting). `chisel server -p 8080 --reverse`
- **chkrootkit** — procura rootkits conhecidos no sistema local. `chkrootkit`
- **cisco-auditing-tool (CAT)** — audita roteadores Cisco (senhas default/SNMP). `CAT -h <IP> -w wordlist -a comunidades`
- **cisco-global-exploiter (cge)** — explora 14 vulnerabilidades clássicas de Cisco. `cge.pl <IP> 3`
- **cisco-ocs** — scanner em massa de dispositivos Cisco. `ocs <IP_inicio> <IP_fim>`
- **cisco-torch** — fingerprint/brute de serviços Cisco. `cisco-torch -A <IP>`
- **clamav** — antivírus open source (scan de malware). `clamscan -r /caminho`
- **cloud-enum** — enumera buckets/recursos públicos em AWS/Azure/GCP. `cloud_enum -k empresa`
- **cloudbrute** — descobre infraestrutura de cloud de um alvo. `cloudbrute -d alvo.com -k palavras.txt`
- **cmospwd** — recupera/limpa senha de BIOS/CMOS. `cmospwd`
- **cmseek** — detecta CMS e enumera (WordPress/Joomla/Drupal). `cmseek -u https://alvo.com`
- **cntlm** — proxy autenticado NTLM (pivot por proxy corporativo). `cntlm -c cntlm.conf`
- **coercer** — força autenticação de um host Windows (PetitPotam et al.). `coercer coerce -u user -p senha -t <alvo> -l <listener>`
- **commix** — automação de injeção de comandos do SO em apps web. `commix -u "https://alvo/?p=1"`
- **copy-router-config** — baixa/sobe config de roteadores via SNMP/TFTP. `copy-router-config.pl <IP> <seuIP> private`
- **cowpatty** — quebra WPA-PSK por dicionário (com rainbow tables opcionais). `cowpatty -r captura.cap -f wordlist -s SSID`
- **crackle** — quebra criptografia BLE (LE Legacy Pairing). `crackle -i captura.pcap`
- **crackmapexec (cme/nxc)** — pós-exploração em massa de redes Windows/AD. `crackmapexec smb <faixa> -u user -p senha`
- **creddump7** — extrai hashes/segredos de hives do Windows. `pwdump.py SYSTEM SAM`
- **crowbar** — brute force para serviços fora do escopo do hydra (RDP, OpenVPN). `crowbar -b rdp -s <IP>/32 -u user -C senhas.txt`
- **crunch** — gera wordlists por padrão/charset. `crunch 8 8 0123456789 -o pins.txt`
- **cryptcat** — netcat com criptografia (shell/transferência). `cryptcat -l -p 4444`
- **cupp** — gera wordlist de senhas a partir de perfil pessoal (OSINT). `cupp -i`
- **curl** — cliente HTTP(S) de linha de comando. `curl -sSL -A "x" https://alvo.com`
- **cutycapt** — captura screenshot de páginas web (headless). `cutycapt --url=https://alvo --out=shot.png`
- **cymothoa** — injeta shellcode em processos vivos (backdoor de memória). `cymothoa -p <PID> -s 1`

## D

- **darkstat** — captura tráfego e serve estatísticas via web. `darkstat -i eth0`
- **davtest** — testa upload/execução em servidores WebDAV. `davtest -url http://alvo/webdav`
- **dbd** — backdoor de rede tipo netcat com criptografia AES. `dbd -l -p 4444 -k chave`
- **dc3dd / dcfldd** — `dd` aprimorado para forense (hashing on-the-fly). `dc3dd if=/dev/sdb of=img.dd hash=sha256`
- **ddrescue** — recupera dados de mídias defeituosas. `ddrescue /dev/sdb img.dd log.txt`
- **detect-it-easy (die)** — identifica packers/compiladores de binários. `diec arquivo.exe`
- **dex2jar** — converte .dex (Android) em .jar para análise. `d2j-dex2jar.sh app.apk`
- **dirb** — brute force de diretórios/arquivos web. `dirb https://alvo.com /usr/share/wordlists/dirb/common.txt`
- **dirbuster** — versão GUI/Java do brute de diretórios. `dirbuster`
- **dirsearch** — brute de caminhos web (rápido, em Python). `dirsearch -u https://alvo.com -e php,txt`
- **dislocker** — monta volumes BitLocker no Linux. `dislocker -V /dev/sdb1 -p<recovery> -- /mnt/bl`
- **dmitry** — recon all-in-one (whois, subdomínios, portas). `dmitry -winse alvo.com`
- **dns2tcp** — tunela TCP sobre DNS (exfil/bypass). `dns2tcpc -r ssh -z tun.alvo.com <servidor>`
- **dnscat2** — C2/tunelamento sobre DNS. `dnscat2 --dns server=<IP>`
- **dnschef** — proxy DNS para spoofing/redirecionamento. `dnschef --fakeip <IP>`
- **dnsenum** — enumeração DNS (registros, zona, brute, Google). `dnsenum alvo.com`
- **dnsgen** — gera nomes de domínio prováveis a partir de entradas. `cat subs.txt | dnsgen -`
- **dnsmap** — brute de subdomínios via dicionário. `dnsmap alvo.com -w palavras.txt`
- **dnsrecon** — recon DNS (AXFR, brute, cache snoop). `dnsrecon -d alvo.com`
- **dnstracer** — rastreia a cadeia de servidores DNS de um nome. `dnstracer alvo.com`
- **dnstwist** — detecta typosquatting/phishing de domínios. `dnstwist alvo.com`
- **dnswalk** — auditoria de consistência de zona DNS. `dnswalk alvo.com.`
- **dnsx** — resolução/probing DNS rápido e versátil (ProjectDiscovery). `dnsx -l subs.txt -resp`
- **donut-shellcode** — gera shellcode a partir de .NET/PE/DLL. `donut -f saida.bin payload.exe`
- **doona** — fork do BED (fuzzer de protocolos). `doona -s HTTP -t <IP>`
- **dos2unix** — converte fins de linha CRLF↔LF. `dos2unix arquivo.txt`
- **dotdotpwn** — fuzzer de directory/path traversal. `dotdotpwn -m http -h <IP>`
- **dploot** — extrai segredos DPAPI do Windows remotamente. `dploot masterkeys -u user -p senha -d dominio <alvo>`
- **dradis** — plataforma de colaboração/relatório de pentest. `dradis`
- **driftnet** — captura imagens trafegando na rede. `driftnet -i eth0`
- **dsniff** — suíte de sniffing de credenciais em texto claro. `dsniff -i eth0`
- **dumpsterdiver** — procura segredos/chaves em grandes volumes de arquivos. `DumpsterDiver -p /caminho`
- **dumpzilla** — extrai artefatos forenses de perfis Firefox. `dumpzilla ~/.mozilla/firefox/perfil`
- **dvwa** — app web deliberadamente vulnerável (treino). `docker run -p 80:80 vulnerables/web-dvwa`

## E

- **eaphammer** — ataques a Wi-Fi WPA2-Enterprise (evil twin, captura credencial). `eaphammer --cert-wizard`
- **eapmd5pass** — quebra autenticação EAP-MD5 capturada. `eapmd5pass -r captura.cap -w wordlist`
- **edb-debugger** — depurador gráfico para Linux (estilo OllyDbg). `edb`
- **email2phonenumber** — OSINT que tenta achar telefone a partir de e-mail. `email2phonenumber -e alvo@x.com`
- **emailharvester** — coleta e-mails de um domínio em fontes públicas. `emailharvester -d alvo.com`
- **enum4linux / enum4linux-ng** — enumera SMB/Windows (shares, users, políticas). `enum4linux-ng -A <IP>`
- **enumiax** — brute/enum de usuários IAX2 (Asterisk VoIP). `enumiax -v <IP>`
- **ettercap** — suíte de MITM em LAN (ARP poisoning, filtros). `ettercap -T -i eth0 -M arp`
- **evil-ssdp** — spoof de dispositivos SSDP/UPnP para roubo de credencial. `evil_ssdp.py eth0 -t templates/`
- **evil-winrm / evil-winrm-py** — shell WinRM para pós-exploração Windows. `evil-winrm -i <IP> -u user -p senha`
- **evilginx2** — proxy de phishing que rouba sessão/2FA. `evilginx2`
- **exiflooter** — extrai geolocalização de metadados EXIF de imagens. `exiflooter -i imagem.jpg`
- **exifprobe / exiv2** — leem/editam metadados de imagens. `exiv2 imagem.jpg`
- **exploitdb (searchsploit)** — base local de exploits pesquisável. `searchsploit apache 2.4`
- **extundelete / ext3grep / ext4magic** — recuperam arquivos apagados em ext3/4. `extundelete /dev/sdb1 --restore-all`
- **eyewitness** — tira screenshots de sites/RDP/VNC e gera relatório. `eyewitness --web -f urls.txt`

## F

- **faraday** — IDE/colaboração para gestão de vulnerabilidades. `faraday-cli`
- **fatcat** — análise/edição forense de sistemas de arquivos FAT. `fatcat -l 0 imagem.img`
- **fcrackzip** — quebra senha de arquivos ZIP. `fcrackzip -u -D -p wordlist.txt arquivo.zip`
- **fern-wifi-cracker** — GUI para auditoria Wi-Fi (WEP/WPA). `fern-wifi-cracker`
- **ferret-sidejack** — captura cookies/sessões para sequestro (sidejacking). `ferret -i eth0`
- **feroxbuster** — brute force recursivo de conteúdo web (Rust, rápido). `feroxbuster -u https://alvo.com -w wordlist`
- **ffuf** — fuzzer web rápido (dirs, params, vhosts). `ffuf -u https://alvo/FUZZ -w wordlist.txt`
- **fierce** — recon DNS e descoberta de hosts não contíguos. `fierce --domain alvo.com`
- **fiked** — IKE fake para MITM de VPN IPsec PSK. `fiked -g <gateway> -k grupo:psk`
- **finalrecon** — recon web all-in-one (headers, whois, dirs). `finalrecon --full https://alvo.com`
- **findomain** — enumeração rápida de subdomínios via fontes/CT logs. `findomain -t alvo.com`
- **firewalk** — descobre regras de ACL/filtros de um gateway. `firewalk -S1-100 -i eth0 <gateway> <alvo>`
- **firmware-mod-kit (fmk)** — extrai e remonta imagens de firmware. `extract-firmware.sh firmware.bin`
- **flashrom** — lê/grava chips de flash/BIOS (SPI). `flashrom -p internal -r backup.bin`
- **fluxion** — engenharia social Wi-Fi (captive portal para roubar PSK). `fluxion`
- **foremost** — file carving (recupera por assinatura). `foremost -i imagem.dd -o saida/`
- **fping** — ping em massa/sweep de faixas IP. `fping -a -g 192.168.0.0/24`
- **fragrouter** — fragmenta tráfego para evadir IDS. `fragrouter -i eth0 -B1`
- **freeradius / freeradius-wpe** — servidor RADIUS (e versão patcheada p/ captura). `radiusd -X`
- **ftester** — testa IDS/firewall injetando e auditando pacotes. `ftest -f regras.conf`

## G

- **galleta** — analisa cookies do Internet Explorer (forense). `galleta cookie.txt`
- **gdb (+ gef/peda)** — depurador padrão do GNU, com extensões de exploração. `gdb -q ./binario`
- **getallurls (gau)** — coleta URLs conhecidas de um domínio (Wayback/CT). `gau alvo.com`
- **getsploit** — busca e baixa exploits da Vulners. `getsploit apache`
- **ghidra** — engenharia reversa/decompilação (NSA). `ghidra`
- **gitleaks** — procura segredos commitados em repositórios git. `gitleaks detect -s .`
- **gitxray** — OSINT em repositórios/orgs do GitHub. `gitxray -r https://github.com/org/repo`
- **gobuster** — brute de dirs/DNS/vhosts (Go, rápido). `gobuster dir -u https://alvo -w wordlist.txt`
- **godoh** — C2/tunelamento sobre DNS-over-HTTPS. `godoh --domain alvo.com receive`
- **goldeneye** — ferramenta de teste de carga/DoS HTTP (lab). `goldeneye https://alvo.com`
- **goofile** — busca arquivos de um tipo num domínio. `goofile -d alvo.com -f pdf`
- **gophish** — framework de campanhas de phishing. `gophish`
- **goshs** — servidor HTTP simples para entrega/exfil de arquivos. `goshs -p 8000`
- **gospider** — web crawler rápido para mapear endpoints. `gospider -s https://alvo.com`
- **gowitness** — screenshots de sites em massa (headless Chrome). `gowitness scan file -f urls.txt`
- **gpp-decrypt** — decifra senhas de Group Policy Preferences (cpassword). `gpp-decrypt <string>`
- **gqrx-sdr / gnuradio / gr-osmosdr** — recepção e processamento de rádio (SDR). `gqrx`
- **graudit** — grep de auditoria de código-fonte por padrões inseguros. `graudit -d php /caminho/src`

## H

- **hackrf-tools** — utilitários para o SDR HackRF (TX/RX). `hackrf_info`
- **hash-identifier / hashid** — identificam o tipo de um hash. `hashid '<hash>'`
- **hashcat** — quebra de hashes acelerada por GPU. `hashcat -m 0 -a 0 hashes.txt wordlist.txt`
- **hashdeep / md5deep** — hashing recursivo e auditoria de integridade. `hashdeep -r /caminho`
- **hcxdumptool / hcxtools** — captura e converte handshakes/PMKID Wi-Fi. `hcxdumptool -i wlan0mon -o captura.pcapng`
- **hexedit / hexinject** — editor hexadecimal / injeção de pacotes crus. `hexedit arquivo.bin`
- **host** — consulta DNS simples. `host alvo.com`
- **httrack** — clona sites para análise offline. `httrack https://alvo.com -O ./copia`
- **httptunnel** — tunela tráfego dentro de HTTP. `hts -F localhost:22 80`
- **hydra (thc-hydra)** — brute force de login em dezenas de protocolos. `hydra -l admin -P senhas.txt ssh://<IP>`
- **hyperion** — cripta executáveis PE para evadir AV. `hyperion payload.exe payload_crypt.exe`

## I

- **ike-scan** — descobre/fingerprint de gateways VPN IPsec/IKE. `ike-scan <IP>`
- **impacket** — coleção de scripts Python para protocolos Windows (SMB/Kerberos/etc.). `impacket-secretsdump dominio/user:senha@<IP>`
- **inetsim** — simula serviços de Internet para análise de malware. `inetsim`
- **intrace** — traceroute aproveitando conexões TCP existentes. `intrace -h alvo.com`
- **iodine** — tunela IPv4 sobre DNS. `iodine -f tun.alvo.com`
- **ip2location** — geolocaliza endereços IP. `ip2location -i <IP>`
- **ipv6toolkit (SI6)** — suíte de avaliação/ataque de IPv6. `scan6 -i eth0 -L`
- **irssi** — cliente IRC em terminal (C2/comunicação). `irssi`
- **isr-evilgrade** — explora mecanismos de atualização inseguros. `evilgrade`

## J

- **jadx** — decompila APK/DEX para Java legível. `jadx-gui app.apk`
- **jd-cli / jd-gui** — decompiladores de Java (.class → .java). `jd-cli arquivo.jar`
- **jhead** — manipula cabeçalhos EXIF de JPEGs. `jhead imagem.jpg`
- **john (john the ripper)** — quebra de senhas/hashes versátil. `john --wordlist=wl.txt hashes.txt`
- **joomscan** — scanner de vulnerabilidades para Joomla. `joomscan -u https://alvo.com`
- **jq** — processa/filtra JSON na linha de comando. `curl -s api | jq '.data[]'`
- **jsql-injection** — exploração automatizada de SQL injection (GUI). `jsql`

## K

- **kalibrate-rtl (kal)** — encontra offset de frequência de SDR via GSM. `kal -s GSM900`
- **keepassxc** — gerenciador de senhas (e análise de bancos .kdbx). `keepassxc`
- **keystone** — engine de assembler multi-arquitetura. `kstool x86-64 "add rax, rbx"`
- **kismet** — detector/sniffer de redes sem fio (Wi-Fi/BT/SDR). `kismet -c wlan0mon`
- **knockpy** — enumeração de subdomínios por dicionário. `knockpy alvo.com`
- **knowsmore** — gestão de credenciais/NTLM em engajamentos AD. `knowsmore --secrets-dump dump.txt`
- **knxmap** — scanner/exploração de redes KNX/EIB (automação predial). `knxmap scan <IP>`
- **krackattacks-scripts** — testa vulnerabilidade KRACK em clientes Wi-Fi. `krack-test-client.py`

## L

- **laps-toolkit** — analisa senhas LAPS expostas no AD. `Get-LAPSPasswords`
- **lbd** — detecta balanceadores de carga (DNS/HTTP). `lbd alvo.com`
- **ldeep** — enumeração profunda e offline de LDAP/AD. `ldeep ldap -u user -p senha -d dominio -s ldap://<DC> all`
- **legion** — framework gráfico de recon/scan semi-automático. `legion`
- **lftp** — cliente de transferência de arquivos sofisticado (FTP/SFTP/HTTP). `lftp -u user,senha ftp://<IP>`
- **libpcap-based tools** — base de captura de pacotes para muitas ferramentas. `tcpdump -i eth0`
- **linkedin2username** — gera listas de usuários a partir de funcionários no LinkedIn. `linkedin2username -c empresa -u user`
- **linux-exploit-suggester** — sugere exploits de elevação locais. `les.sh`
- **linwinpwn** — automação de enumeração/ataque AD a partir do Linux. `linWinPwn.sh -t <DC> -u user -p senha`
- **lynis** — auditoria de hardening/segurança de sistemas Unix. `lynis audit system`

## M

- **macchanger** — altera o endereço MAC de uma interface. `macchanger -r eth0`
- **maltego** — plataforma gráfica de OSINT e link analysis. `maltego`
- **maskprocessor** — gera wordlists por máscara (alta velocidade). `mp64 ?d?d?d?d > pins.txt`
- **masscan** — scanner de portas em escala de Internet (assíncrono). `masscan <faixa> -p1-65535 --rate 10000`
- **mdk3 / mdk4** — estresse/ataques a Wi-Fi (deauth, beacon flood). `mdk4 wlan0mon d -b lista.txt`
- **medusa** — brute force de login paralelo e modular. `medusa -h <IP> -u admin -P senhas.txt -M ssh`
- **metasploit-framework (msfconsole)** — framework de exploração e pós-exploração. `msfconsole`
- **mfoc / mfcuk** — quebram chaves de cartões MIFARE Classic (RFID). `mfoc -O dump.mfd`
- **mimikatz** — extrai credenciais/tickets da memória do Windows. `mimikatz # sekurlsa::logonpasswords`
- **minimodem** — modem de software (decodifica/gera áudio FSK). `minimodem -r 1200`
- **mitmproxy** — proxy HTTPS interativo de interceptação. `mitmproxy -p 8080`
- **msfpc** — gera payloads do Metasploit de forma simplificada. `msfpc windows <seuIP>`
- **multiforcer / mp** — utilitários de cracking distribuído. `multiforcer -h`

## N

- **nbtscan** — varre redes por informações NetBIOS. `nbtscan <faixa>`
- **ncat / netcat (nc)** — leitura/escrita em conexões TCP/UDP (shells, transfer). `nc -lvnp 4444`
- **ncrack** — brute force de autenticação em rede de alta velocidade. `ncrack -u admin -P senhas.txt rdp://<IP>`
- **netdiscover** — descoberta ativa/passiva de hosts via ARP. `netdiscover -i eth0 -r <faixa>`
- **netexec (nxc)** — sucessor do CrackMapExec para pós-exploração de rede. `nxc smb <faixa> -u user -p senha`
- **nikto** — scanner de vulnerabilidades/exposições em servidores web. `nikto -h https://alvo.com`
- **nipper-ng** — audita configurações de dispositivos de rede. `nipper --ios-router config.txt`
- **nmap** — scanner de portas/serviços/vulns com NSE. `nmap -sV -sC -p- <IP>`
- **nuclei** — scanner web baseado em templates (CVEs/exposições). `nuclei -u https://alvo.com`

## O

- **onesixtyone** — brute rápido de community strings SNMP. `onesixtyone -c comunidades.txt <IP>`
- **ophcrack** — quebra hashes LM/NTLM com rainbow tables (GUI). `ophcrack`
- **openvas / gvm** — scanner de vulnerabilidades de rede completo. `gvm-start`
- **osrframework** — suíte de OSINT (usernames, e-mails, domínios). `usufy -n alvo`

## P

- **p0f** — fingerprint passivo de SO/conexões. `p0f -i eth0`
- **pacu** — framework de exploração de ambientes AWS. `pacu`
- **padbuster** — explora oráculos de padding (criptografia). `padbuster <URL> <amostra> 8`
- **patator** — brute force multipropósito e modular. `patator ssh_login host=<IP> user=admin password=FILE0 0=wl.txt`
- **payloadsallthethings** — coleção de payloads/cheatsheets (referência). `ls /usr/share/payloadsallthethings`
- **pdf-parser / peepdf** — analisam PDFs maliciosos. `pdf-parser arquivo.pdf`
- **pixiewps** — explora WPS offline (Pixie Dust). `pixiewps -e <pke> -r <pkr> -s <ehash> -z <shash> -a <authkey>`
- **plink (putty-tools)** — cliente SSH em linha (túneis/pivot). `plink -R 3389:127.0.0.1:3389 user@<IP>`
- **powersploit / powershell-empire** — pós-exploração PowerShell / C2. `powershell-empire server`
- **proxychains-ng** — força aplicações a passarem por proxies (pivot). `proxychains nmap -sT <IP>`
- **pwncat** — netcat com recursos de pós-exploração e persistência. `pwncat-cs <IP> 4444`

## Q

- **qsslcaudit** — testa robustez de clientes TLS/SSL. `qsslcaudit -l 0.0.0.0 -p 8443`
- **quark-engine** — pontua/analisa comportamento malicioso de APKs. `quark -a app.apk`

## R

- **radare2 / rizin** — framework de engenharia reversa em linha de comando. `r2 -A ./binario`
- **rainbowcrack (rcrack)** — quebra hashes com rainbow tables. `rcrack tabelas/ -h <hash>`
- **rdesktop / xfreerdp** — clientes RDP (acesso/teste a Windows). `xfreerdp /u:user /p:senha /v:<IP>`
- **reaver** — força bruta de PIN WPS para recuperar PSK. `reaver -i wlan0mon -b <BSSID> -vv`
- **recon-ng** — framework modular de reconhecimento web (estilo msf). `recon-ng`
- **redis-tools (redis-cli)** — interage com/explora instâncias Redis expostas. `redis-cli -h <IP>`
- **responder** — envenena LLMNR/NBT-NS/mDNS e captura hashes NetNTLM. `responder -I eth0`
- **rfcat** — controla dongles RF (sub-GHz) para análise/replay. `rfcat -r`
- **rsmangler** — expande/mangle wordlists com variações. `rsmangler -f base.txt`
- **rtl_433 / rtl-sdr** — recebe e decodifica sinais ISM com RTL-SDR. `rtl_433 -f 433920000`

## S

- **scalpel** — file carving por assinaturas (forense). `scalpel imagem.dd -o saida/`
- **scrcpy** — espelha/controla tela de dispositivos Android. `scrcpy`
- **sherlock** — caça contas de um username em centenas de sites. `sherlock usuario`
- **set (social-engineer toolkit)** — framework de engenharia social (phishing, clones). `setoolkit`
- **sherlock / spiderfoot** — OSINT automatizado de pessoas/infra. `spiderfoot -l 127.0.0.1:5001`
- **siege** — teste de carga/stress HTTP. `siege -c 50 https://alvo.com`
- **skipfish** — scanner ativo e rápido de aplicações web. `skipfish -o saida/ https://alvo.com`
- **sleuthkit (tsk)** — ferramentas de análise forense de disco (base do Autopsy). `fls -r imagem.dd`
- **smbclient / smbmap** — acessa e mapeia compartilhamentos SMB. `smbmap -H <IP> -u user -p senha`
- **smtp-user-enum** — enumera usuários via SMTP (VRFY/EXPN/RCPT). `smtp-user-enum -M VRFY -U users.txt -t <IP>`
- **snmp-check / snmpwalk** — coletam informações via SNMP. `snmpwalk -v2c -c public <IP>`
- **snort** — IDS/IPS de rede baseado em regras. `snort -A console -i eth0 -c snort.conf`
- **social-analyzer** — analisa/localiza perfis em redes sociais (OSINT). `social-analyzer -u "nome"`
- **spectre-meltdown-checker** — verifica vulnerabilidade da CPU a Spectre/Meltdown. `spectre-meltdown-checker`
- **spiderfoot** — automação de OSINT/recon com dezenas de módulos. `spiderfoot -s alvo.com`
- **spike (generic_*_send)** — fuzzer de protocolos de rede. `generic_send_tcp <IP> 80 script.spk 0 0`
- **spose / sparta** — scanners/recon assistido (legado). `sparta`
- **sqlmap** — detecção e exploração automatizada de SQL injection. `sqlmap -u "https://alvo/?id=1" --batch`
- **sqlninja** — exploração de SQLi em MS-SQL com foco em shell. `sqlninja -m test -f sqlninja.conf`
- **ssh-audit** — audita configuração/algoritmos de servidores SSH. `ssh-audit <IP>`
- **sshpass** — fornece senha SSH não-interativamente (scripts). `sshpass -p senha ssh user@<IP>`
- **sshuttle** — VPN/pivot transparente sobre SSH. `sshuttle -r user@<IP> 10.0.0.0/8`
- **sslscan / sslyze / testssl.sh** — auditam configuração TLS/SSL de serviços. `sslscan alvo.com`
- **sslstrip** — rebaixa HTTPS para HTTP em MITM. `sslstrip -l 8080`
- **steghide / stegseek** — escondem/extraem dados em imagens-áudio (esteganografia). `steghide extract -sf imagem.jpg`
- **strace / ltrace** — rastreiam syscalls / chamadas de biblioteca de um processo. `strace -f ./binario`
- **subfinder** — enumeração passiva de subdomínios (ProjectDiscovery). `subfinder -d alvo.com`
- **sublist3r** — enumera subdomínios via buscadores. `sublist3r -d alvo.com`
- **sucrack** — brute force de senha local via `su`. `sucrack -w 10 -u root wordlist.txt`
- **sqlsus / sudomy** — exploração MySQL / recon de subdomínios. `sudomy -d alvo.com`

## T

- **t50** — gerador de tráfego/stress de rede (muitos protocolos). `t50 <IP> --flood`
- **tcpdump** — captura e analisa pacotes na linha de comando. `tcpdump -i eth0 -w captura.pcap`
- **tcpflow** — reconstrói e grava fluxos TCP. `tcpflow -i eth0`
- **tcpreplay** — reinjeta tráfego de arquivos pcap. `tcpreplay -i eth0 captura.pcap`
- **testdisk / photorec** — recuperam partições e arquivos apagados. `testdisk imagem.dd`
- **thc-ipv6** — suíte de ataque/teste de protocolos IPv6. `atk6-alive6 eth0`
- **thc-ssl-dos** — teste de exaustão por renegociação SSL (lab). `thc-ssl-dos <IP> 443`
- **theharvester** — coleta e-mails/hosts/subdomínios em fontes públicas. `theHarvester -d alvo.com -b all`
- **tnscmd10g** — interage com o listener TNS do Oracle. `tnscmd10g version -h <IP>`
- **tor / torsocks** — roteamento anônimo e socksify de aplicações. `torsocks curl https://alvo`
- **traceroute / tracetcp** — traçam o caminho de rede até um host. `traceroute alvo.com`
- **trity / trufflehog** — utilitários diversos / busca de segredos em repos. `trufflehog git https://github.com/org/repo`
- **twofi** — gera wordlist a partir de tweets do alvo. `twofi -u usuario`

## U

- **unicornscan** — scanner de portas assíncrono e flexível. `unicornscan <IP>:1-65535`
- **unix-privesc-check** — checa configurações para elevação de privilégio local. `unix-privesc-check standard`
- **urlcrazy** — gera variações de domínio (typosquatting/brand). `urlcrazy alvo.com`

## V

- **vega** — scanner gráfico de vulnerabilidades web. `vega`
- **veil** — gera payloads que evadem antivírus. `veil`
- **villain** — framework C2 multi-sessão (reverse shells). `python3 Villain.py`
- **volatility3** — análise forense de memória RAM. `vol -f memoria.raw windows.pslist`
- **vncviewer / vncsnapshot** — cliente VNC / captura de tela remota. `vncviewer <IP>::5900`

## W

- **wafw00f** — identifica/fingerprint de WAFs à frente de um site. `wafw00f https://alvo.com`
- **wapiti** — scanner de vulnerabilidades web (black-box). `wapiti -u https://alvo.com`
- **wash** — detecta APs com WPS habilitado. `wash -i wlan0mon`
- **wfuzz** — fuzzer web para força bruta de conteúdo/parâmetros. `wfuzz -w wl.txt https://alvo/FUZZ`
- **whatweb** — identifica tecnologias de um site. `whatweb https://alvo.com`
- **whois** — consulta registro de domínios/IPs. `whois alvo.com`
- **wifiphisher** — ataques de phishing/associação automatizada em Wi-Fi. `wifiphisher`
- **wifite** — automatiza ataques a redes Wi-Fi (WEP/WPA/WPS). `wifite`
- **windapsearch** — enumera usuários/grupos do AD via LDAP. `windapsearch -d dominio --dc <IP> -U`
- **wireshark / tshark** — analisador de protocolos de rede (GUI/CLI). `tshark -i eth0`
- **wordlists** — coleção de wordlists (inclui rockyou). `ls /usr/share/wordlists`
- **wpscan** — scanner de vulnerabilidades para WordPress. `wpscan --url https://alvo.com --enumerate u`

## X

- **xhydra** — front-end gráfico do hydra. `xhydra`
- **xprobe2** — fingerprint de SO remoto via ICMP. `xprobe2 <IP>`
- **xsser** — detecção e exploração automatizada de XSS. `xsser -u "https://alvo/?q=teste"`

## Y

- **yara** — identifica/classifica malware por regras de padrões. `yara regras.yar arquivo`
- **yersinia** — ataques a protocolos de camada 2 (STP, DHCP, CDP). `yersinia -G`

## Z

- **zaproxy (OWASP ZAP)** — proxy/scanner de segurança de aplicações web. `zaproxy`
- **zenmap** — interface gráfica oficial do nmap. `zenmap`
- **zphisher** — kit automatizado de páginas de phishing (lab/educativo). `bash zphisher.sh`
- **zsteg** — detecta dados ocultos (esteganografia) em PNG/BMP. `zsteg imagem.png`

---

### Como usar este guia
1. Identifique a **fase** do trabalho (recon, scan, exploração, pós-exploração, forense).
2. Escolha a ferramenta, rode `<ferramenta> -h` ou `man <ferramenta>` para a sintaxe exata.
3. Pratique primeiro no **laboratório** (`../lab/docker-compose.yml`) antes de qualquer alvo real autorizado.
4. Consulte também: [ARSENAL.md](ARSENAL.md), [GUIA-WEB-RECON.md](GUIA-WEB-RECON.md), [WALKTHROUGH.md](WALKTHROUGH.md).

> Lista completa e sempre atualizada: <https://www.kali.org/tools/all-tools/>

