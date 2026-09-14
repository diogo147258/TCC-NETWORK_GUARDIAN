from dataclasses import dataclass
from enum import Enum
@dataclass
class PacoteInfo:
    horario: str
    ip_origem: str
    ip_destino: str
    porta_origem: int | None
    porta_destino: int | None
    protocolo: str
    tamanho: int
    eh_syn: bool = False

class Severidade(str, Enum):
    BAIXA = "Baixa"
    MEDIA = "Média"
    ALTA = "Alta"
    CRITICA = "Crítica"

    @property
    def cor(self) -> str:
        return {
            Severidade.BAIXA: "#22C55E",
            Severidade.MEDIA: "#F5A524",
            Severidade.ALTA: "#F97316",
            Severidade.CRITICA: "#EF4444",
        }[self]


@dataclass
class Alerta:
    tipo: str
    severidade: Severidade
    ip: str
    mensagem: str
    horario: float