from configuracao import CONFIG
from geopy.distance import geodesic

BASE_DSIN_COORDS = tuple(CONFIG['base_dsin']['coordenadas'])

def calcular_distancia(pato_coords):
    try:
        dist = geodesic(BASE_DSIN_COORDS, pato_coords).kilometers
        return dist
    except Exception:
        return 0.0
def identificar_ambiente(pato, regras_ambiente):
    texto_local = f"{pato.localizacao['cidade']} {pato.localizacao['pais']} {pato.ponto_referencia}".lower()
    
    for nome_ambiente, dados_ambiente in regras_ambiente.items():
        if nome_ambiente == 'padrao':
            continue
        for palavra in dados_ambiente['palavras_chave']:
            if palavra in texto_local:
                return nome_ambiente.replace('_', ' ').title(), dados_ambiente
    return "Terreno Padrão", regras_ambiente['padrao']

def analisar_pato(pato):    
    regras_custo = CONFIG['regras_custo']
    regras_risco = CONFIG['regras_risco']
    regras_ciencia = CONFIG['regras_ciencia']
    regras_prioridade = CONFIG['regras_prioridade']
    regras_ambiente = CONFIG['regras_ambiente']
    
    # --- 1. CÁLCULO DO CUSTO OPERACIONAL ---
    custo_base = regras_custo['base']
    custo_altura = pato.altura_cm * regras_custo['por_cm_altura']
    custo_peso = (pato.peso_g / 100) * regras_custo['por_100g_peso']
    pato_coords = (pato.localizacao['latitude'], pato.localizacao['longitude'])
    distancia_km = calcular_distancia(pato_coords)
    custo_distancia = distancia_km * regras_custo['por_km_distancia']
    custo_genoma = (pato.quantidade_mutacoes ** regras_custo['mutacao_exponencial']) * regras_custo['mutacao_multiplicador']
    custo_total = custo_base + custo_altura + custo_peso + custo_distancia + custo_genoma

    # --- 2. CÁLCULO DO GRAU DE RISCO ---
    risco_total = 0
    status = pato.status_hibernacao
    
    if status == 'hibernação profunda':
        risco_total += regras_risco['status']['hibernacao_profunda']
    elif status == 'em transe':
        risco_total += regras_risco['status']['em_transe']
        if pato.batimentos_cardiacos_bpm:
            bpm_base = regras_risco['instabilidade_transe']['bpm_base']
            if pato.batimentos_cardiacos_bpm > bpm_base:
                multiplicador = regras_risco['instabilidade_transe']['multiplicador_por_bpm']
                risco_total += (pato.batimentos_cardiacos_bpm - bpm_base) * multiplicador
    elif status == 'desperto':
        risco_total += regras_risco.get('status', {}).get('desperto', 70) 

        if pato.super_poder and isinstance(pato.super_poder, dict): 
            regras_poder = regras_risco.get('poder_classificacao', {}) 
            
            try:
                classificacoes_poder = pato.super_poder.get('classificacoes', []) 
                
                print(f"DEBUG: Super Poder: {pato.super_poder}") 
                print(f"DEBUG: Classificacoes encontradas: {classificacoes_poder}")

                if isinstance(classificacoes_poder, list):
                    for classificacao in classificacoes_poder:
                        if classificacao in regras_poder:
                
                            print(f"DEBUG: Adicionando risco para classificação '{classificacao}': {regras_poder.get(classificacao)}")
                            risco_total += regras_poder[classificacao]
                else:
                    print(f"AVISO: 'classificacoes' em pato {pato.drone['numero_serie']} não é uma lista: {classificacoes_poder}")

                if not classificacoes_poder:
                    print(f"AVISO: Pato {pato.drone['numero_serie']} desperto não possui 'classificacoes' definidas ou a lista está vazia.")
                    
            except KeyError as e:
                print(f"ERRO INTERNO NO BLOCO DE CLASSIFICAÇÕES: Chave não encontrada - {e}. Continuando análise sem risco de classificação.")
            except Exception as e_geral:
                print(f"ERRO INESPERADO NO BLOCO DE CLASSIFICAÇÕES: {e_geral}. Continuando análise sem risco de classificação.")
    
    # --- 3. CÁLCULO DO GANHO EM CONHECIMENTO ---
    ciencia_total = pato.quantidade_mutacoes * regras_ciencia['por_mutacao']
    if status in regras_ciencia['status_bonus']:
        ciencia_total += regras_ciencia['status_bonus'][status]
    if pato.super_poder:
        regras_raridade = regras_ciencia['poder_raridade']
        for classificacao in pato.super_poder.get('classificacoes', []):
            if classificacao in regras_raridade:
                ciencia_total += regras_raridade[classificacao]
    nome_ambiente, dados_ambiente = identificar_ambiente(pato, regras_ambiente)
    
    custo_final = custo_total * dados_ambiente['mod_custo']
    risco_final = risco_total * dados_ambiente['mod_risco']

    # --- 4. CÁLCULO DO ÍNDICE DE PRIORIDADE ---
    denominador = custo_total + risco_total
    if denominador == 0:
        indice_prioridade = ciencia_total * 1000
    else:
        indice_prioridade = (ciencia_total * regras_prioridade['multiplicador_ciencia']) / denominador

    niveis = regras_prioridade['niveis']
    if indice_prioridade > niveis['maxima']:
        interpretacao = "PRIORIDADE MÁXIMA (Alvo Crítico)"
    elif niveis['alta'] <= indice_prioridade <= niveis['maxima']:
        interpretacao = "PRIORIDADE ALTA (Captura Recomendada)"
    elif niveis['media'] <= indice_prioridade < niveis['alta']:
        interpretacao = "PRIORIDADE MÉDIA (Alvo Oportunista)"
    else:
        interpretacao = "PRIORIDADE BAIXA (Apenas Monitorar)"
        
    # --- 5. DEFINIÇÃO DO PODERIO MILITAR ---
    if risco_total < 20:
        poderio_militar = "Equipe de Contenção Leve"
    elif 20 <= risco_total < 50:
        poderio_militar = "Unidade de Operações Especiais"
    elif 50 <= risco_total < 100:
        poderio_militar = "Batalhão de Contenção Pesada"
    else:
        poderio_militar = "Protocolo de Ameaça Nível Ômega"

    # --- 6. Compilando o relatório final ---
    analise = {
        "nome_pato": f"Espécime-{pato.drone['numero_serie']}",
        "ambiente_detectado": f"{nome_ambiente} (Custo x{dados_ambiente['mod_custo']}, Risco x{dados_ambiente['mod_risco']})",
        "distancia_km": distancia_km,
        "custo_operacional": custo_final,
        "grau_de_risco": risco_final,
        "ganho_conhecimento": ciencia_total,
        "poderio_militar": poderio_militar,
        "indice_prioridade": indice_prioridade,
        "interpretacao_prioridade": interpretacao
    }
    return analise