from datetime import datetime
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QProgressBar, QPushButton, QSpinBox,
    QStackedWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from interface.tema import Cores
from interface.componentes.barra_lateral import BarraLateral
from interface.componentes.painel_indicador import PainelIndicador
from interface.componentes.grafico_linha import GraficoLinha
from interface.componentes.grafico_pizza import GraficoPizza
from interface.componentes.grafico_barra import GraficoBarras
from database.banco import Banco
from servicos.alertas import ServicoAlertas
from servicos.relatorio import gerar_relatorio
from PyQt6.QtGui import QIcon
from core.thread_captura import ThreadCaptura
from core.thread_scan import ThreadScanner
from core.thread_host import ThreadHosts          # <- linha nova
from core.captura import listar_interfaces


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Guardian")
        self.setWindowIcon(QIcon("imagens/icone identidade network guardian/network_guardian.ico"))


        self.banco = Banco()
        self.servico_alertas = ServicoAlertas()
        self.lista_de_alertas = []
        self.total_pacotes = 0
        self.total_alertas = 0
        self.alertas_ativos = 0

        self._montar_layout()

    # ------------------------------------------------------------------------------
    # tela principal layout

    def _montar_layout(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout_geral = QHBoxLayout(central)
        layout_geral.setContentsMargins(0, 0, 0, 0)

        self.barra_lateral = BarraLateral()
        layout_geral.addWidget(self.barra_lateral)

        self.paginas = QStackedWidget()
        layout_geral.addWidget(self.paginas)

        self.pagina_dashboard = self._montar_dashboard()
        self.pagina_alertas = self._montar_alertas()
        self.pagina_estatisticas = self._montar_estatisticas()
        self.pagina_scan = self._montar_scan()
        self.pagina_configuracoes = self._montar_configuracoes()

        self.paginas.addWidget(self.pagina_dashboard)
        self.paginas.addWidget(self.pagina_alertas)
        self.paginas.addWidget(self.pagina_estatisticas)
        self.paginas.addWidget(self.pagina_scan)
        self.paginas.addWidget(self.pagina_configuracoes)

        self.barra_lateral.pagina_selec.connect(self._trocar_pagina)

    def _trocar_pagina(self, identificador):
        if identificador == "dashboard":
            self.paginas.setCurrentWidget(self.pagina_dashboard)
        elif identificador == "alertas":
            self.paginas.setCurrentWidget(self.pagina_alertas)
        elif identificador == "estatisticas":
            self._atualizar_estatisticas()
            self.paginas.setCurrentWidget(self.pagina_estatisticas)
        elif identificador == "scan":
            self.paginas.setCurrentWidget(self.pagina_scan)
        elif identificador == "configuracoes":
            self.paginas.setCurrentWidget(self.pagina_configuracoes)

    # ------------------------------------------------------------------
    # Pag Dashboard

    def _montar_dashboard(self) -> QWidget:
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(24, 24, 24, 24)

        linha_topo = QHBoxLayout()
        titulo = QLabel("Dashboard")
        titulo.setStyleSheet(f"color: {Cores.TEXTO_PRIMARIO}; font-size: 18px; font-weight: 700;")
        linha_topo.addWidget(titulo)
        linha_topo.addStretch()

        self.botao_iniciar_captura = QPushButton("Iniciar Captura")
        self.botao_iniciar_captura.clicked.connect(self._ao_clicar_botao_captura)
        linha_topo.addWidget(self.botao_iniciar_captura)

        layout.addLayout(linha_topo)

        linha_paineis = QHBoxLayout()

        self.painel_pacotes = PainelIndicador("Pacotes/segundo", "dashboard", Cores.DESTAQUE, "0")
        self.painel_hosts = PainelIndicador("Hosts monitorados", "rede", Cores.SECUNDARIA, "0")
        self.painel_alertas_ativos = PainelIndicador("Alertas ativos", "alerta", Cores.SEVERIDADE_ALTA, "0")
        self.painel_alertas_totais = PainelIndicador("Alertas totais", "escudo", Cores.SEVERIDADE_MEDIA, "0")

        for painel in (self.painel_pacotes, self.painel_hosts, self.painel_alertas_ativos, self.painel_alertas_totais):
            linha_paineis.addWidget(painel)

        layout.addLayout(linha_paineis)

        linha_graficos = QHBoxLayout()

        self.grafico_trafego = GraficoLinha()
        linha_graficos.addWidget(
            self._envolver_com_titulo("Tráfego da Rede", self.grafico_trafego), stretch=2
        )

        self.grafico_protocolos = GraficoPizza()
        linha_graficos.addWidget(
            self._envolver_com_titulo("Protocolos", self.grafico_protocolos), stretch=1
        )

        layout.addLayout(linha_graficos)

        self.tabela_eventos = self._montar_tabela_eventos()
        layout.addWidget(self._envolver_com_titulo("Eventos de Ataque", self.tabela_eventos))
        layout.addWidget(self._montar_ips_ativos())
        return pagina

    def _montar_tabela_eventos(self) -> QTableWidget:
        tabela = QTableWidget(0, 4)
        tabela.setHorizontalHeaderLabels(["Horário", "IP Origem", "IP Destino", "Pacotes no segundo"])
        tabela.setAlternatingRowColors(True)
        tabela.verticalHeader().setVisible(False)
        tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        cabecalho = tabela.horizontalHeader()
        cabecalho.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        cabecalho.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        return tabela
    def _montar_ips_ativos(self) -> QWidget:
        conteudo = QWidget()
        layout_interno = QVBoxLayout(conteudo)
        layout_interno.setContentsMargins(0, 0, 0, 0)

        linha_controles = QHBoxLayout()
        self.campo_faixa_rede = QLineEdit()
        self.campo_faixa_rede.setPlaceholderText("ex.: 192.168.1.0/24")
        linha_controles.addWidget(self.campo_faixa_rede)

        self.botao_escanear_rede = QPushButton("Escanear Rede")
        self.botao_escanear_rede.clicked.connect(self._escanear_rede)
        linha_controles.addWidget(self.botao_escanear_rede)

        layout_interno.addLayout(linha_controles)

        self.tabela_hosts_ativos = QTableWidget(0, 2)
        self.tabela_hosts_ativos.setHorizontalHeaderLabels(["IP", "MAC"])
        self.tabela_hosts_ativos.setAlternatingRowColors(True)
        self.tabela_hosts_ativos.verticalHeader().setVisible(False)
        self.tabela_hosts_ativos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        cabecalho = self.tabela_hosts_ativos.horizontalHeader()
        cabecalho.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        cabecalho.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout_interno.addWidget(self.tabela_hosts_ativos)

        return self._envolver_com_titulo("IPs Ativos na Rede", conteudo)

    def _calcular_faixa_padrao(self) -> str:
        texto_interface = self.combo_interface.currentText()
        ip = texto_interface.split(" - ")[0].strip()
        partes = ip.split(".")
        if len(partes) == 4:
            return f"{partes[0]}.{partes[1]}.{partes[2]}.0/24"
        return "192.168.1.0/24"

    def _escanear_rede(self):
        faixa = self.campo_faixa_rede.text().strip()
        if not faixa:
            faixa = self._calcular_faixa_padrao()
            self.campo_faixa_rede.setText(faixa)
        interface_escolhida = self.combo_interface.currentData()
        self.botao_escanear_rede.setEnabled(False)
        self.tabela_hosts_ativos.setRowCount(0)

        self.thread_hosts = ThreadHosts(faixa, interface = interface_escolhida)
        self.thread_hosts.concluido.connect(self._ao_concluir_hosts)
        self.thread_hosts.erro.connect(self._ao_errar_hosts)
        self.thread_hosts.start()

    def _ao_concluir_hosts(self, hosts):
        self.botao_escanear_rede.setEnabled(True)
        self.tabela_hosts_ativos.setRowCount(0)

        for ip, mac in hosts:
            linha = self.tabela_hosts_ativos.rowCount()
            self.tabela_hosts_ativos.insertRow(linha)
            self.tabela_hosts_ativos.setItem(linha, 0, QTableWidgetItem(ip))
            self.tabela_hosts_ativos.setItem(linha, 1, QTableWidgetItem(mac))

        self.painel_hosts.definir_valor(str(len(hosts)))

    def _ao_errar_hosts(self, mensagem):
        self.botao_escanear_rede.setEnabled(True)
        print(f"Erro ao escanear rede: {mensagem}")
    def _ao_detectar_ataque(self, ip_origem, ip_destino, quantidade):
        tabela = self.tabela_eventos
        tabela.insertRow(0)

        horario = datetime.now().strftime("%H:%M:%S")
        valores = [horario, ip_origem, ip_destino, str(quantidade)]

        for coluna, valor in enumerate(valores):
            tabela.setItem(0, coluna, QTableWidgetItem(valor))

        if tabela.rowCount() > 50:
            tabela.removeRow(tabela.rowCount() - 1)

    def _ao_clicar_botao_captura(self):
        if hasattr(self, "thread_captura") and self.thread_captura.isRunning():
            self.thread_captura.parar()
            self.botao_iniciar_captura.setText("Parando...")
            self.botao_iniciar_captura.setEnabled(False)
        else:
            self._iniciar_captura()

    # ------------------------------------------------------------------
    # Pag Alertas

    def _montar_alertas(self) -> QWidget:
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(24, 24, 24, 24)

        linha_topo = QHBoxLayout()
        titulo = QLabel("Alertas")
        titulo.setStyleSheet(f"color: {Cores.TEXTO_PRIMARIO}; font-size: 18px; font-weight: 700;")
        linha_topo.addWidget(titulo)
        linha_topo.addStretch()

        botao_relatorio = QPushButton("Gerar Relatório PDF")
        botao_relatorio.clicked.connect(self._gerar_relatorio)
        linha_topo.addWidget(botao_relatorio)

        layout.addLayout(linha_topo)

        self.tabela_alertas = QTableWidget(0, 5)
        self.tabela_alertas.setHorizontalHeaderLabels(["Horário", "Tipo", "IP", "Severidade", "Mensagem"])
        self.tabela_alertas.setAlternatingRowColors(True)
        self.tabela_alertas.verticalHeader().setVisible(False)
        self.tabela_alertas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        cabecalho = self.tabela_alertas.horizontalHeader()
        cabecalho.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self._envolver_com_titulo("Histórico de Alertas", self.tabela_alertas))

        return pagina

    def _gerar_relatorio(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar relatório", "relatorio_network_guardian.pdf", "PDF (*.pdf)"
        )
        if not caminho:
            return

        gerar_relatorio(caminho, self.total_pacotes, self.total_alertas, self.lista_de_alertas)

    def _adicionar_linha_alerta(self, alerta):
        tabela = self.tabela_alertas
        tabela.insertRow(0)

        horario = datetime.fromtimestamp(alerta.horario).strftime("%H:%M:%S")
        tabela.setItem(0, 0, QTableWidgetItem(horario))
        tabela.setItem(0, 1, QTableWidgetItem(alerta.tipo))
        tabela.setItem(0, 2, QTableWidgetItem(alerta.ip))

        item_severidade = QTableWidgetItem(alerta.severidade.value)
        item_severidade.setForeground(QColor(alerta.severidade.cor))
        fonte = item_severidade.font()
        fonte.setBold(True)
        item_severidade.setFont(fonte)
        tabela.setItem(0, 3, item_severidade)

        tabela.setItem(0, 4, QTableWidgetItem(alerta.mensagem))

    # ------------------------------------------------------------------
    # Pag Estatísticas

    def _montar_estatisticas(self) -> QWidget:
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(24, 24, 24, 24)

        linha_topo = QHBoxLayout()
        titulo = QLabel("Estatísticas")
        titulo.setStyleSheet(f"color: {Cores.TEXTO_PRIMARIO}; font-size: 18px; font-weight: 700;")
        linha_topo.addWidget(titulo)
        linha_topo.addStretch()

        botao_atualizar = QPushButton("Atualizar")
        botao_atualizar.clicked.connect(self._atualizar_estatisticas)
        linha_topo.addWidget(botao_atualizar)

        layout.addLayout(linha_topo)

        linha_graficos = QHBoxLayout()

        self.grafico_top_ips = GraficoBarras(Cores.DESTAQUE)
        linha_graficos.addWidget(self._envolver_com_titulo("Top 10 IPs de Origem", self.grafico_top_ips))

        self.grafico_top_portas = GraficoBarras(Cores.SECUNDARIA)
        linha_graficos.addWidget(self._envolver_com_titulo("Top 10 Portas de Destino", self.grafico_top_portas))

        layout.addLayout(linha_graficos)
        layout.addStretch()

        return pagina

    def _atualizar_estatisticas(self):
        top_ips = self.banco.top_ip(limite=10)
        self.grafico_top_ips.definir_dados([(ip, total) for ip, total in top_ips])

        top_portas = self.banco.top_porta(limite=10)
        self.grafico_top_portas.definir_dados([(str(porta), total) for porta, total in top_portas])

    # --------------------------------------------------------------
    # Pag Port Scan

    def _montar_scan(self) -> QWidget:
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(24, 24, 24, 24)

        titulo = QLabel("Port Scan")
        titulo.setStyleSheet(f"color: {Cores.TEXTO_PRIMARIO}; font-size: 18px; font-weight: 700;")
        layout.addWidget(titulo)

        painel_formulario = QWidget()
        painel_formulario.setProperty("painel", "true")
        formulario = QFormLayout(painel_formulario)

        self.campo_ip_scan = QLineEdit()
        self.campo_ip_scan.setPlaceholderText("ex.: 127.0.0.1")
        formulario.addRow("IP alvo:", self.campo_ip_scan)

        self.campo_porta_inicio = QSpinBox()
        self.campo_porta_inicio.setRange(1, 65535)
        self.campo_porta_inicio.setValue(1)
        formulario.addRow("Porta inicial:", self.campo_porta_inicio)

        self.campo_porta_fim = QSpinBox()
        self.campo_porta_fim.setRange(1, 65535)
        self.campo_porta_fim.setValue(1024)
        formulario.addRow("Porta final:", self.campo_porta_fim)

        layout.addWidget(painel_formulario)

        self.botao_scan = QPushButton("Iniciar Varredura")
        self.botao_scan.clicked.connect(self._iniciar_scan)
        layout.addWidget(self.botao_scan)

        self.barra_progresso_scan = QProgressBar()
        self.barra_progresso_scan.setVisible(False)
        layout.addWidget(self.barra_progresso_scan)

        self.tabela_scan = QTableWidget(0, 2)
        self.tabela_scan.setHorizontalHeaderLabels(["Porta", "Status"])
        self.tabela_scan.setAlternatingRowColors(True)
        self.tabela_scan.verticalHeader().setVisible(False)
        self.tabela_scan.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._envolver_com_titulo("Resultado", self.tabela_scan))

        return pagina

    def _iniciar_scan(self):
        ip = self.campo_ip_scan.text().strip()
        if not ip:
            return

        self.botao_scan.setEnabled(False)
        self.barra_progresso_scan.setVisible(True)
        self.barra_progresso_scan.setRange(0, 0)
        self.tabela_scan.setRowCount(0)

        self.thread_scan = ThreadScanner(
            ip, self.campo_porta_inicio.value(), self.campo_porta_fim.value()
        )
        self.thread_scan.concluido.connect(self._ao_concluir_scan)
        self.thread_scan.erro.connect(self._ao_errar_scan)
        self.thread_scan.start()

    def _ao_concluir_scan(self, portas_abertas):
        self.barra_progresso_scan.setVisible(False)
        self.botao_scan.setEnabled(True)

        for porta in portas_abertas:
            linha = self.tabela_scan.rowCount()
            self.tabela_scan.insertRow(linha)
            self.tabela_scan.setItem(linha, 0, QTableWidgetItem(str(porta)))
            item_status = QTableWidgetItem("Aberta")
            item_status.setForeground(QColor(Cores.SEVERIDADE_BAIXA))
            self.tabela_scan.setItem(linha, 1, item_status)

    def _ao_errar_scan(self, mensagem):
        self.barra_progresso_scan.setVisible(False)
        self.botao_scan.setEnabled(True)
        print(f"Erro no scan: {mensagem}")

    # ------------------------------------------------------------------
    # Configurações

    def _montar_configuracoes(self) -> QWidget:
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(24, 24, 24, 24)

        titulo = QLabel("Configurações")
        titulo.setStyleSheet(f"color: {Cores.TEXTO_PRIMARIO}; font-size: 18px; font-weight: 700;")
        layout.addWidget(titulo)

        painel_formulario = QWidget()
        painel_formulario.setProperty("painel", "true")
        formulario = QFormLayout(painel_formulario)

        self.combo_interface = QComboBox()
        for rotulo, identificador in listar_interfaces():
            self.combo_interface.addItem(rotulo, userData=identificador)
        formulario.addRow("Interface de rede:", self.combo_interface)

        self.campo_limite_pps = QSpinBox()
        self.campo_limite_pps.setRange(1, 100000)
        self.campo_limite_pps.setValue(50)
        formulario.addRow("Limite de pacotes/s:", self.campo_limite_pps)

        self.campo_limite_zscore = QDoubleSpinBox()
        self.campo_limite_zscore.setRange(0.5, 10.0)
        self.campo_limite_zscore.setValue(3.0)
        formulario.addRow("Limite de z-score:", self.campo_limite_zscore)

        self.campo_janela_segundos = QSpinBox()
        self.campo_janela_segundos.setRange(1, 300)
        self.campo_janela_segundos.setValue(10)
        formulario.addRow("Janela de tempo do scan (s):", self.campo_janela_segundos)

        layout.addWidget(painel_formulario)

        botao_salvar = QPushButton("Salvar Configurações")
        botao_salvar.clicked.connect(self._salvar_configuracoes)
        layout.addWidget(botao_salvar)

        layout.addStretch()

        return pagina

    def _salvar_configuracoes(self):
        if not hasattr(self, "thread_captura"):
            return

        self.thread_captura.atualizar_configuracoes(
            limite_pps=self.campo_limite_pps.value(),
            limite_zscore=self.campo_limite_zscore.value(),
            janela_segundos=self.campo_janela_segundos.value(),
        )

    # ------------------------------------------------------------------
    # widget de titulo

    def _envolver_com_titulo(self, titulo: str, conteudo: QWidget) -> QWidget:
        painel = QWidget()
        painel.setProperty("painel", "true")

        layout = QVBoxLayout(painel)

        rotulo = QLabel(titulo)
        rotulo.setStyleSheet(f"color: {Cores.TEXTO_PRIMARIO}; font-size: 14px; font-weight: 700;")
        layout.addWidget(rotulo)

        layout.addWidget(conteudo)

        return painel

    # --------------------------------------------------------
    # captura em segundo plano e sinais

    def _iniciar_captura(self):
        interface_escolhida = self.combo_interface.currentData()
        self.thread_captura = ThreadCaptura(
            interface=interface_escolhida,
            limite_pps=self.campo_limite_pps.value(),
            limite_zscore=self.campo_limite_zscore.value(),
            janela_segundos=self.campo_janela_segundos.value(),
        )
        self.thread_captura.pacotes_capturados.connect(self._ao_receber_pacotes)
        self.thread_captura.estatisticas_prontas.connect(self._ao_fechar_janela)
        self.thread_captura.alerta_gerado.connect(self._ao_gerar_alerta)
        self.thread_captura.evento_ataque.connect(self._ao_detectar_ataque)
        self.thread_captura.finished.connect(self._ao_parar_captura)
        self.thread_captura.start()
        self.botao_iniciar_captura.setText("Parar Captura")
        self.botao_iniciar_captura.setEnabled(True)

    def _ao_parar_captura(self):
        self.botao_iniciar_captura.setText("Iniciar Captura")
        self.botao_iniciar_captura.setEnabled(True)

    def _ao_receber_pacotes(self, pacotes):
        self.total_pacotes += len(pacotes)

    def _ao_fechar_janela(self, pacotes_no_segundo):
        self.painel_pacotes.definir_valor(str(pacotes_no_segundo))
        self.grafico_trafego.adicionar_valor(pacotes_no_segundo)
        self._atualizar_protocolos()

    def _atualizar_protocolos(self):
        distribuicao = self.banco.distribuicao_protocolos()
        dados = [
            (protocolo, total, Cores.protocolo(protocolo))
            for protocolo, total in distribuicao
        ]
        self.grafico_protocolos.definir_dados(dados)

    def _ao_gerar_alerta(self, alerta):
        self.lista_de_alertas.append(alerta)

        self.total_alertas += 1
        self.alertas_ativos += 1
        self.painel_alertas_totais.definir_valor(str(self.total_alertas))
        self.painel_alertas_ativos.definir_valor(str(self.alertas_ativos))

        self.servico_alertas.notificar(alerta)

        if hasattr(self, "tabela_alertas"):
            self._adicionar_linha_alerta(alerta)