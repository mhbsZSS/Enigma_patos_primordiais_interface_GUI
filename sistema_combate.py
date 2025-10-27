import random

class Arma:
    def __init__(self, nome, dano_min, dano_max, custo_bateria, usos, efeito_especial=None):
        self.nome = nome
        self.dano_min = dano_min
        self.dano_max = dano_max
        self.custo_bateria = custo_bateria
        self.usos_restantes = usos
        self.efeito_especial = efeito_especial

    def calcular_dano(self):
        return random.randint(self.dano_min, self.dano_max)

class DroneDeCombate:
    def __init__(self):
        self.integridade = 100
        self.bateria = 100
        self.combustivel = 100
        self.inventario = [
            Arma(nome="Canhão Sônico", dano_min=10, dano_max=20, custo_bateria=5, usos=float('inf'), efeito_especial="desorientar"),
            Arma(nome="Rede de Titânio", dano_min=5, dano_max=10, custo_bateria=15, usos=2, efeito_especial="imobilizar"),
            Arma(nome="Míssil de PEM", dano_min=25, dano_max=40, custo_bateria=20, usos=1)
        ]
        self.efeitos_ativos = []

    def listar_inventario_formatado(self):
        linhas = ["[Inventário de Armas]"]
        for i, arma in enumerate(self.inventario):
            usos = "infinitos" if arma.usos_restantes == float('inf') else arma.usos_restantes
            linhas.append(f"  {i + 1}. {arma.nome} (Dano: {arma.dano_min}-{arma.dano_max}, Bateria: {arma.custo_bateria}, Usos: {usos})")
        return "\n".join(linhas)

    def atacar(self, pato, arma_index):
        resultado = {'log': '', 'sucesso': False, 'efeito': None}
        
        if not (0 <= arma_index < len(self.inventario)):
            resultado['log'] = "Seleção de arma inválida."
            return resultado

        arma_escolhida = self.inventario[arma_index]

        if self.bateria < arma_escolhida.custo_bateria:
            resultado['log'] = f"Bateria insuficiente para usar {arma_escolhida.nome}!"
            return resultado
        if arma_escolhida.usos_restantes <= 0:
            resultado['log'] = f"{arma_escolhida.nome} não tem mais munição!"
            return resultado

        self.bateria -= arma_escolhida.custo_bateria
        if arma_escolhida.usos_restantes != float('inf'):
            arma_escolhida.usos_restantes -= 1

        dano = arma_escolhida.calcular_dano()
        pato.hp -= dano

        resultado['log'] = f"Drone disparou {arma_escolhida.nome}! O {pato.nome} sofreu {dano} de dano."
        resultado['sucesso'] = True
        
        if arma_escolhida.efeito_especial:
            resultado['log'] += f"\nEfeito especial '{arma_escolhida.efeito_especial.upper()}' ativado!"
            duracao = 0
            if arma_escolhida.efeito_especial == 'imobilizar': duracao = 2
            elif arma_escolhida.efeito_especial == 'desorientar': duracao = 3
            
            if duracao > 0:
                pato.efeitos_ativos.append({'nome': arma_escolhida.efeito_especial, 'turnos_restantes': duracao})

        return resultado

    def escanear_pontos_fracos(self, pato):
        if self.bateria < 10:
            return "Bateria insuficiente para escanear!"
        self.bateria -= 10
        
        fraquezas = ["Plumagem Densa (resistente a sônico)", "Juntas Expostas (vulnerável a rede)", "Blindagem Biônica"]
        fraqueza_detectada = random.choice(fraquezas)
        return f"Escaneamento... Bateria: {self.bateria}%\nVida do Alvo: {pato.hp} HP.\nFraqueza Detectada: {fraqueza_detectada}."

    def usar_sgda(self, super_poder):
        if self.bateria < 25:
            return {'log': "Bateria do SGDA insuficiente! Defesa falhou!", 'sucesso': False}
        self.bateria -= 25
        
        if random.random() > 0.4:
            return {'log': "SGDA ativado! Defesa bem-sucedida!", 'sucesso': True}
        else:
            return {'log': "Falha na defesa! O Drone foi atingido!", 'sucesso': False}

class PatoCombatente:
    def __init__(self, registro_pato):
        self.nome = f"Espécime-{registro_pato.drone['numero_serie']}"
        self.hp = int((registro_pato.peso_g / 100) + (registro_pato.quantidade_mutacoes * 5))
        self.hp_max = self.hp
        self.status = registro_pato.status_hibernacao
        self.super_poder = registro_pato.super_poder
        self.efeitos_ativos = []

    def escolher_acao(self, drone_oponente):
        log_acao = ""
        
        if any(e['nome'] == 'desorientar' for e in self.efeitos_ativos):
            log_acao += f"O {self.nome} está desorientado!\n"
            if random.random() < 0.5:
                log_acao += "...e sua ação falhou!"
                return {'tipo': 'falha', 'dano': 0, 'log': log_acao}

        em_furia = self.hp < (self.hp_max * 0.3)
        drone_vulneravel = drone_oponente.integridade < 40

        if em_furia:
            log_acao += f"O {self.nome} está em fúria!\n"

        if self.super_poder and self.status == 'desperto':
            chance_super_poder = 0.8 if drone_vulneravel or em_furia else 0.6
            if random.random() < chance_super_poder:
                dano = random.randint(20, 40)
                if em_furia: dano = int(dano * 1.5)
                log_acao += f"O Pato está usando seu super-poder: {self.super_poder['nome']}!"
                return {'tipo': 'super_poder', 'dano': dano, 'efeito': 'desorientar', 'log': log_acao, 'poder_info': self.super_poder}

        dano = random.randint(5, 15)
        if em_furia: dano = int(dano * 1.5)
        log_acao += f"O {self.nome} ataca fisicamente!"
        return {'tipo': 'ataque_fisico', 'dano': dano, 'log': log_acao}

def gerenciar_efeitos(personagem):
    efeitos_a_remover = []
    pode_agir = True
    log = ""

    nome_personagem = getattr(personagem, 'nome', 'Drone')

    for efeito in personagem.efeitos_ativos:
        log += f"  | Efeito ativo em {nome_personagem}: {efeito['nome'].upper()} ({efeito['turnos_restantes']} turnos restantes)\n"
        
        if efeito['nome'] == 'imobilizar':
            pode_agir = False

        efeito['turnos_restantes'] -= 1
        if efeito['turnos_restantes'] <= 0:
            efeitos_a_remover.append(efeito)
            log += f"  | Efeito '{efeito['nome'].upper()}' em {nome_personagem} terminou.\n"

    personagem.efeitos_ativos = [e for e in personagem.efeitos_ativos if e not in efeitos_a_remover]
    
    if not pode_agir:
        log += f"  | {nome_personagem} está imobilizado e não pode agir!\n"
        
    return log.strip(), pode_agir