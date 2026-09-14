class AnalisadorDeTrafego:
    def __init__(self):
        self.pacotes = 0
        self.bytes = 0
        self.host = set()
        self.contagem_por_par = {}

    def somar_pacotes(self, pacote):
        self.pacotes += 1
        self.bytes += pacote.tamanho
        self.host.add(pacote.ip_origem)
        self.host.add(pacote.ip_destino)

        par = (pacote.ip_origem, pacote.ip_destino)
        self.contagem_por_par[par] = self.contagem_por_par.get(par, 0) + 1

    def par_mais_ativo(self):
        if not self.contagem_por_par:
            return None, None, 0
        par, quantidade = max(self.contagem_por_par.items(), key=lambda item: item[1])
        ip_origem, ip_destino = par
        return ip_origem, ip_destino, quantidade

    def tempo_limite(self):
        pacotes = self.pacotes
        self.pacotes = 0
        self.bytes = 0
        self.host = set()
        self.contagem_por_par = {}
        return pacotes