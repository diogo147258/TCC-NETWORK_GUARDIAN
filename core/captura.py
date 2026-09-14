from scapy.layers.inet import IP, TCP, UDP, ICMP
from database.modelo import PacoteInfo
from scapy.all import get_if_list

def converter_pacote(pacote_scapy):
    if IP not in pacote_scapy:
        return None

    camada_ip = pacote_scapy[IP]

    porta_origem = None
    porta_destino = None
    protocolo = "Outro"
    eh_syn = False

    if TCP in pacote_scapy:
        protocolo = "TCP"
        porta_origem = pacote_scapy[TCP].sport
        porta_destino = pacote_scapy[TCP].dport

        try:
            flags = int(pacote_scapy[TCP].flags)
            eh_syn = bool(flags & 0x02) and not bool(flags & 0x10)
        except Exception:
            eh_syn = False

    elif UDP in pacote_scapy:
        protocolo = "UDP"
        porta_origem = pacote_scapy[UDP].sport
        porta_destino = pacote_scapy[UDP].dport
    elif ICMP in pacote_scapy:
        protocolo = "ICMP"

    return PacoteInfo(
        horario=pacote_scapy.time,
        ip_origem=camada_ip.src,
        ip_destino=camada_ip.dst,
        porta_origem=porta_origem,
        porta_destino=porta_destino,
        protocolo=protocolo,
        tamanho=len(pacote_scapy),
        eh_syn=eh_syn,
    )

def listar_interfaces():
    try:
        from scapy.all import conf
        interfaces = []
        for identificador, interface_obj in conf.ifaces.items():
            ip = (getattr(interface_obj, "ip", "") or "").strip()
            nome = (
                getattr(interface_obj, "description", "")
                or getattr(interface_obj, "name", "")
                or str(identificador)
            )
            if ip and ip not in ("0.0.0.0", "::"):
                rotulo = f"{ip} - {nome}"
            else:
                rotulo = f"{nome} (sem IP)"
            interfaces.append((rotulo, str(identificador)))
        if interfaces:
            return interfaces
    except Exception:
        pass
    return [(nome, nome) for nome in get_if_list()]