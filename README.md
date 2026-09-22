# Network Guardian

A desktop network monitoring and threat-detection tool built in Python — developed as an undergraduate Computer Science thesis (TCC) project.

It captures live network traffic and automatically detects two common threat patterns: **DDoS attacks** and **port scans** — all through a dark-themed, SOC-style desktop dashboard.

![Network Guardian dashboard](docs/screenshot-dashboard.png)
*(replace with an actual screenshot before publishing)*

---

## ✨ Features

- **Dashboard** — live traffic graph, protocol breakdown (TCP/UDP/ICMP), and a table of detected attack events
- **Active Hosts discovery** — scan your local network to see which devices are currently online
- **Alerts** — severity-classified history of every DDoS / Port Scan detection
- **Statistics** — top source IPs and top destination ports since capture started
- **Port Scan tool** — built-in active TCP port scanner (multi-threaded)
- **Configuration** — pick the capture interface and tune detection thresholds live, without restarting
- **PDF reports** — export a session summary with one click

## 🧠 How detection works (short version)

- **DDoS**: combines a fixed packets/second threshold with a statistical z-score check against a rolling window of recent traffic, so both sudden spikes and "unusual for this specific network" traffic get caught.
- **Port Scan**: tracks distinct destination ports contacted per (source → destination) pair within a sliding time window. Only genuine new-connection attempts (pure SYN packets) are counted, so normal response traffic from an open port doesn't get mistaken for a scan.

## 🛠️ Tech stack

| | |
|---|---|
| Language | Python 3.12+ |
| GUI | PyQt6 (QThread + signals/slots for safe concurrency) |
| Packet capture | Scapy |
| Storage | SQLite (WAL mode) |
| Reports | ReportLab |
| Active scanning | `concurrent.futures.ThreadPoolExecutor` |

## ✅ Requirements

- Windows 10/11
- [Npcap](https://npcap.com/) installed (see below)
- **Administrator privileges** when running the app (raw packet capture requires it)
- Python 3.12+ if running from source

### Installing Npcap (required)

Scapy needs Npcap to capture packets on Windows — the app won't see any traffic without it.

1. Download the installer from [npcap.com/#download](https://npcap.com/#download)
2. During setup, make sure **"Install Npcap in WinPcap API-compatible Mode"** is checked
3. Finish the install (a reboot is usually not required, but do it if prompted)

## 🚀 Installation (from source)

```bash
git clone https://github.com/<your-username>/network-guardian.git
cd network-guardian
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## ▶️ Running

Open a terminal **as Administrator**, then:

```bash
.venv\Scripts\python.exe main.py
```

> Packet capture will silently fail to see traffic if the app isn't running elevated. Everything else (Statistics, Port Scan, Configuration) still works without admin rights.

## 📦 Pre-built executable

A standalone Windows build is available under [Releases](../../releases) — no Python installation required.

## ⚠️ Responsible use

The active **Port Scan** and **Active Hosts** tools are meant to be used **only against networks and hosts you own or have explicit permission to test.** Scanning third-party networks without authorization may be illegal in your jurisdiction.

## 🐞 Known limitations

- Tuned for small/home networks — not a replacement for a production IDS (Snort, Suricata, etc.)
- Very slow, spread-out port scans can fall outside the detection time window
- Alerts live in memory only and are lost when the app closes (not yet persisted to the database)
- Windows-only for now (Npcap dependency)
- Wi-Fi adapters generally can't *send* raw/injected packets (a driver limitation, not specific to this app) — active scanning tools use normal OS sockets instead to work around this

## 🙏 I'd love your help testing this

This is part of my undergraduate thesis, and real-world feedback from different machines/networks would help a lot — even just "it installed and ran fine on my PC" is useful data.

- Found a bug or something confusing? Please [open an Issue](../../issues).
- General feedback / your OS version / whether detection worked as expected: [feedback form link here]

Thanks for taking the time to try it out!

## 📄 License

[MIT](LICENSE) — feel free to explore, fork, or reuse.

## 👤 Author

Diogo — Computer Science undergraduate student, Brazil
