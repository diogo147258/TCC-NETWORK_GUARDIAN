from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QButtonGroup,QGraphicsDropShadowEffect, QLabel, QPushButton, QVBoxLayout, QWidget
from interface.tema import Cores
from interface.componentes.icones import carregar_icone
from PyQt6.QtGui import QColor

Paginas = [
    ("dashboard","Dashboard","dashboard"),
    ("alertas","Alertas","alerta"),
    ("estatisticas","Estatisticas","estatisticas"),
    ("scan","Port Scan","scan"),
    ("configuracoes","Configuracoes","configuracoes")
]
class BarraLateral(QWidget):
    pagina_selec=pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)
        self.setStyleSheet(f"background-color: {Cores.FUNDO_PAINEL};")
        layout = QVBoxLayout(self)

        titulo = QLabel("Network Guardian")
        titulo.setStyleSheet(f"color: {Cores.DESTAQUE}; font-size: 17px; font-weight: 800; border: none;")
        titulo.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        efeito_neon = QGraphicsDropShadowEffect()
        efeito_neon.setColor(QColor(Cores.DESTAQUE))
        efeito_neon.setOffset(0, 0)
        efeito_neon.setBlurRadius(25)
        titulo.setGraphicsEffect(efeito_neon)

        layout.addWidget(titulo)
        self.botoes={}
        grupo=QButtonGroup(self)
        grupo.setExclusive(True)

        for identificador, nome, nome_icone in Paginas:
            botao=QPushButton(f"{nome}")
            botao.setCheckable(True)
            botao.setCursor(Qt.CursorShape.PointingHandCursor)
            botao.setIcon(carregar_icone(nome_icone,Cores.TEXTO_SECUNDARIO,18))
            botao.clicked.connect(lambda _clicado, id=identificador:self._selecionar(id))
            grupo.addButton(botao)
            layout.addWidget(botao)
            self.botoes[identificador]=botao
        layout.addStretch()
        self._selecionar("dashboard")

    def _selecionar(self, identificador:str):
        for id_botao, botao in self.botoes.items():
            ativo=id_botao==identificador
            botao.setChecked(ativo)
            cor=Cores.DESTAQUE if ativo else Cores.TEXTO_SECUNDARIO
            botao.setIcon(
                carregar_icone(
                    next(icone for id_p,_n,icone in Paginas if id_p==id_botao),
                    cor,18
                )
            )
        self.pagina_selec.emit(identificador)
