from PyQt6.QtCore import QThread, pyqtSignal

from core.scanner_host import descobrir_hosts


class ThreadHosts(QThread):
    concluido = pyqtSignal(list)  # lista de (ip, mac)
    erro = pyqtSignal(str)

    def __init__(self, faixa_rede: str, interface=None):
        super().__init__()
        self.faixa_rede = faixa_rede
        self.interface = interface

    def run(self):
        try:
            hosts = descobrir_hosts(self.faixa_rede, iface = self.interface)
            self.concluido.emit(hosts)
        except Exception as erro:
            self.erro.emit(str(erro))