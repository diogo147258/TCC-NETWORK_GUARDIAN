import socket
from concurrent.futures import ThreadPoolExecutor


def testar_porta(ip: str, porta: int, timeout: float = 0.5) -> bool:
    conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conexao.settimeout(timeout)

    resultado = conexao.connect_ex((ip, porta))
    conexao.close()

    return resultado == 0


def varrer_portas(ip: str, porta_inicio: int, porta_fim: int, timeout: float = 0.5) -> list[int]:
    portas = range(porta_inicio, porta_fim + 1)
    portas_abertas = []

    with ThreadPoolExecutor(max_workers=200) as executor:
        resultados = executor.map(lambda porta: (porta, testar_porta(ip, porta, timeout)), portas)

        for porta, esta_aberta in resultados:
            if esta_aberta:
                portas_abertas.append(porta)

    return sorted(portas_abertas)