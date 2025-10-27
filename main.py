# --- Imports ---
from modelos import RegistroPatoPrimordial
import database as db
import analisador_risco as ar
import sistema_combate as sc
from conversor import converter_altura, converter_peso

def solicitar_float(mensagem):
    while True:
        try:
            valor = float(input(mensagem))
            return valor
        except ValueError:
            print("Erro: Por favor, digite um número válido (ex: 12.34).")

def solicitar_int(mensagem):
    while True:
        try:
            valor = int(input(mensagem))
            return valor
        except ValueError:
            print("Erro: Por favor, digite um número inteiro válido (ex: 10).")

def solicitar_opcao_valida(mensagem, opcoes):
    while True:
        prompt = f"{mensagem} ({', '.join(opcoes)}): "
        escolha = input(prompt).lower()
        if escolha in opcoes:
            return escolha
        else:
            print(f"Erro: Opção inválida. Por favor, escolha uma das opções disponíveis.")

def adicionar_novo_registro(catalogo):
    print("\n--- Adicionando Novo Registro de Pato Primordial ---")
    drone_info = {'numero_serie': input("Número de série do drone: "), 'fabricante': input("Fabricante do drone: "), 'pais_origem': input("País de origem do drone: ")}
    altura = solicitar_float("Altura do pato: ")
    unidade_altura = solicitar_opcao_valida("Unidade da altura", ["cm", "pés"])
    peso = solicitar_float("Peso do pato (g): ")
    unidade_peso = solicitar_opcao_valida("Unidade do peso", ["g", "libras"])
    local_info = {'cidade': input("Cidade do avistamento: "), 'pais': input("País do avistamento: "), 'latitude': solicitar_float("Latitude (GPS): "), 'longitude': solicitar_float("Longitude (GPS): ")}
    precisao = solicitar_float("Precisão da localização: ")
    unidade_precisao = solicitar_opcao_valida("Unidade da precisão", ["m", "jardas"])
    ponto_referencia = input("Ponto de referência (deixe em branco se não houver): ") or None
    opcoes_status = ["desperto", "em transe", "hibernação profunda"]
    status = solicitar_opcao_valida("Status de hibernação", opcoes_status)
    batimentos_cardiacos = None
    super_poder_info = None
    if status in ["em transe", "hibernação profunda"]:
        batimentos_cardiacos = solicitar_int("Batimentos cardíacos (bpm): ")
    elif status == "desperto":
        print("--- Descrevendo o Super-Poder ---")
        nome_poder = input("Nome do poder: ")
        desc_poder = input("Descrição do poder: ")
        class_poder = input("Classificações (separadas por vírgula): ")
        super_poder_info = {'nome': nome_poder, 'descricao': desc_poder, 'classificacoes': [c.strip() for c in class_poder.split(',')]}
    qtd_mutacoes = solicitar_int("Quantidade de mutações: ")
    novo_pato = RegistroPatoPrimordial(drone_info, altura, unidade_altura, peso, unidade_peso, local_info, precisao, unidade_precisao, status, qtd_mutacoes, ponto_referencia, batimentos_cardiacos, super_poder_info)
    db.adicionar_pato(novo_pato)
    print("\n✅ Novo Pato Primordial adicionado ao catálogo com sucesso!")

def listar_todos(catalogo):
    if not catalogo:
        print("\nO catálogo está vazio.")
        return
    print(f"\n--- Exibindo {len(catalogo)} Registro(s) ---")
    for pato in catalogo:
        pato.exibir_relatorio()

def pesquisar_registros():
    print("\n--- Pesquisar no Catálogo ---")
    print("Escolha o critério de busca:")
    print("1. Por País do Avistamento")
    print("2. Por Status de Hibernação")

    print("3. Por Ponto de Referência")
    print("0. Voltar ao menu principal")
    
    escolha = input("Critério: ")
    resultados = []

    if escolha == '1':
        termo_busca = input("Digite o nome do país: ")
        resultados = db.pesquisar_patos('local_pais', termo_busca)
    
    elif escolha == '2':
        termo_busca = input("Digite o status (desperto, em transe, hibernação profunda): ")
        resultados = db.pesquisar_patos('status_hibernacao', termo_busca)
        
    elif escolha == '3':
        termo_busca = input("Digite uma palavra-chave do Ponto de Referência: ")
        resultados = db.pesquisar_patos('ponto_referencia', termo_busca)
            
    elif escolha == '0':
        return
        
    else:
        print("Critério inválido.")
        return

    if not resultados:
        print("\nNenhum registro encontrado para este critério.")
    else:
        listar_todos(resultados)

