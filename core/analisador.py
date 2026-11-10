import ipaddress

class AnalisadorDeTrafego:
    def __init__(self):
        self.pacotes = 0
        self.bytes = 0
        self.host = set()
        self.contagem_por_par = {}
        self.contagem_por_destino = {}

    def somar_pacotes(self, pacote):
        self.pacotes += 1
        self.bytes += pacote.tamanho
        self.host.add(pacote.ip_origem)
        self.host.add(pacote.ip_destino)

        par = (pacote.ip_origem, pacote.ip_destino)
        self.contagem_por_par[par] = self.contagem_por_par.get(par, 0) + 1

        destino = pacote.ip_destino
        self.contagem_por_destino[destino] = self.contagem_por_destino.get(destino, 0) + 1

    def par_mais_ativo(self):
        if not self.contagem_por_par:
            return None, None, 0
        par, quantidade = max(self.contagem_por_par.items(), key=lambda item: item[1])
        ip_origem, ip_destino = par
        return ip_origem, ip_destino, quantidade

    def destino_mais_atingido(self):
        if not self.contagem_por_destino:
            return None, 0
        return max(self.contagem_por_destino.items(), key=lambda item: item[1])

    def origem_principal(self, ip_destino):
        # de todos que mandaram pacote pro ip_destino, quem mandou mais
        candidatos = {
            origem: qtd
            for (origem, destino), qtd in self.contagem_por_par.items()
            if destino == ip_destino
        }
        if not candidatos:
            return None
        return max(candidatos, key=candidatos.get)

    def tempo_limite(self):
        pacotes = self.pacotes
        self.pacotes = 0
        self.bytes = 0
        self.host = set()
        self.contagem_por_par = {}
        self.contagem_por_destino = {}
        return pacotes

    def destino_mais_atingido(self):
        locais = {
            ip: qtd
            for ip, qtd in self.contagem_por_destino.items()
            if self._eh_local(ip)
        }
        if not locais:
            return None, 0
        return max(locais.items(), key=lambda item: item[1])

    @staticmethod
    def _eh_local(ip):
        try:
            endereco = ipaddress.ip_address(ip)
        except ValueError:
            return False
        return endereco.is_private and not endereco.is_multicast