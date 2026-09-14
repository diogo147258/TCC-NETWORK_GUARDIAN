from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def gerar_relatorio(caminho_arquivo, total_pacotes, total_alertas, lista_de_alertas):
    documento = SimpleDocTemplate(caminho_arquivo, pagesize=A4)
    estilos = getSampleStyleSheet()

    conteudo = [
        Paragraph("Network Guardian - Relatório", estilos["Title"]),
        Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilos["Normal"]),
        Spacer(1, 20),
        Paragraph(f"Total de pacotes capturados: {total_pacotes}", estilos["Normal"]),
        Paragraph(f"Total de alertas gerados: {total_alertas}", estilos["Normal"]),
        Spacer(1, 20),
        Paragraph("Alertas", estilos["Heading2"]),
    ]

    dados_tabela = [["Horário", "Tipo", "IP", "Severidade", "Mensagem"]]
    for alerta in lista_de_alertas:
        horario = datetime.fromtimestamp(alerta.horario).strftime("%H:%M:%S")
        dados_tabela.append([horario, alerta.tipo, alerta.ip, alerta.severidade.value, alerta.mensagem])

    tabela = Table(dados_tabela, colWidths=[2 * cm, 2.5 * cm, 3 * cm, 2.5 * cm, 6 * cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B0F14")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    conteudo.append(tabela)

    documento.build(conteudo)