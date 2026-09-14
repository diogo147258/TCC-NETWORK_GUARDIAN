from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from interface.tema import Cores
from interface.componentes.icones import carregar_icone


class PainelIndicador(QFrame):
    def __init__(self, titulo: str, nome_icone: str, cor: str = Cores.DESTAQUE, valor: str = "0"):
        super().__init__()
        self.setFixedHeight(100)
        self.setProperty("cartao", "true")

        layout_externo = QVBoxLayout(self)

        linha_topo = QHBoxLayout()

        rotulo_titulo = QLabel(titulo.upper())
        rotulo_titulo.setStyleSheet(f"color: {Cores.TEXTO_SECUNDARIO}; font-size: 11px; font-weight: 600;")
        linha_topo.addWidget(rotulo_titulo)
        linha_topo.addStretch()

        rotulo_icone = QLabel()
        icone = carregar_icone(nome_icone, cor, 18)
        rotulo_icone.setPixmap(icone.pixmap(18, 18))
        linha_topo.addWidget(rotulo_icone)

        layout_externo.addLayout(linha_topo)

        self.rotulo_valor = QLabel(valor)
        self.rotulo_valor.setStyleSheet(f"color: {Cores.TEXTO_PRIMARIO}; font-size: 26px; font-weight: 700;")
        layout_externo.addWidget(self.rotulo_valor)

    def definir_valor(self, novo_valor: str):
        self.rotulo_valor.setText(novo_valor)