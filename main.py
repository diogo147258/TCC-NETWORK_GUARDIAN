import sys

from PyQt6.QtWidgets import QApplication
from interface.janela import JanelaPrincipal
from interface.tema import montar_folha_de_estilo


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(montar_folha_de_estilo())

    janela = JanelaPrincipal()
    janela.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()