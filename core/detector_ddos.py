import statistics
from collections import deque

class DetectorDdos:
    def __init__(self, limite=1000, tamanho_historico=60, limite_zscore=3.0):
        self.limite=limite
        self.limite_zscore=limite_zscore
        self.historico=deque(maxlen=tamanho_historico)

    def analisar(self, pacotes_no_segundo):
        passou = pacotes_no_segundo>=self.limite
        z= self._calcular_zscore(pacotes_no_segundo)
        fugiu_media=z>=self.limite_zscore
        self.historico.append(pacotes_no_segundo)

        if passou and fugiu_media:
            return True, "limite fixo e desvio da media"
        elif passou:
            return True, "limite fixo"
        elif fugiu_media:
            return True, "desvio da media (z-score)"
        else:
            return False,""

    def _calcular_zscore(self,valor_atual):
        if len(self.historico) <2:
            return 0.0
        media= statistics.mean(self.historico)
        desvio= statistics.pstdev(self.historico)

        if desvio == 0:
            return 0.0
        return (valor_atual - media)/desvio