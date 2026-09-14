from collections import deque
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QPaintEvent
from PyQt6.QtWidgets import QWidget
from interface.tema import Cores

class GraficoLinha(QWidget):
    def __init__(self, tamanho_max:int=60):
        super().__init__()
        self.setMinimumHeight(200)
        self.valores=deque(maxlen=tamanho_max)

    def adicionar_valor(self, valor:float):
        self.valores.append(valor)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing,True)

        if len(self.valores) <2:
            return

        maximo=max(self.valores) or 1
        largura=self.width()
        altura=self.height()

        pontos=[]
        for indice,valor in enumerate(self.valores):
            x=(indice/(len(self.valores)-1))*largura
            y=altura-(valor/maximo)*altura
            pontos.append(QPointF(x,y))

        caneta=QPen(QColor(QColor(Cores.DESTAQUE)))
        caneta.setWidthF(2.0)
        caneta.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(caneta)

        for i in range(len(pontos)-1):
            painter.drawLine(pontos[i],pontos[i+1])
