class DetectorPortScan:
    def __init__(self, limite_porta=15, janela_segundos=10):
        self.limite_porta = limite_porta
        self.janela_segundos=janela_segundos
        self.eventos_por_par={}
        self.pares_em_alerta=set()

    def processar_pacote(self, pacote):
        chave = (pacote.ip_origem, pacote.ip_destino)
        if chave not in self.eventos_por_par:
            self.eventos_por_par[chave] = []
        self.eventos_por_par[chave].append((pacote.horario, pacote.porta_destino))
        self._esquecer_antigo(chave, pacote.horario)

        porta_janela = {
            porta for _horario, porta in self.eventos_por_par[chave]
        }
        esta_escaneando = len(porta_janela) >= self.limite_porta
        if esta_escaneando and chave not in self.pares_em_alerta:
            self.pares_em_alerta.add(chave)
            return True

        if not esta_escaneando and chave in self.pares_em_alerta:
            self.pares_em_alerta.discard(chave)

        return False

    def _esquecer_antigo(self, chave, agora):
        limite_tempo=agora-self.janela_segundos
        self.eventos_por_par[chave] = [
            (horario,porta)
            for horario,porta in self.eventos_por_par[chave]
            if horario>=limite_tempo
        ]