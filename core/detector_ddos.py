import statistics
from collections import deque


class DetectorDdos:

    def __init__(
        self,
        limite=1000,
        tamanho_historico=60,
        limite_zscore=3.0,
        amostras_minimas=30,
        piso_desvio=1.0,
        maximo_congelado=300,
    ):
        self.limite = limite
        self.limite_zscore = limite_zscore
        self.historico = deque(maxlen=tamanho_historico)
        self.amostras_minimas = amostras_minimas
        self.piso_desvio = piso_desvio
        self.maximo_congelado = maximo_congelado
        self.segundos_congelados = 0
        self.ultimo_zscore = 0.0

    # ------------------------------------------------------------------
    def analisar(self, pacotes_no_segundo):
        """Devolve (eh_ataque, motivo) — mesma assinatura da versão anterior."""
        passou = pacotes_no_segundo >= self.limite
        z = self._calcular_zscore(pacotes_no_segundo)
        self.ultimo_zscore = z
        fugiu_media = z >= self.limite_zscore

        eh_ataque = passou or fugiu_media
        self._aprender(pacotes_no_segundo, eh_ataque)

        if passou and fugiu_media:
            return True, "limite fixo e desvio da media"
        elif passou:
            return True, "limite fixo"
        elif fugiu_media:
            return True, "desvio da media (z-score)"
        else:
            return False, ""

    # ------------------------------------------------------------------
    def _aprender(self, pacotes_no_segundo, eh_ataque):
        if not eh_ataque:
            self.historico.append(pacotes_no_segundo)
            self.segundos_congelados = 0
            return
        self.segundos_congelados += 1
        if self.segundos_congelados > self.maximo_congelado:
            self.historico.append(pacotes_no_segundo)

    # ------------------------------------------------------------------
    def _calcular_zscore(self, valor_atual):
        if len(self.historico) < max(2, self.amostras_minimas):
            return 0.0

        media = statistics.mean(self.historico)
        desvio = statistics.stdev(self.historico)
        desvio = max(desvio, self.piso_desvio)

        return (valor_atual - media) / desvio

    # ------------------------------------------------------------------
    def esta_aquecido(self):
        return len(self.historico) >= max(2, self.amostras_minimas)

    def progresso_do_aquecimento(self):
        return len(self.historico), max(2, self.amostras_minimas)