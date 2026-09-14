from __future__ import annotations


class Cores:
    FUNDO_BASE = "#0B0F14"
    FUNDO_PAINEL = "#121821"
    FUNDO_PAINEL_ALT = "#161D28"
    FUNDO_ELEVADO = "#1B2330"
    BORDA = "#232B38"
    BORDA_SUAVE = "#1B222D"

    TEXTO_PRIMARIO = "#E6EDF3"
    TEXTO_SECUNDARIO = "#8B98A9"
    TEXTO_APAGADO = "#5B6675"

    DESTAQUE = "#22D3EE"
    DESTAQUE_ESCURO = "#0E7490"
    FUNDO_DESTAQUE_SUAVE = "#122A31"
    SECUNDARIA = "#6366F1"

    SEVERIDADE_BAIXA = "#22C55E"
    SEVERIDADE_MEDIA = "#F5A524"
    SEVERIDADE_ALTA = "#F97316"
    SEVERIDADE_CRITICA = "#EF4444"

    @staticmethod
    def severidade(nome: str) -> str:
        return {
            "Baixa": Cores.SEVERIDADE_BAIXA,
            "Média": Cores.SEVERIDADE_MEDIA,
            "Alta": Cores.SEVERIDADE_ALTA,
            "Crítica": Cores.SEVERIDADE_CRITICA,
        }.get(nome, Cores.TEXTO_SECUNDARIO)

    @staticmethod
    def protocolo(nome: str) -> str:
        return {
            "TCP": Cores.DESTAQUE,
            "UDP": Cores.SECUNDARIA,
            "ICMP": Cores.SEVERIDADE_MEDIA,
        }.get(nome, Cores.TEXTO_APAGADO)


class Fontes:
    TITULO = "Segoe UI Semibold, Inter, Arial"
    TEXTO = "Segoe UI, Inter, Arial"
    MONO = "Consolas, JetBrains Mono, Courier New"


RAIO = 10
RAIO_PEQUENO = 6


def montar_folha_de_estilo() -> str:
    return f"""
        QMainWindow {{
            background-color: {Cores.FUNDO_BASE};
        }}

        QWidget[painel="true"] {{
            background-color: {Cores.FUNDO_PAINEL};
            border: 1px solid {Cores.BORDA};
            border-radius: {RAIO}px;
        }}

        QFrame[painel="true"] {{
            background-color: {Cores.FUNDO_PAINEL};
            border: 1px solid {Cores.BORDA};
            border-radius: {RAIO}px;
        }}

        QLabel {{
            border: none;
        }}
    """