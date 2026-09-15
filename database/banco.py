import sqlite3
import os
import sys
from database.modelo import PacoteInfo


try:
    DIRETORIO_EXECUTAVEL = os.path.dirname(sys.argv[0])   # pasta onde o .exe realmente está
except Exception:
    DIRETORIO_EXECUTAVEL = os.path.dirname(os.path.abspath(__file__))

class Banco:
    def __init__(self, caminho="./database/DB_Criado/network_guardian.db"):
        self.conexao = sqlite3.connect(caminho, timeout=10)
        self.conexao.execute("PRAGMA journal_mode=WAL;")
        self._criar_tabelas()

    def _criar_tabelas(self):
        self.conexao.execute("""
        CREATE TABLE IF NOT EXISTS pacotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            horario REAL,
            ip_origem TEXT,
            ip_destino  TEXT,
            porta_origem INTEGER,
            porta_destino  INTEGER,
            protocolo TEXT,
            tamanho INTEGER
        )
        """)
        self.conexao.commit()

    def salvar_pacotes(self, pacotes: list):
        if not pacotes:
            return

        self.conexao.executemany("""
                                 INSERT INTO pacotes
                                    (horario, ip_origem, ip_destino,porta_origem, porta_destino, protocolo, tamanho)
                                 VALUES (?,?,?,?,?,?,?)
                                 """,
                                 [
                                     (p.horario, p.ip_origem, p.ip_destino, p.porta_origem,
                                      p.porta_destino, p.protocolo, p.tamanho)
                                     for p in pacotes
                                 ])
        self.conexao.commit()
    def listar_pacotes(self):
        cursor = self.conexao.execute("SELECT * FROM pacotes")
        return cursor.fetchall()
    def top_ip(self, limite=10):
        cursor = self.conexao.execute("""
        SELECT ip_origem, COUNT(*) as total
        FROM pacotes
        WHERE porta_destino IS NOT NULL
        GROUP BY ip_origem
        ORDER BY total DESC
        LIMIT ?
        """,(limite,))
        return cursor.fetchall()
    def top_porta(self, limite=10):
        cursor = self.conexao.execute("""
        SELECT porta_destino, COUNT(*) as total
        FROM pacotes 
        WHERE porta_destino IS NOT NULL
        GROUP BY porta_destino
        ORDER BY total DESC
        LIMIT ?
        """, (limite,))
        return cursor.fetchall()

    def distribuicao_protocolos(self):
        cursor = self.conexao.execute("""
            SELECT protocolo, COUNT(*) as total
            FROM pacotes
            GROUP BY protocolo
            ORDER BY total DESC
        """)
        return cursor.fetchall()