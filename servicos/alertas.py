import time

from database.modelo import Alerta


class ServicoAlertas:
    def __init__(self, tempo_espera=10):
        self.tempo_espera = tempo_espera
        self.ultima_vez = {}

    def notificar(self, alerta: Alerta):
        chave = (alerta.tipo, alerta.ip)
        agora = time.time()
        ultima = self.ultima_vez.get(chave, 0)

        if agora - ultima < self.tempo_espera:
            return

        print(f"[{alerta.severidade.value}] {alerta.mensagem}")
        self.ultima_vez[chave] = agora