import time
from PyQt6.QtCore import QThread, pyqtSignal
from scapy.all import sniff
from core.captura import converter_pacote
from core.analisador import AnalisadorDeTrafego
from core.detector_ddos import DetectorDdos
from core.detector_portScan import DetectorPortScan
from database.banco import Banco
from database.modelo import Alerta, Severidade


class ThreadCaptura(QThread):
    pacotes_capturados = pyqtSignal(list)
    estatisticas_prontas = pyqtSignal(int)
    alerta_gerado = pyqtSignal(object)
    evento_ataque = pyqtSignal(str, str, int)

    def __init__(self, interface=None, limite_pps=50, limite_zscore=3.0, janela_segundos=10):
        super().__init__()
        self.interface = interface
        self.analisador = AnalisadorDeTrafego()
        self.detector_ddos = DetectorDdos(limite=limite_pps, tamanho_historico=60, limite_zscore=limite_zscore)
        self.detector_scan = DetectorPortScan(limite_porta=15, janela_segundos=janela_segundos)
        self.inicio_janela = time.time()
        self.buffer_pacotes = []
        self.ultimo_envio_pacotes = time.time()
        self._deve_parar=False

    def run(self):
        self.banco = Banco()
        while not self._deve_parar:
            sniff(prn=self._processar, timeout=1, iface=self.interface, store=False)

    def parar(self):
        self._deve_parar = True

    def _processar(self, pacote_scapy):
        pacote = converter_pacote(pacote_scapy)
        if pacote is None:
            return

        self.analisador.somar_pacotes(pacote)
        self.buffer_pacotes.append(pacote)

        agora = time.time()
        if agora - self.ultimo_envio_pacotes >= 0.5:
            self.banco.salvar_pacotes(self.buffer_pacotes)
            self.pacotes_capturados.emit(self.buffer_pacotes)
            self.buffer_pacotes = []
            self.ultimo_envio_pacotes = agora

        deve_analisar_scan = pacote.porta_destino is not None and (
                pacote.protocolo != "TCP" or pacote.eh_syn
        )
        if deve_analisar_scan:
            eh_scan = self.detector_scan.processar_pacote(pacote)
            if eh_scan:
                alerta = Alerta(
                    tipo="port_scan",
                    severidade=Severidade.MEDIA,
                    ip=pacote.ip_origem,
                    mensagem=f"Possível Port Scan — origem={pacote.ip_origem} destino={pacote.ip_destino}",
                    horario=pacote.horario,
                )
                self.alerta_gerado.emit(alerta)

        if time.time() - self.inicio_janela >= 1.0:
            ip_origem_top, ip_destino_top, _qtd_top = self.analisador.par_mais_ativo()
            pacotes_no_segundo = self.analisador.tempo_limite()
            self.inicio_janela = time.time()
            self.estatisticas_prontas.emit(pacotes_no_segundo)

            eh_ataque, motivo = self.detector_ddos.analisar(pacotes_no_segundo)
            if eh_ataque:
                self.evento_ataque.emit(
                    ip_origem_top or "-", ip_destino_top or "-", pacotes_no_segundo
                )

                alerta = Alerta(
                    tipo="ddos",
                    severidade=self._definir_severidade(motivo),
                    ip="rede",
                    mensagem=f"Possível DDoS — motivo: {motivo}",
                    horario=time.time(),
                )
                self.alerta_gerado.emit(alerta)

    def _definir_severidade(self, motivo: str) -> Severidade:
        if "limite fixo e desvio" in motivo:
            return Severidade.CRITICA
        elif "limite fixo" in motivo:
            return Severidade.ALTA
        else:
            return Severidade.MEDIA

    def atualizar_configuracoes(self, limite_pps, limite_zscore, janela_segundos):
        self.detector_ddos.limite = limite_pps
        self.detector_ddos.limite_zscore = limite_zscore
        self.detector_scan.janela_segundos = janela_segundos