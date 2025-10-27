# Arquivo: migracao.py
import json
import database

print("Iniciando migração de dados do JSON para o SQLite...")

database.criar_tabela()

try:
    with open('catalogo_patos.json', 'r', encoding='utf-8') as f:
        dados_json = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    print("Arquivo 'catalogo_patos.json' não encontrado ou inválido. Nenhuma migração a fazer.")
    dados_json = []

from modelos import RegistroPatoPrimordial
catalogo_antigo = []
for dados_pato in dados_json:
    pato = RegistroPatoPrimordial(
        drone_info=dados_pato['drone_info'],
        altura=dados_pato['altura_cm'], unidade_altura='cm',
        peso=dados_pato['peso_g'], unidade_peso='g',
        local_info=dados_pato['localizacao'],
        precisao=dados_pato['precisao_m'], unidade_precisao='m',
        status=dados_pato['status_hibernacao'],
        qtd_mutacoes=dados_pato['quantidade_mutacoes'],
        ponto_referencia=dados_pato.get('ponto_referencia'),
        batimentos_cardiacos=dados_pato.get('batimentos_cardiacos_bpm'),
        super_poder_info=dados_pato.get('super_poder')
    )
    catalogo_antigo.append(pato)

if catalogo_antigo:
    print(f"Encontrados {len(catalogo_antigo)} registros no JSON. Inserindo no banco de dados...")
    for pato in catalogo_antigo:
        database.adicionar_pato(pato)
    print("Migração concluída com sucesso!")
else:
    print("Nenhum dado para migrar.")