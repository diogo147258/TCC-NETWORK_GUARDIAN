import csv
import os
import threading
import time
import traceback
from datetime import datetime

from PyQt6.QtCore import QThread, pyqtSignal
from scapy.all import AsyncSniffer
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

    def __init__(self, interface=None, limite_pps=600, limite_zscore=3.0, janela_segundos=10):
        super().__init__()
        self.ips_excecao = set()
        self.interface = interface
        self.analisador = AnalisadorDeTrafego()
        self.detector_ddos = DetectorDdos(limite=limite_pps, tamanho_historico=60, limite_zscore=limite_zscore)
        self.detector_scan = DetectorPortScan(limite_porta=15, janela_segundos=janela_segundos)
        self.buffer_pacotes = []
        self.trava = threading.Lock()
        self._deve_parar = False
        self.sniffer = None
        self.ultimo_fechamento = None

    # ------------------------------------------------------------------
    # laco principal

    def run(self):
        os.makedirs("registros", exist_ok=True)
        self.banco = Banco()
        self._abrir_csv()
        self._iniciar_sniffer()
        self.ultimo_fechamento = time.perf_counter()

        # o relogio: fecha um segundo de cada vez, chegando pacote ou nao
        proximo = time.time() + 1.0
        while not self._deve_parar:
            espera = proximo - time.time()
            if espera > 0:
                time.sleep(espera)
            else:
                proximo = time.time()  # atrasou: recomeca o relogio
            proximo += 1.0

            try:
                self._fechar_segundo()
            except Exception:
                self._registrar_erro("_fechar_segundo")

            # se a placa de rede sumiu (wi-fi caiu, notebook economizando energia...),
            # o sniffer do scapy morre; aqui ele e registrado e reiniciado
            if not self._sniffer_vivo():
                erro_scapy = getattr(self.sniffer, "exception", None)
                self._registrar_erro("sniffer", f"o sniffer parou sozinho: {erro_scapy}\n")
                time.sleep(1)
                self._iniciar_sniffer()

        try:
            if self.sniffer is not None:
                self.sniffer.stop()
        except Exception:
            pass
        self.arquivo_csv.close()

    def parar(self):
        self._deve_parar = True

    # ------------------------------------------------------------------
    # sniffer, csv e log de erros

    def _iniciar_sniffer(self):
        try:
            self.sniffer = AsyncSniffer(prn=self._processar, iface=self.interface, store=False)
            self.sniffer.start()
        except Exception:
            self._registrar_erro("_iniciar_sniffer")

    def _sniffer_vivo(self):
        if self.sniffer is None:
            return False
        thread = getattr(self.sniffer, "thread", None)
        return thread is not None and thread.is_alive()

    def _abrir_csv(self):
        nome_arquivo = datetime.now().strftime("registros/captura_%Y%m%d_%H%M%S.csv")
        self.arquivo_csv = open(nome_arquivo, "w", newline="", encoding="utf-8")
        self.escritor_csv = csv.writer(self.arquivo_csv, delimiter=";")
        self.escritor_csv.writerow([
            "horario", "intervalo_s", "pacotes_total", "ip_destino_top", "pacotes_destino_top",
            "zscore", "tamanho_historico", "alerta", "motivo", "processamento_ms",
        ])

    def _registrar_erro(self, onde, mensagem=None):
        try:
            with open("registros/erros.log", "a", encoding="utf-8") as arquivo:
                arquivo.write(f"\n[{datetime.now():%d/%m %H:%M:%S}] problema em {onde}\n")
                arquivo.write(mensagem or traceback.format_exc())
        except Exception:
            pass

    # ------------------------------------------------------------------
    # roda na thread do Scapy, uma vez para cada pacote

    def _processar(self, pacote_scapy):
        try:
            pacote = converter_pacote(pacote_scapy)
            if pacote is None:
                return
            eh_excecao = pacote.ip_origem in self.ips_excecao or pacote.ip_destino in self.ips_excecao

            with self.trava:
                if not eh_excecao:
                    self.analisador.somar_pacotes(pacote)  # so conta se nao for excecao
                self.buffer_pacotes.append(pacote)  # mas salva no banco sempre
            if eh_excecao:
                return

            deve_analisar_scan = pacote.porta_destino is not None and (
                    pacote.protocolo != "TCP" or pacote.eh_syn
            )
            if deve_analisar_scan:
                eh_scan = self.detector_scan.processar_pacote(pacote)
                if eh_scan:
                    alerta = Alerta(
                        tipo="Port_Scan",
                        severidade=Severidade.MEDIA,
                        ip=pacote.ip_origem,
                        mensagem=f"Possível Port Scan — origem={pacote.ip_origem} destino={pacote.ip_destino}",
                        horario=pacote.horario,
                    )
                    self.alerta_gerado.emit(alerta)
        except Exception:
            self._registrar_erro("_processar")

    # ------------------------------------------------------------------
    # roda na QThread, uma vez por segundo

    def _fechar_segundo(self):
        inicio = time.perf_counter()

        with self.trava:
            ip_destino_top, pacotes_destino_top = self.analisador.destino_mais_atingido()
            ip_origem_top = self.analisador.origem_principal(ip_destino_top)
            pacotes_contados = self.analisador.tempo_limite()
            pacotes_para_salvar = self.buffer_pacotes
            self.buffer_pacotes = []

            # quanto tempo passou de verdade desde o ultimo fechamento
            agora = time.perf_counter()
            intervalo = max(agora - self.ultimo_fechamento, 0.2)
            self.ultimo_fechamento = agora

        # se o computador atrasou e passou mais de 1 segundo, a contagem e dividida
        # pelo tempo real, para continuar sendo "pacotes por segundo"
        pacotes_no_segundo = round(pacotes_contados / intervalo)
        pacotes_destino_top = round(pacotes_destino_top / intervalo)

        if pacotes_para_salvar:
            self.banco.salvar_pacotes(pacotes_para_salvar)
            self.pacotes_capturados.emit(pacotes_para_salvar)

        # o grafico e o indicador continuam mostrando o total da interface
        self.estatisticas_prontas.emit(pacotes_no_segundo)

        # a deteccao usa so o destino da rede local que mais recebeu pacotes
        eh_ataque, motivo = self.detector_ddos.analisar(pacotes_destino_top)

        self.escritor_csv.writerow([
            datetime.now().strftime("%H:%M:%S"),
            f"{intervalo:.2f}",
            pacotes_no_segundo,
            ip_destino_top or "-",
            pacotes_destino_top,
            f"{self.detector_ddos.ultimo_zscore:.2f}",
            len(self.detector_ddos.historico),
            int(eh_ataque),
            motivo,
            round((time.perf_counter() - inicio) * 1000),
        ])
        self.arquivo_csv.flush()

        if eh_ataque:
            self.evento_ataque.emit(
                ip_origem_top or "-", ip_destino_top or "-", pacotes_destino_top
            )

            alerta = Alerta(
                tipo="DDoS",
                severidade=self._definir_severidade(motivo),
                ip=ip_destino_top or "rede",
                mensagem=f"Possível DDoS contra {ip_destino_top} — motivo: {motivo}",
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

    def atualizar_configuracoes(self, limite_pps, limite_zscore, janela_segundos, ips_excecao=None):
        self.detector_ddos.limite = limite_pps
        self.detector_ddos.limite_zscore = limite_zscore
        self.detector_scan.janela_segundos = janela_segundos
        if ips_excecao is not None:
            self.ips_excecao = set(ips_excecao)
