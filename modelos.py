from conversor import converter_altura, converter_peso, converter_precisao

class RegistroPatoPrimordial:
    def __init__(self, drone_info, altura, unidade_altura, peso, unidade_peso, 
                 local_info, precisao, unidade_precisao, status, 
                 qtd_mutacoes, ponto_referencia=None, batimentos_cardiacos=None, 
                 super_poder_info=None):
    
        # Informações do Drone
        self.drone = drone_info
        
        # Dados Físicos
        self.altura_cm = converter_altura(altura, unidade_altura)
        self.peso_g = converter_peso(peso, unidade_peso)
        
        # Localização
        self.localizacao = local_info
        self.precisao_m = converter_precisao(precisao, unidade_precisao)
        self.ponto_referencia = ponto_referencia
        
        # Status e Biometria 
        self.status_hibernacao = status
        self.batimentos_cardiacos_bpm = None
        if self.status_hibernacao in ["em transe", "hibernação profunda"]:
            self.batimentos_cardiacos_bpm = batimentos_cardiacos
            
        # Mutações e Poderes
        self.quantidade_mutacoes = qtd_mutacoes
        self.super_poder = None
        if self.status_hibernacao == "desperto":
            self.super_poder = super_poder_info

    def exibir_relatorio(self):
        print("--- Relatório de Avistamento de Pato Primordial ---")
        print(f"Drone: {self.drone['numero_serie']} (Fab.: {self.drone['fabricante']}, País: {self.drone['pais_origem']})")
        print(f"Local: {self.localizacao['cidade']}, {self.localizacao['pais']} (Lat: {self.localizacao['latitude']}, Lon: {self.localizacao['longitude']})")
        if self.ponto_referencia:
            print(f"  -> Ponto de Referência: {self.ponto_referencia}")
        print(f"Precisão da Coleta: {self.precisao_m:.2f} metros")
        print("-" * 20)
        print("Dados do Pato Primordial:")
        print(f"  Altura: {self.altura_cm:.2f} cm")
        print(f"  Peso: {self.peso_g:.2f} g")
        print(f"  Status: {self.status_hibernacao.title()}")
        if self.batimentos_cardiacos_bpm:
            print(f"  Batimentos Cardíacos: {self.batimentos_cardiacos_bpm} bpm")
        print(f"  Nível de Mutação: {self.quantidade_mutacoes}")
        if self.super_poder:
            print("  --- Super-Poder Detectado ---")
            print(f"  Nome: {self.super_poder['nome']}")
            print(f"  Descrição: {self.super_poder['descricao']}")
            print(f"  Classificação: {', '.join(self.super_poder['classificacoes'])}")
        print("="*47 + "\n")

    def to_dict(self):
        return {
            'drone_info': self.drone,
            'altura_cm': self.altura_cm,
            'peso_g': self.peso_g,
            'localizacao': self.localizacao,
            'precisao_m': self.precisao_m,
            'ponto_referencia': self.ponto_referencia,
            'status_hibernacao': self.status_hibernacao,
            'batimentos_cardiacos_bpm': self.batimentos_cardiacos_bpm,
            'quantidade_mutacoes': self.quantidade_mutacoes,
            'super_poder': self.super_poder
        }