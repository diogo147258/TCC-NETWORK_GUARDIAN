import statistics
from collections import deque


class DetectorDdos:

    def __init__(
            self,
            limite=600,
            tamanho_historico=60,
            limite_zscore=3.0,
            amostras_minimas=30,
            piso_desvio=1.0,
            maximo_congelado=300,
            segundos_confirmar=3,
            atraso_aprendizado=5,
            volume_minimo_z=100,
    ):
        self.limite = limite
        self.limite_zscore = limite_zscore
        self.historico = deque(maxlen=tamanho_historico)
        self.amostras_minimas = amostras_minimas
        self.piso_desvio = piso_desvio
        self.maximo_congelado = maximo_congelado
        self.segundos_congelados = 0
        self.ultimo_zscore = 0.0
        self.segundos_confirmar = segundos_confirmar
        self.segundos_seguidos_z = 0
        self.segundos_seguidos_fixo = 0
        # cada segundo espera um pouco antes de entrar no historico;
        # se vier um alerta nesse meio tempo, ele e descartado
        self.atraso_aprendizado = atraso_aprendizado
        self.pendentes = deque()
        # abaixo desse volume nenhum aparelho esta sendo sobrecarregado,
        # entao o z-score nao conta (evita alerta com 15 pacotes numa rede parada)
        self.volume_minimo_z = volume_minimo_z

    # ------------------------------------------------------------------
    def analisar(self, pacotes_no_segundo):
        passou = pacotes_no_segundo >= self.limite
        z = self._calcular_zscore(pacotes_no_segundo)
        self.ultimo_zscore = z
        fugiu_media = z >= self.limite_zscore and pacotes_no_segundo >= self.volume_minimo_z

        # conta quantos segundos seguidos o limite fixo ficou estourado
        if passou:
            self.segundos_seguidos_fixo += 1
        else:
            self.segundos_seguidos_fixo = 0
        confirmou_fixo = self.segundos_seguidos_fixo >= self.segundos_confirmar

        # conta quantos segundos seguidos o z-score ficou alto
        if fugiu_media:
            self.segundos_seguidos_z += 1
        else:
            self.segundos_seguidos_z = 0
        confirmou_z = self.segundos_seguidos_z >= self.segundos_confirmar

        eh_ataque = confirmou_fixo or confirmou_z

        # segundo acima do limite fixo nao entra no historico, mesmo sem confirmar
        self._aprender(pacotes_no_segundo, eh_ataque or passou)

        if confirmou_fixo and fugiu_media:
            return True, "limite fixo e desvio da media"
        elif confirmou_fixo:
            return True, "limite fixo"
        elif confirmou_z:
            return True, "desvio da media (z-score)"
        else:
            return False, ""

    # ------------------------------------------------------------------
    def _aprender(self, pacotes_no_segundo, eh_ataque):
        if eh_ataque:
            self.pendentes.clear()
            self.segundos_congelados += 1
            if self.segundos_congelados > self.maximo_congelado:
                self.historico.append(pacotes_no_segundo)
            return

        self.segundos_congelados = 0
        self.pendentes.append(pacotes_no_segundo)
        # so entra no historico depois de alguns segundos sem alerta
        if len(self.pendentes) > self.atraso_aprendizado:
            self.historico.append(self.pendentes.popleft())

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
