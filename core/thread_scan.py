from PyQt6.QtCore import QThread , pyqtSignal
from core.scanner_ativo import varrer_portas

class ThreadScanner(QThread):
    concluido=pyqtSignal(list)
    erro=pyqtSignal(str)

    def __init__(self, ip:str,porta_inicio:int,porta_fim:int):
        super().__init__()
        self.ip = ip
        self.porta_inicio = porta_inicio
        self.porta_fim = porta_fim

    def run(self):
        try:
            abertas = varrer_portas(self.ip,self.porta_inicio,self.porta_fim)
            self.concluido.emit(abertas)
        except Exception as erro:
            self.erro.emit(str(erro))
