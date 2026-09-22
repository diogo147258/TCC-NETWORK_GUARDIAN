# Network Guardian

Uma ferramenta desktop de monitoramento de rede e detecção de ameaças, feita em Python — desenvolvida como Trabalho de Conclusão de Curso (TCC) de Ciência da Computação.

O sistema captura o tráfego de rede em tempo real e detecta automaticamente dois padrões de ameaça comuns: **ataques de DDoS** e **varredura de portas (port scan)** — tudo isso através de um painel estilo SOC (Security Operations Center), com tema escuro.

![Dashboard do Network Guardian](docs/screenshot-dashboard.png)
*(troca por um print real antes de publicar)*

---

## ✨ Funcionalidades

- **Dashboard** — gráfico de tráfego em tempo real, distribuição de protocolos (TCP/UDP/ICMP) e tabela dos eventos de ataque detectados
- **Descoberta de hosts ativos** — escaneia a rede local pra ver quais dispositivos estão online agora
- **Alertas** — histórico de todas as detecções de DDoS/Port Scan, classificadas por severidade
- **Estatísticas** — top IPs de origem e top portas de destino desde o início da captura
- **Port Scan** — ferramenta própria de varredura de portas ativa (multi-thread)
- **Configurações** — escolhe a interface de captura e ajusta os limites de detecção em tempo real, sem reiniciar
- **Relatório em PDF** — exporta um resumo da sessão com um clique

## 🧠 Como a detecção funciona (resumo)

- **DDoS**: combina um limite fixo de pacotes/segundo com uma checagem estatística (z-score) contra o histórico recente de tráfego — pega tanto picos súbitos quanto tráfego "incomum pra aquela rede específica".
- **Port Scan**: rastreia quantas portas de destino diferentes cada par (origem → destino) contatou dentro de uma janela de tempo. Só conta tentativas genuínas de conexão nova (pacotes SYN puros), pra tráfego de resposta de uma porta aberta não ser confundido com varredura.

## 🛠️ Tecnologias usadas

| | |
|---|---|
| Linguagem | Python 3.12+ |
| Interface | PyQt6 (QThread + sinais/slots pra concorrência segura) |
| Captura de pacotes | Scapy |
| Armazenamento | SQLite (modo WAL) |
| Relatórios | ReportLab |
| Varredura ativa | `concurrent.futures.ThreadPoolExecutor` |

## ✅ Requisitos

- Windows 10/11
- [Npcap](https://npcap.com/) instalado (veja abaixo)
- **Privilégio de administrador** pra rodar o programa (captura de pacote bruto exige isso)
- Python 3.12+, se for rodar direto do código-fonte

### Instalando o Npcap (obrigatório)

O Scapy precisa do Npcap pra capturar pacote no Windows — sem ele, o programa simplesmente não vê nenhum tráfego.

1. Baixa o instalador em [npcap.com/#download](https://npcap.com/#download)
2. Durante a instalação, marca a opção **"Install Npcap in WinPcap API-compatible Mode"**
3. Termina a instalação (geralmente não precisa reiniciar, mas reinicia se ele pedir)

## 🚀 Instalação (a partir do código-fonte)

```bash
git clone https://github.com/<seu-usuario>/network-guardian.git
cd network-guardian
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## ▶️ Executando

Abre um terminal **como Administrador**, depois:

```bash
.venv\Scripts\python.exe main.py
```

> Sem privilégio de administrador, a captura de pacote simplesmente não vê nenhum tráfego, silenciosamente. O resto (Estatísticas, Port Scan, Configurações) funciona mesmo sem privilégio elevado.

## 📦 Executável pronto

Uma versão `.exe` (Windows, sem precisar instalar Python) está disponível em [Releases](../../releases).

## ⚠️ Uso responsável

As ferramentas de **Port Scan** e **Hosts Ativos** devem ser usadas **só em redes e hosts que você é proprietário ou tem autorização explícita pra testar.** Escanear rede de terceiros sem autorização pode ser crime, dependendo da legislação local.

## 🐞 Limitações conhecidas

- Calibrado pra redes pequenas/domésticas — não substitui um IDS de produção (Snort, Suricata, etc.)
- Varreduras de porta muito lentas e espalhadas no tempo podem escapar da janela de detecção
- Alertas ficam só em memória e são perdidos ao fechar o programa (ainda não persistidos no banco)
- Só funciona em Windows, por enquanto (depende do Npcap)
- Placas Wi-Fi geralmente não conseguem *enviar* pacote bruto/injetado (limitação do driver, não é bug do programa) — as ferramentas de varredura ativa usam socket normal do sistema pra contornar isso

## 🙏 Preciso da sua ajuda pra testar

Esse projeto é parte do meu TCC, e feedback de gente testando em máquinas/redes diferentes ajuda muito — mesmo só "instalou e rodou certinho no meu PC" já é um dado valioso.

- Achou um bug ou algo confuso? [Abre uma Issue](../../issues).
- Feedback geral / qual SO você usa / se a detecção funcionou como esperado: [link do formulário aqui]

Obrigado desde já por dar uma chance ao projeto!

## 📄 Licença

[MIT](LICENSE) — sinta-se livre pra explorar, dar fork, ou reaproveitar.

## 👤 Autor

Diogo — estudante de Ciência da Computação, Brasil