def editar_registro(catalogo):
    if not catalogo:
        print("\nO catálogo está vazio. Nada para editar.")
        return
    print("\nQual registro você deseja editar?")
    for i, pato in enumerate(catalogo):
        print(f"{i + 1}. Espécime-{pato.drone['numero_serie']} (Local: {pato.localizacao['cidade']})")
    max_index = len(catalogo)
    escolha_str = f"\nEscolha um número de 1 a {max_index} (ou 0 para cancelar): "
    try:
        index = solicitar_int(escolha_str)
        if index == 0: return
        if 1 <= index <= max_index:
            pato_escolhido = catalogo[index - 1]
            while True:
                print(f"\n--- Editando Espécime-{pato_escolhido.drone['numero_serie']} ---")
                print("1. Ponto de Referência\n2. Quantidade de Mutações\n3. Status de Hibernação\n4. Altura e Unidade\n5. Peso e Unidade\n0. Concluir Edição e Voltar")
                campo_escolha = input("Opção: ")
                if campo_escolha == '1':
                    novo_valor = input(f"Novo Ponto de Referência [{pato_escolhido.ponto_referencia}]: ")
                    if novo_valor: pato_escolhido.ponto_referencia = novo_valor
                elif campo_escolha == '2':
                    novo_valor_str = input(f"Nova Quantidade de Mutações [{pato_escolhido.quantidade_mutacoes}]: ")
                    if novo_valor_str:
                        try: pato_escolhido.quantidade_mutacoes = int(novo_valor_str)
                        except ValueError: print("Entrada inválida. Mantendo valor original.")
                elif campo_escolha == '3':
                    while True:
                        opcoes_status = ["desperto", "em transe", "hibernação profunda"]
                        novo_status = input(f"Novo Status ({', '.join(opcoes_status)}) [{pato_escolhido.status_hibernacao}]: ").lower()
                        if not novo_status: break
                        if novo_status in opcoes_status:
                            pato_escolhido.status_hibernacao = novo_status
                            if novo_status == "desperto":
                                pato_escolhido.batimentos_cardiacos_bpm = None
                                print("Status alterado. Insira as informações do super-poder.")
                                nome_poder = input("Nome do poder: "); desc_poder = input("Descrição do poder: "); class_poder = input("Classificações (separadas por vírgula): ")
                                pato_escolhido.super_poder = {'nome': nome_poder, 'descricao': desc_poder, 'classificacoes': [c.strip() for c in class_poder.split(',')]}
                            else:
                                pato_escolhido.super_poder = None
                                pato_escolhido.batimentos_cardiacos_bpm = solicitar_int("Batimentos cardíacos (bpm): ")
                            break
                        else: print("Erro: Status inválido. Tente novamente ou deixe em branco para manter o atual.")
                elif campo_escolha == '4':
                    nova_altura = solicitar_float("Digite a nova altura: ")
                    nova_unidade = solicitar_opcao_valida("Digite a nova unidade", ["cm", "pés"])
                    pato_escolhido.altura_cm = converter_altura(nova_altura, nova_unidade)
                    print(f"Altura atualizada para {pato_escolhido.altura_cm:.2f} cm.")
                elif campo_escolha == '5':
                    novo_peso = solicitar_float("Digite o novo peso: ")
                    nova_unidade = solicitar_opcao_valida("Digite a nova unidade", ["g", "libras"])
                    pato_escolhido.peso_g = converter_peso(novo_peso, nova_unidade)
                    print(f"Peso atualizado para {pato_escolhido.peso_g:.2f} g.")
                elif campo_escolha == '0':
                    print("\n✅ Alterações salvas no registro!")
                    break
                else: print("Opção inválida.")
        else: print("Número de registro inválido.")
    except ValueError: print("Entrada inválida.")

def remover_registro(catalogo):
    if not catalogo:
        print("\nO catálogo está vazio. Nada para remover.")
        return
    print("\nQual registro você deseja remover?")
    for i, pato in enumerate(catalogo):
        print(f"{i + 1}. Espécime-{pato.drone['numero_serie']} (Local: {pato.localizacao['cidade']})")
    max_index = len(catalogo)
    escolha_str = f"\nEscolha um número de 1 a {max_index} para remover (ou 0 para cancelar): "
    try:
        index = solicitar_int(escolha_str)
        if index == 0: return
        if 1 <= index <= max_index:
            confirmacao = input(f"Tem certeza que deseja remover o Espécime-{catalogo[index-1].drone['numero_serie']}? (s/n): ").lower()
            if confirmacao == 's':
                catalogo.pop(index - 1)
                print("\n✅ Registro removido com sucesso!")
            else:
                print("\nOperação de remoção cancelada.")
        else:
            print("Número inválido.")
    except ValueError:
        print("Entrada inválida.")

