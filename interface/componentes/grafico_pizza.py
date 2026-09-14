from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget
from interface.tema import Cores


class GraficoPizza(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 240)
        self.dados = []  # lista de tuplas (rotulo, valor, cor)

    def definir_dados(self, dados: list):
        self.dados = dados
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if not self.dados:
            return

        altura_legenda = 26
        area_donut_altura = self.height() - altura_legenda

        total = sum(valor for _rotulo, valor, _cor in self.dados)
        if total > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            diametro = min(self.width(), area_donut_altura) - 20
            retangulo = QRectF((self.width() - diametro) / 2, 10, diametro, diametro)

            angulo_atual = 90 * 16
            for _rotulo, valor, cor in self.dados:
                fatia = int((valor / total) * 360 * 16)
                painter.setBrush(QColor(cor))
                painter.drawPie(retangulo, angulo_atual, -fatia)
                angulo_atual -= fatia

            self._furar_o_meio(painter, retangulo, diametro)

        self._legenda(painter, area_donut_altura, altura_legenda)

    def _furar_o_meio(self, painter: QPainter, retangulo: QRectF, diametro: float):
        proporcao_buraco = 0.55
        diametro_buraco = diametro * proporcao_buraco
        margem = (diametro - diametro_buraco) / 2

        buraco = QRectF(
            retangulo.x() + margem, retangulo.y() + margem,
            diametro_buraco, diametro_buraco,
        )
        painter.setBrush(QColor(Cores.FUNDO_PAINEL))
        painter.drawEllipse(buraco)

    def _legenda(self, painter: QPainter, y_inicio: float, altura_legenda: float):
        quadrado = 10
        espaco = 10

        fonte = painter.font()
        fonte.setPixelSize(11)
        painter.setFont(fonte)
        metrica = painter.fontMetrics()

        larguras_item = [
            quadrado + 4 + metrica.horizontalAdvance(rotulo)
            for rotulo, _valor, _cor in self.dados
        ]
        largura_total = sum(larguras_item) + espaco * (len(self.dados) - 1)
        x = max(4, (self.width() - largura_total) / 2)

        alinhamento = int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        for (rotulo, _valor, cor), largura_item in zip(self.dados, larguras_item):
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(cor))
            painter.drawRect(QRectF(x, y_inicio + altura_legenda / 2 - quadrado / 2, quadrado, quadrado))

            painter.setPen(QColor(Cores.TEXTO_SECUNDARIO))
            painter.drawText(
                QRectF(x + quadrado + 4, y_inicio, largura_item, altura_legenda),
                alinhamento,
                rotulo,
            )
            x += largura_item + espaco