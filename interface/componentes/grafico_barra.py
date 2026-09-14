from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget

from interface.tema import Cores


class GraficoBarras(QWidget):
    def __init__(self, cor: str = Cores.DESTAQUE):
        super().__init__()
        self.setMinimumHeight(200)
        self.cor = cor
        self.dados = []  # lista de tuplas (rotulo, valor)

    def definir_dados(self, dados: list):
        self.dados = dados
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if not self.dados:
            return

        maior_valor = max(valor for _rotulo, valor in self.dados) or 1
        largura_rotulo = 100
        altura_linha = self.height() / len(self.dados)
        altura_barra = min(16, altura_linha * 0.5)

        alinhar_direita_centro = int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        alinhar_esquerda_centro = int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        for indice, (rotulo, valor) in enumerate(self.dados):
            centro_y = altura_linha * indice + altura_linha / 2

            painter.setPen(QColor(Cores.TEXTO_SECUNDARIO))
            area_rotulo = QRectF(0, centro_y - altura_linha / 2, largura_rotulo - 10, altura_linha)
            painter.drawText(area_rotulo, alinhar_direita_centro, rotulo)

            largura_disponivel = self.width() - largura_rotulo - 50
            largura_barra = (valor / maior_valor) * largura_disponivel

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(self.cor))
            barra = QRectF(largura_rotulo, centro_y - altura_barra / 2, largura_barra, altura_barra)
            painter.drawRoundedRect(barra, altura_barra / 2, altura_barra / 2)

            painter.setPen(QColor(Cores.TEXTO_PRIMARIO))
            area_valor = QRectF(largura_rotulo + largura_barra + 8, centro_y - altura_linha / 2, 40, altura_linha)
            painter.drawText(area_valor, alinhar_esquerda_centro, str(valor))