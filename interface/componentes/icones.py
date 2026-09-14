from PyQt6.QtCore import QByteArray, Qt
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

def carregar_icone(nome:str, cor:str, tamanho:int=24)->QIcon:
    caminho=f"imagens/icones/{nome}.svg"
    arquivo=open(caminho,"r",encoding="utf-8")
    conteudo_svg=arquivo.read()

    conteudo_colorido=conteudo_svg.replace("currentColor",cor)
    renderiza=QSvgRenderer(QByteArray(conteudo_colorido.encode("utf-8")))
    pixmap=QPixmap(tamanho,tamanho)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    renderiza.render(painter)
    painter.end()
    return QIcon(pixmap)