import sqlite3
import json
from modelos import RegistroPatoPrimordial
from helpers_app import resource_path

NOME_BANCO_DE_DADOS = resource_path('patos.db')

def conectar():
    conn = sqlite3.connect(NOME_BANCO_DE_DADOS) 
    return conn, conn.cursor()

def criar_tabela():
    conn, cursor = conectar()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drone_numero_serie TEXT NOT NULL,
            drone_fabricante TEXT,
            drone_pais_origem TEXT,
            altura_cm REAL,
            peso_g REAL,
            local_cidade TEXT,
            local_pais TEXT,
            local_latitude REAL,
            local_longitude REAL,
            precisao_m REAL,
            ponto_referencia TEXT,
            status_hibernacao TEXT,
            batimentos_cardiacos_bpm INTEGER,
            quantidade_mutacoes INTEGER,
            super_poder TEXT 
        )
    ''')
    conn.commit()
    conn.close()

def adicionar_pato(pato_obj):
    conn, cursor = conectar()
    super_poder_json = json.dumps(pato_obj.super_poder) if pato_obj.super_poder else None
    
    cursor.execute('''
        INSERT INTO patos (drone_numero_serie, drone_fabricante, drone_pais_origem, altura_cm, peso_g, 
                           local_cidade, local_pais, local_latitude, local_longitude, precisao_m, 
                           ponto_referencia, status_hibernacao, batimentos_cardiacos_bpm, 
                           quantidade_mutacoes, super_poder)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        pato_obj.drone['numero_serie'], pato_obj.drone['fabricante'], pato_obj.drone['pais_origem'],
        pato_obj.altura_cm, pato_obj.peso_g, pato_obj.localizacao['cidade'], pato_obj.localizacao['pais'],
        pato_obj.localizacao['latitude'], pato_obj.localizacao['longitude'], pato_obj.precisao_m,
        pato_obj.ponto_referencia, pato_obj.status_hibernacao, pato_obj.batimentos_cardiacos_bpm,
        pato_obj.quantidade_mutacoes, super_poder_json
    ))
    conn.commit()
    conn.close()

def listar_patos():
    conn, cursor = conectar()
    cursor.execute('SELECT * FROM patos')
    registros_db = cursor.fetchall()
    conn.close()
    
    catalogo = []
    for reg in registros_db:
        drone_info = {'numero_serie': reg[1], 'fabricante': reg[2], 'pais_origem': reg[3]}
        local_info = {'cidade': reg[6], 'pais': reg[7], 'latitude': reg[8], 'longitude': reg[9]}
        super_poder_info = json.loads(reg[15]) if reg[15] else None

        pato = RegistroPatoPrimordial(
            drone_info=drone_info, altura=reg[4], unidade_altura='cm', peso=reg[5], unidade_peso='g',
            local_info=local_info, precisao=reg[10], unidade_precisao='m', status=reg[12],
            qtd_mutacoes=reg[14], ponto_referencia=reg[11], batimentos_cardiacos=reg[13],
            super_poder_info=super_poder_info
        )
        pato.id = reg[0]
        catalogo.append(pato)
        
    return catalogo

def remover_pato(pato_id):
    conn, cursor = conectar()
    cursor.execute('DELETE FROM patos WHERE id = ?', (pato_id,))
    conn.commit()
    conn.close()


def atualizar_pato(pato_obj):
    conn, cursor = conectar()
    super_poder_json = json.dumps(pato_obj.super_poder) if pato_obj.super_poder else None

    cursor.execute('''
        UPDATE patos
        SET drone_numero_serie = ?, drone_fabricante = ?, drone_pais_origem = ?, 
            altura_cm = ?, peso_g = ?, local_cidade = ?, local_pais = ?, 
            local_latitude = ?, local_longitude = ?, precisao_m = ?, 
            ponto_referencia = ?, status_hibernacao = ?, batimentos_cardiacos_bpm = ?, 
            quantidade_mutacoes = ?, super_poder = ?
        WHERE id = ?
    ''', (
        pato_obj.drone['numero_serie'], pato_obj.drone['fabricante'], pato_obj.drone['pais_origem'],
        pato_obj.altura_cm, pato_obj.peso_g, pato_obj.localizacao['cidade'], pato_obj.localizacao['pais'],
        pato_obj.localizacao['latitude'], pato_obj.localizacao['longitude'], pato_obj.precisao_m,
        pato_obj.ponto_referencia, pato_obj.status_hibernacao, pato_obj.batimentos_cardiacos_bpm,
        pato_obj.quantidade_mutacoes, super_poder_json,
        pato_obj.id 
    ))
    conn.commit()
    conn.close()

def pesquisar_patos(coluna, valor):
    conn, cursor = conectar()
    query = f"SELECT * FROM patos WHERE {coluna} LIKE ?"
    cursor.execute(query, (f'%{valor}%',))
    registros_db = cursor.fetchall()
    conn.close()
    
    catalogo = []
    for reg in registros_db:
        drone_info = {'numero_serie': reg[1], 'fabricante': reg[2], 'pais_origem': reg[3]}
        local_info = {'cidade': reg[6], 'pais': reg[7], 'latitude': reg[8], 'longitude': reg[9]}
        super_poder_info = json.loads(reg[15]) if reg[15] else None
        pato = RegistroPatoPrimordial(
            drone_info=drone_info, altura=reg[4], unidade_altura='cm', peso=reg[5], unidade_peso='g',
            local_info=local_info, precisao=reg[10], unidade_precisao='m', status=reg[12],
            qtd_mutacoes=reg[14], ponto_referencia=reg[11], batimentos_cardiacos=reg[13],
            super_poder_info=super_poder_info
        )
        pato.id = reg[0]
        catalogo.append(pato)
        
    return catalogo

def editar_pato(pato_id, pato_obj):
    conn, cursor = conectar()
    super_poder_json = json.dumps(pato_obj.super_poder) if pato_obj.super_poder else None
    
    cursor.execute('''
        UPDATE patos 
        SET drone_numero_serie = ?, drone_fabricante = ?, drone_pais_origem = ?, 
            altura_cm = ?, peso_g = ?, local_cidade = ?, local_pais = ?, 
            local_latitude = ?, local_longitude = ?, precisao_m = ?, 
            ponto_referencia = ?, status_hibernacao = ?, batimentos_cardiacos_bpm = ?, 
            quantidade_mutacoes = ?, super_poder = ?
        WHERE id = ?
    ''', (
        pato_obj.drone['numero_serie'], pato_obj.drone['fabricante'], pato_obj.drone['pais_origem'],
        pato_obj.altura_cm, pato_obj.peso_g, pato_obj.localizacao['cidade'], pato_obj.localizacao['pais'],
        pato_obj.localizacao['latitude'], pato_obj.localizacao['longitude'], pato_obj.precisao_m,
        pato_obj.ponto_referencia, pato_obj.status_hibernacao, pato_obj.batimentos_cardiacos_bpm,
        pato_obj.quantidade_mutacoes, super_poder_json,
        pato_id
    ))
    conn.commit()
    conn.close()