import re
import subprocess
from concurrent.futures import ThreadPoolExecutor


def descobrir_hosts(faixa_rede: str, iface=None) -> list:
    base_ip = faixa_rede.split("/")[0]
    prefixo = ".".join(base_ip.split(".")[:3])
    ips_para_testar = [f"{prefixo}.{ultimo}" for ultimo in range(1, 255)]

    with ThreadPoolExecutor(max_workers=100) as executor:
        ativos = list(executor.map(_esta_ativo, ips_para_testar))

    ips_ativos = [ip for ip, ativo in zip(ips_para_testar, ativos) if ativo]
    macs = _ler_cache_arp()

    return [(ip, macs.get(ip, "-")) for ip in ips_ativos]


def _esta_ativo(ip: str) -> bool:
    resultado = subprocess.run(
        ["ping", "-n", "1", "-w", "500", ip],
        capture_output=True, text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    return resultado.returncode == 0


def _ler_cache_arp() -> dict:
    saida = subprocess.run(
        ["arp", "-a"], capture_output=True, text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    ).stdout

    macs = {}
    for linha in saida.splitlines():
        partes = linha.split()
        if len(partes) >= 2 and re.match(r"^\d+\.\d+\.\d+\.\d+$", partes[0]):
            macs[partes[0]] = partes[1]
    return macs