def exibir_relatorio_analise(analise):
    print("\n--- Relatório de Análise de Captura ---")
    print(f"Análise para: {analise['nome_pato']}")
    print("-" * 45)
    print(f"  > Ambiente Detectado: {analise['ambiente_detectado']}")
    print(f"  > Distância da Base: {analise['distancia_km']:.2f} km")
    print(f"  > Distância da Base: {analise['distancia_km']:.2f} km")
    print(f"  > Ganho em Conhecimento: {analise['ganho_conhecimento']:.1f} Pontos de Ciência")
    print(f"  > Custo Operacional: {analise['custo_operacional']:.1f} Pontos de Custo")
    print(f"  > Grau de Risco: {analise['grau_de_risco']:.1f} Pontos de Risco")
    print(f"  > Poderio Militar Necessário: {analise['poderio_militar']}")
    print("-" * 45)
    print(f"  >> Índice de Prioridade: {analise['indice_prioridade']:.2f}")
    print(f"  >> Recomendação: {analise['interpretacao_prioridade']}")
    print("-" * 45)

def analisar_registro_especifico(catalogo):
    if not catalogo:
        print("\nO catálogo está vazio. Adicione um registro primeiro.")
        return
    print("\nQual registro você deseja analisar?")
    for i, pato in enumerate(catalogo):
        print(f"{i + 1}. Espécime-{pato.drone['numero_serie']} (Local: {pato.localizacao['cidade']})")
    max_index = len(catalogo)
    escolha_str = f"\nEscolha um número de 1 a {max_index}: "
    try:
        index = solicitar_int(escolha_str) - 1
        if 0 <= index < max_index:
            pato_escolhido = catalogo[index]
            resultado_analise = ar.analisar_pato(pato_escolhido)
            exibir_relatorio_analise(resultado_analise)
        else:
            print(f"Número inválido. Por favor, escolha um número entre 1 e {max_index}.")
    except ValueError:
        print("Entrada inválida.")

def gerar_relatorio_prioridades(catalogo):
    if not catalogo:
        print("\nO catálogo está vazio.")
        return
    print("\nAnalisando todo o catálogo para gerar o relatório de prioridades...")
    lista_de_analises = [ar.analisar_pato(pato) for pato in catalogo]
    lista_de_analises.sort(key=lambda x: x['indice_prioridade'], reverse=True)
    print("\n--- RELATÓRIO DE ALVOS PRIORITÁRIOS ---")
    print("-" * 60)
    print(f"{'#':<4}{'Espécime':<25}{'Índice':<10}{'Recomendação'}")
    print("-" * 60)
    for i, analise in enumerate(lista_de_analises):
        rank = f"{i + 1}."
        nome = analise['nome_pato']
        indice = f"{analise['indice_prioridade']:.2f}"
        recomendacao = analise['interpretacao_prioridade']
        print(f"{rank:<4}{nome:<25}{indice:<10}{recomendacao}")
    print("-" * 60)

def iniciar_missao(catalogo):
    if not catalogo:
        print("\nO catálogo está vazio. Adicione um registro primeiro.")
        return
    print("\nQual espécime será o alvo da missão de captura?")
    for i, pato in enumerate(catalogo):
        print(f"{i + 1}. Espécime-{pato.drone['numero_serie']} (Status: {pato.status_hibernacao.title()})")
    max_index = len(catalogo)
    escolha_str = f"\nEscolha o alvo (1 a {max_index}): "
    try:
        index = solicitar_int(escolha_str) - 1
        if 0 <= index < max_index:
            pato_escolhido = catalogo[index]
            drone = sc.DroneDeCombate()
            pato_combatente = sc.PatoCombatente(pato_escolhido)
            sc.iniciar_simulacao(drone, pato_combatente)
        else:
            print("Alvo inválido.")
    except ValueError:
        print("Entrada inválida.")

def menu_principal():
    db.criar_tabela()
    while True:
        catalogo_de_patos = db.listar_patos()
        print("\n--- Sistema de Catálogo e Controle de Patos Primordiais ---")
        print("1. Adicionar Novo Registro\n2. Listar Todos os Registros\n3. Pesquisar no Catálogo\n4. Editar um Registro\n5. Remover um Registro\n6. Analisar Risco de Alvo Único\n7. Gerar Relatório de Prioridades\n8. Iniciar Missão de Captura\n9. Salvar e Sair")
        escolha = input("Escolha uma opção: ")
        if escolha == '1': adicionar_novo_registro(catalogo_de_patos)
        elif escolha == '2': listar_todos(catalogo_de_patos)
        elif escolha == '3': pesquisar_registros(catalogo_de_patos)
        elif escolha == '4': editar_registro(catalogo_de_patos)
        elif escolha == '5': remover_registro(catalogo_de_patos)
        elif escolha == '6': analisar_registro_especifico(catalogo_de_patos)
        elif escolha == '7': gerar_relatorio_prioridades(catalogo_de_patos)
        elif escolha == '8': iniciar_missao(catalogo_de_patos)
        elif escolha == '9':
            print("Encerrando o sistema...")
            break
        else: print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu_principal()