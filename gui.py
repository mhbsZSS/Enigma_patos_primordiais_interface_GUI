import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import database
from modelos import RegistroPatoPrimordial
import conversor
import analisador_risco
import sistema_combate
import webbrowser
from helpers_app import resource_path

try:
    from PIL import Image, ImageTk
    PIL_INSTALADO = True
except ImportError:
    PIL_INSTALADO = False

try:
    import folium
    FOLIUM_INSTALADO = True
except ImportError:
    FOLIUM_INSTALADO = False

class JanelaFormulario(tk.Toplevel):
    def __init__(self, parent_app, pato=None):
        super().__init__(parent_app.root)
        
        self.app = parent_app  
        self.pato = pato       

        # --- Configuração da Janela ---
        if self.pato:
            self.title(f"Editar Registro - ID {self.pato.id}")
        else:
            self.title("Adicionar Novo Registro")
            
        self.geometry("500x450")
        self.transient(parent_app.root)
        self.grab_set()

        # Dicionário para guardar todos os widgets de entrada
        self.entries = {}
        self.dynamic_widgets = {}

        # --- Construção do Layout ---
        self._construir_layout_abas()
        self._construir_botoes()

        if self.pato:
            self._preencher_formulario()
        else:
            self._atualizar_campos_dinamicos() 

    def _construir_layout_abas(self):
        notebook = ttk.Notebook(self, padding="10")
        
        # Cria os frames para cada aba
        tab_drone = ttk.Frame(notebook)
        tab_local = ttk.Frame(notebook)
        tab_biometria = ttk.Frame(notebook)
        
        notebook.add(tab_drone, text="Drone")
        notebook.add(tab_local, text="Localização")
        notebook.add(tab_biometria, text="Biometria")
        
        notebook.pack(fill=tk.BOTH, expand=True)

        # --- Aba 1: Drone ---
        campos_drone = ["Número de série do drone", "Fabricante do drone", "País de origem do drone"]
        for i, campo_texto in enumerate(campos_drone):
            ttk.Label(tab_drone, text=f"{campo_texto}:").grid(row=i, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(tab_drone, width=40)
            entry.grid(row=i, column=1, sticky="ew", padx=10, pady=5)
            self.entries[campo_texto] = entry

        # --- Aba 2: Localização ---
        campos_local = ["Cidade do avistamento", "País do avistamento", "Latitude", "Longitude", "Ponto de Referência"]
        for i, campo_texto in enumerate(campos_local):
            ttk.Label(tab_local, text=f"{campo_texto}:").grid(row=i, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(tab_local, width=40)
            entry.grid(row=i, column=1, sticky="ew", padx=10, pady=5)
            self.entries[campo_texto] = entry

        # --- Aba 3: Biometria ---
        # Campos de Altura e Peso
        ttk.Label(tab_biometria, text="Altura do espécime:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        entry_altura = ttk.Entry(tab_biometria, width=20)
        entry_altura.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        combo_altura = ttk.Combobox(tab_biometria, values=['cm', 'jardas'], width=7)
        combo_altura.grid(row=0, column=2, padx=5)
        combo_altura.set('cm')
        self.entries["Altura do espécime"] = (entry_altura, combo_altura)

        ttk.Label(tab_biometria, text="Peso do espécime:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        entry_peso = ttk.Entry(tab_biometria, width=20)
        entry_peso.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        combo_peso = ttk.Combobox(tab_biometria, values=['g', 'libras'], width=7)
        combo_peso.grid(row=1, column=2, padx=5)
        combo_peso.set('g')
        self.entries["Peso do espécime"] = (entry_peso, combo_peso)

        # Campo de Mutações
        ttk.Label(tab_biometria, text="Quantidade de mutações:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        entry_mutacoes = ttk.Entry(tab_biometria, width=10)
        entry_mutacoes.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        self.entries["Quantidade de mutações"] = entry_mutacoes

        # --- Campos Dinâmicos (Status e seus dependentes) ---
        ttk.Label(tab_biometria, text="Status de Hibernação:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        status_values = ["desperto", "em transe", "hibernação profunda"]
        combo_status = ttk.Combobox(tab_biometria, values=status_values, width=20)
        combo_status.grid(row=3, column=1, sticky="w", padx=10, pady=5)
        self.entries["Status de Hibernação"] = combo_status
       
        combo_status.bind("<<ComboboxSelected>>", self._atualizar_campos_dinamicos)

        self._construir_campos_dinamicos(tab_biometria)

    def _construir_campos_dinamicos(self, parent_tab):
        # --- Campos de "Em Transe" ---
        lbl_bpm = ttk.Label(parent_tab, text="Batimentos Cardíacos (bpm):")
        entry_bpm = ttk.Entry(parent_tab, width=10)
        self.dynamic_widgets['em_transe'] = [lbl_bpm, entry_bpm]
        self.entries["Batimentos Cardíacos (bpm)"] = entry_bpm
        
        # --- Campos de "Desperto" ---
        lbl_poder_nome = ttk.Label(parent_tab, text="Super-poder Nome:")
        entry_poder_nome = ttk.Entry(parent_tab, width=30)
        lbl_poder_desc = ttk.Label(parent_tab, text="Super-poder Descrição:")
        entry_poder_desc = ttk.Entry(parent_tab, width=40)
        self.dynamic_widgets['desperto'] = [lbl_poder_nome, entry_poder_nome, lbl_poder_desc, entry_poder_desc]
        self.entries["Super-poder Nome"] = entry_poder_nome
        self.entries["Super-poder Descrição"] = entry_poder_desc

    def _atualizar_campos_dinamicos(self, event=None):
        status_selecionado = self.entries["Status de Hibernação"].get()
        # 1. Oculta todos os widgets dinâmicos
        for widgets in self.dynamic_widgets.values():
            for widget in widgets:
                widget.grid_remove()

        # 2. Mostra os widgets relevantes
        if status_selecionado == 'em transe':
            # Posiciona os widgets de BPM
            self.dynamic_widgets['em_transe'][0].grid(row=4, column=0, sticky="w", padx=10, pady=5)
            self.dynamic_widgets['em_transe'][1].grid(row=4, column=1, sticky="w", padx=10, pady=5)
        elif status_selecionado == 'desperto':
            # Posiciona os widgets de Super-poder
            self.dynamic_widgets['desperto'][0].grid(row=4, column=0, sticky="w", padx=10, pady=5)
            self.dynamic_widgets['desperto'][1].grid(row=4, column=1, columnspan=2, sticky="ew", padx=10, pady=5)
            self.dynamic_widgets['desperto'][2].grid(row=5, column=0, sticky="w", padx=10, pady=5)
            self.dynamic_widgets['desperto'][3].grid(row=5, column=1, columnspan=2, sticky="ew", padx=10, pady=5)

    def _preencher_formulario(self):
        pato = self.pato
        
        # Aba Drone
        self.entries["Número de série do drone"].insert(0, pato.drone['numero_serie'])
        self.entries["Fabricante do drone"].insert(0, pato.drone['fabricante'])
        self.entries["País de origem do drone"].insert(0, pato.drone['pais_origem'])
        
        # Aba Localização
        self.entries["Cidade do avistamento"].insert(0, pato.localizacao['cidade'])
        self.entries["País do avistamento"].insert(0, pato.localizacao['pais'])
        self.entries["Latitude"].insert(0, pato.localizacao['latitude'])
        self.entries["Longitude"].insert(0, pato.localizacao['longitude'])
        self.entries["Ponto de Referência"].insert(0, pato.ponto_referencia)
        
        # Aba Biometria
        self.entries["Altura do espécime"][0].insert(0, f"{pato.altura_cm:.2f}")
        self.entries["Altura do espécime"][1].set('cm')
        self.entries["Peso do espécime"][0].insert(0, f"{pato.peso_g:.2f}")
        self.entries["Peso do espécime"][1].set('g')
        self.entries["Quantidade de mutações"].insert(0, pato.quantidade_mutacoes)
        
        self.entries["Status de Hibernação"].set(pato.status_hibernacao)
        
        # Preenche os campos dinâmicos
        if pato.status_hibernacao == 'em transe' and pato.batimentos_cardiacos_bpm:
            self.entries["Batimentos Cardíacos (bpm)"].insert(0, pato.batimentos_cardiacos_bpm)
        elif pato.status_hibernacao == 'desperto' and pato.super_poder:
            self.entries["Super-poder Nome"].insert(0, pato.super_poder.get('nome', ''))
            self.entries["Super-poder Descrição"].insert(0, pato.super_poder.get('descricao', ''))
            
        self._atualizar_campos_dinamicos()

    def _construir_botoes(self):
        frame_botoes = ttk.Frame(self, padding="10")
        frame_botoes.pack(fill=tk.X, side=tk.BOTTOM)

        texto_salvar = "Salvar Alterações" if self.pato else "Salvar"
        btn_salvar = ttk.Button(frame_botoes, text=texto_salvar, command=self._salvar)
        btn_salvar.pack(side=tk.RIGHT, padx=5)

        btn_cancelar = ttk.Button(frame_botoes, text="Cancelar", command=self.destroy)
        btn_cancelar.pack(side=tk.RIGHT, padx=10)

    def _salvar(self):
        try:
            # --- 1. Coleta e Converte ---
            altura_entry, altura_combo = self.entries["Altura do espécime"]
            altura_final_cm = conversor.converter_altura(float(altura_entry.get()), altura_combo.get())
            
            peso_entry, peso_combo = self.entries["Peso do espécime"]
            peso_final_g = conversor.converter_peso(float(peso_entry.get()), peso_combo.get())

            # --- 2. Coleta Dados Padrão ---
            drone_info = {
                'numero_serie': self.entries["Número de série do drone"].get(),
                'fabricante': self.entries["Fabricante do drone"].get(),
                'pais_origem': self.entries["País de origem do drone"].get()
            }
            local_info = {
                'cidade': self.entries["Cidade do avistamento"].get(),
                'pais': self.entries["País do avistamento"].get(),
                'latitude': float(self.entries["Latitude"].get()),
                'longitude': float(self.entries["Longitude"].get())
            }
            status = self.entries["Status de Hibernação"].get()
            
            # --- 3. Coleta Dados Dinâmicos ---
            batimentos_cardiacos = None
            super_poder_info = None
            
            if status == 'em transe':
                bpm_str = self.entries["Batimentos Cardíacos (bpm)"].get()
                if bpm_str:
                    batimentos_cardiacos = int(bpm_str)
            elif status == 'desperto':
                nome_poder = self.entries["Super-poder Nome"].get()
                desc_poder = self.entries["Super-poder Descrição"].get()
                if nome_poder: 
                    super_poder_info = {'nome': nome_poder, 'descricao': desc_poder}

            # --- 4. Cria o Objeto Pato ---
            pato_obj = RegistroPatoPrimordial(
                drone_info=drone_info,
                altura=altura_final_cm, unidade_altura='cm',
                peso=peso_final_g, unidade_peso='g',
                local_info=local_info,
                precisao=10, unidade_precisao='m',
                status=status,
                qtd_mutacoes=int(self.entries["Quantidade de mutações"].get()),
                ponto_referencia=self.entries["Ponto de Referência"].get(),
                batimentos_cardiacos=batimentos_cardiacos,
                super_poder_info=super_poder_info
            )
            
            # --- 5. Decide se Adiciona ou Edita ---
            if self.pato:
                database.editar_pato(self.pato.id, pato_obj)
                messagebox.showinfo("Sucesso", "Registro atualizado com sucesso!")
            else: 
                database.adicionar_pato(pato_obj)
                messagebox.showinfo("Sucesso", "Novo registro adicionado com sucesso!")

            # --- 6. Finaliza ---
            self.destroy() 
            self.app.carregar_lista_patos()

        except ValueError as e:
            messagebox.showerror("Erro de Entrada", f"Verifique os campos. Detalhe: {e}", parent=self)
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}", parent=self)

class AplicacaoDSIN:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Controle de Patos Primoriais")
        self.root.geometry("900x600")

        frame_header = ttk.Frame(self.root)
        frame_header.pack(fill=tk.X, side=tk.TOP, pady=(5, 0))

        if PIL_INSTALADO:
            try:
                caminho_logo = resource_path('logo_dsin.png')
                img_pil = Image.open(caminho_logo)
                
                nova_altura = 50
                proporcao = nova_altura / img_pil.height
                nova_largura = int(img_pil.width * proporcao)
                img_pil = img_pil.resize((nova_largura, nova_altura), Image.Resampling.LANCZOS)
                
                self.logo_image_tk = ImageTk.PhotoImage(img_pil)
                
                lbl_logo = ttk.Label(frame_header, image=self.logo_image_tk)
                lbl_logo.pack(pady=10)
                
            except Exception as e:
                print(f"AVISO: Não foi possível carregar o logo 'logo_dsin.png'. Usando header de texto. Erro: {e}")
                self._criar_header_texto(frame_header)
        else:
            print("AVISO: Biblioteca 'Pillow' não instalada. Usando header de texto.")
            self._criar_header_texto(frame_header)

        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', padx=10, pady=5)

        self.catalogo = []
        self.pato_selecionado_id = None
        self.pato_selecionado_obj = None

        frame_principal = ttk.Frame(self.root, padding="10")
        frame_principal.pack(fill=tk.BOTH, expand=True)
        frame_lista = ttk.Frame(frame_principal, padding="5")
        frame_lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.frame_detalhes = ttk.Frame(frame_principal, padding="5")
        self.frame_detalhes.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        frame_botoes = ttk.Frame(self.root, padding="10")
        frame_botoes.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Label(frame_lista, text="Registros Atuais", font=("-weight bold")).pack(anchor="w")
        frame_listbox = ttk.Frame(frame_lista)
        frame_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.lista_patos = tk.Listbox(frame_listbox, height=10)
        self.lista_patos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(frame_listbox, orient=tk.VERTICAL, command=self.lista_patos.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.lista_patos.config(yscrollcommand=scrollbar.set)
        self.lista_patos.bind('<<ListboxSelect>>', self.mostrar_detalhes_pato)

        ttk.Label(self.frame_detalhes, text="Detalhes do Espécime", font=("-weight bold")).pack(anchor="w")
        self.label_info_inicial = ttk.Label(self.frame_detalhes, text="\nSelecione um registro na lista para ver os detalhes.")
        self.label_info_inicial.pack(anchor="w", pady=10)
        
        # --- Botões ---
        btn_adicionar = ttk.Button(frame_botoes, text="Adicionar Novo Registro", command=self.abrir_janela_adicionar)
        btn_adicionar.pack(side=tk.LEFT, padx=5)
        
        self.btn_remover = ttk.Button(frame_botoes, text="Remover Registro", command=self.remover_registro_selecionado)
        self.btn_remover.pack(side=tk.LEFT, padx=5)
        self.btn_remover.config(state=tk.DISABLED)

        self.btn_editar = ttk.Button(frame_botoes, text="Editar Registro", command=self.abrir_janela_editar)
        self.btn_editar.pack(side=tk.LEFT, padx=5)
        self.btn_editar.config(state=tk.DISABLED)

        self.btn_analisar = ttk.Button(frame_botoes, text="Analisar Risco", command=self.abrir_janela_analise)
        self.btn_analisar.pack(side=tk.LEFT, padx=5)
        self.btn_analisar.config(state=tk.DISABLED)
        
        self.btn_missao = ttk.Button(frame_botoes, text="Iniciar Missão de Captura", command=self.abrir_janela_combate)
        self.btn_missao.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_missao.config(state=tk.DISABLED)

        frame_mapa = ttk.Frame(frame_botoes)
        frame_mapa.pack(side=tk.RIGHT)
        
        btn_mapa = ttk.Button(frame_mapa, text="Ver Mapa Global", command=self.abrir_mapa_global)
        btn_mapa.pack(side=tk.RIGHT, padx=10)

        self.carregar_lista_patos()

    def _criar_header_texto(self, parent_frame):
            style = ttk.Style()
            style.configure("Titulo.TLabel", font=("-size 14 -weight bold"))
            style.configure("Slogan.TLabel", font=("-size 10 -slant italic"))
            
            lbl_titulo = ttk.Label(parent_frame, 
                                text="DSIN - Departamento de Sincronia Interdimensional de Narcóticos", 
                                style="Titulo.TLabel")
            lbl_titulo.pack(pady=(5, 0))

            lbl_slogan = ttk.Label(parent_frame, 
                                text="\"Controlando o caos interdimensional, um pato de cada vez.\"", 
                                style="Slogan.TLabel")
            lbl_slogan.pack(pady=(0, 10))

    def abrir_janela_adicionar(self):
        JanelaFormulario(self)

    def abrir_janela_editar(self):
        if not self.pato_selecionado_obj:
            messagebox.showwarning("Erro", "Nenhum Pato selecionado para editar.")
            return
        JanelaFormulario(self, self.pato_selecionado_obj)

    def limpar_detalhes(self):
        for widget in self.frame_detalhes.winfo_children(): widget.destroy()
        ttk.Label(self.frame_detalhes, text="Detalhes do Espécime", font=("-weight bold")).pack(anchor="w")
        ttk.Label(self.frame_detalhes, text="\nSelecione um registro na lista para ver os detalhes.").pack(anchor="w", pady=10)
        self.pato_selecionado_id = None
        self.pato_selecionado_obj = None
        self.btn_remover.config(state=tk.DISABLED)
        self.btn_editar.config(state=tk.DISABLED)
        self.btn_analisar.config(state=tk.DISABLED)
        self.btn_missao.config(state=tk.DISABLED)

    def carregar_lista_patos(self):
        self.lista_patos.delete(0, tk.END)
        self.catalogo = database.listar_patos()
        for pato in self.catalogo:
            texto_item = f"ID {pato.id}: Espécime-{pato.drone['numero_serie']}"
            self.lista_patos.insert(tk.END, texto_item)
        self.limpar_detalhes()

    def mostrar_detalhes_pato(self, event):
        indices_selecionados = self.lista_patos.curselection()
        if not indices_selecionados: return 
        index = indices_selecionados[0]
        pato_selecionado = self.catalogo[index]
        self.pato_selecionado_id = pato_selecionado.id
        self.pato_selecionado_obj = pato_selecionado
        
        self.btn_remover.config(state=tk.NORMAL)
        self.btn_editar.config(state=tk.NORMAL)
        self.btn_analisar.config(state=tk.NORMAL)
        if pato_selecionado.status_hibernacao == 'desperto':
            self.btn_missao.config(state=tk.NORMAL)
        else:
            self.btn_missao.config(state=tk.DISABLED)

        for widget in self.frame_detalhes.winfo_children(): widget.destroy()
        ttk.Label(self.frame_detalhes, text="Detalhes do Espécime", font=("-weight bold")).pack(anchor="w")
        detalhes = {
            "ID do Banco": pato_selecionado.id,
            "Série do Drone": pato_selecionado.drone['numero_serie'],
            "Localização": f"{pato_selecionado.localizacao['cidade']}, {pato_selecionado.localizacao['pais']}",
            "Status": pato_selecionado.status_hibernacao.title(),
            "Altura": f"{pato_selecionado.altura_cm:.2f} cm",
            "Peso": f"{pato_selecionado.peso_g:.2f} g",
            "Mutações": pato_selecionado.quantidade_mutacoes,
        }
        
        if pato_selecionado.status_hibernacao == 'em transe':
            detalhes["Batimentos"] = f"{pato_selecionado.batimentos_cardiacos_bpm} bpm"
        elif pato_selecionado.status_hibernacao == 'desperto' and pato_selecionado.super_poder:
            detalhes["Poder"] = pato_selecionado.super_poder.get('nome', 'N/A')
            
        detalhes["Ref."] = pato_selecionado.ponto_referencia

        for chave, valor in detalhes.items():
            texto = f"{chave}: {valor}"
            ttk.Label(self.frame_detalhes, text=texto).pack(anchor="w", padx=10, pady=2)

    def remover_registro_selecionado(self):
        if not self.pato_selecionado_id:
            messagebox.showwarning("Nenhuma seleção", "Nenhum registro está selecionado.")
            return
        confirmar = messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover permanentemente o registro ID {self.pato_selecionado_id}?")
        if confirmar:
            try:
                database.remover_pato(self.pato_selecionado_id)
                messagebox.showinfo("Sucesso", "Registro removido com sucesso.")
                self.carregar_lista_patos()
            except Exception as e:
                messagebox.showerror("Erro", f"Ocorreu um erro ao remover o registro: {e}")

    def abrir_janela_analise(self):
        if not self.pato_selecionado_obj:
            messagebox.showwarning("Erro", "Nenhum Pato selecionado para analisar.")
            return
        try:
            if not hasattr(analisador_risco, 'analisar_pato'):
                 messagebox.showerror("Erro", "Módulo 'analisador_risco.py' não encontrado ou incompleto.")
                 return
            analise = analisador_risco.analisar_pato(self.pato_selecionado_obj)
            
            janela_analise = tk.Toplevel(self.root)
            janela_analise.title(f"Relatório de Análise - {analise.get('nome_pato', 'N/A')}")
            janela_analise.geometry("500x400")
            janela_analise.transient(self.root)
            janela_analise.grab_set()
            frame_relatorio = ttk.Frame(janela_analise, padding="15")
            frame_relatorio.pack(fill=tk.BOTH, expand=True)
            style = ttk.Style()
            style.configure("Titulo.TLabel", font=("-size 12 -weight bold"))
            for chave, valor in analise.items():
                chave_formatada = chave.replace('_', ' ').title()
                if chave in ['interpretacao_prioridade', 'interpretacao_risco', 'interpretacao_custo']:
                    texto_label = f"{chave_formatada}: {valor}"
                    ttk.Label(frame_relatorio, text=texto_label, style="Titulo.TLabel").pack(anchor="w", pady=5)
                elif isinstance(valor, (int, float)):
                    texto_label = f"{chave_formatada}: {valor:,.2f}"
                    ttk.Label(frame_relatorio, text=texto_label).pack(anchor="w", padx=10, pady=2)
                else:
                    texto_label = f"{chave_formatada}: {valor}"
                    ttk.Label(frame_relatorio, text=texto_label).pack(anchor="w", padx=10, pady=2)
        except Exception as e:
            messagebox.showerror("Erro na Análise", f"Ocorreu um erro ao gerar a análise: {e}")
            
    def abrir_janela_combate(self):
        if not self.pato_selecionado_obj:
            messagebox.showwarning("Erro", "Nenhum Pato selecionado para a missão.")
            return
        if not hasattr(sistema_combate, 'DroneDeCombate'):
             messagebox.showerror("Erro", "Módulo 'sistema_combate.py' não encontrado ou incompleto.")
             return
        
        JanelaCombate(self.root, self.pato_selecionado_obj)

    def abrir_mapa_global(self):
        if not FOLIUM_INSTALADO:
            messagebox.showerror("Biblioteca Faltando",
                                 "A biblioteca 'folium' não foi encontrada.\n"
                                 "Por favor, instale-a executando:\npip install folium")
            return
            
        catalogo = database.listar_patos()
        if not catalogo:
            messagebox.showinfo("Mapa Vazio", "Nenhum registro no banco de dados para exibir no mapa.")
            return
            
        mapa = folium.Map(location=[-21.65, -50.18], zoom_start=4)

        try:
            for pato in catalogo:
                lat = pato.localizacao.get('latitude')
                lon = pato.localizacao.get('longitude')
                
                if lat is None or lon is None:
                    continue
                    
                popup_html = f"""
                <b>Espécime-{pato.drone['numero_serie']}</b><br>
                ID: {pato.id}<br>
                Status: {pato.status_hibernacao.title()}<br>
                Local: {pato.localizacao['cidade']}, {pato.localizacao['pais']}
                """
                
                cor_icone = 'blue'
                if pato.status_hibernacao == 'desperto':
                    cor_icone = 'red'
                elif pato.status_hibernacao == 'em transe':
                    cor_icone = 'orange'
                
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color=cor_icone, icon='info-sign')
                ).add_to(mapa)
                
            nome_arquivo = "mapa_global_patos.html"
            mapa.save(nome_arquivo)
            webbrowser.open(nome_arquivo)
            
        except Exception as e:
            messagebox.showerror("Erro ao Gerar Mapa", f"Ocorreu um erro: {e}")

class JanelaCombate(tk.Toplevel):
    def __init__(self, parent, pato_obj):
        super().__init__(parent)
        self.pato_registro = pato_obj
        self.transient(parent)
        self.grab_set()
        self.title(f"Missão de Captura: {pato_obj.drone['numero_serie']}")
        self.geometry("600x700")
        self.drone = sistema_combate.DroneDeCombate()
        self.pato = sistema_combate.PatoCombatente(pato_obj)
        self.turno = 1
        frame_status = ttk.Frame(self, padding="10")
        frame_status.pack(fill=tk.X)
        self.lbl_drone_status = ttk.Label(frame_status, text="", font=("-weight bold"))
        self.lbl_drone_status.pack(side=tk.LEFT)
        self.lbl_pato_status = ttk.Label(frame_status, text="", font=("-weight bold"))
        self.lbl_pato_status.pack(side=tk.RIGHT)
        frame_log = ttk.Frame(self, padding="10")
        frame_log.pack(fill=tk.BOTH, expand=True)
        self.log_combate = tk.Text(frame_log, height=20, state=tk.DISABLED, relief="solid", borderwidth=1, wrap=tk.WORD)
        self.log_combate.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_log = ttk.Scrollbar(frame_log, orient=tk.VERTICAL, command=self.log_combate.yview)
        scrollbar_log.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_combate.config(yscrollcommand=scrollbar_log.set)
        frame_acoes = ttk.Frame(self, padding="10")
        frame_acoes.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Label(frame_acoes, text="Ações do Drone:", font=("-weight bold")).pack(anchor="w")
        self.btn_atacar = ttk.Button(frame_acoes, text="Atacar", command=self.acao_atacar)
        self.btn_atacar.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.btn_escanear = ttk.Button(frame_acoes, text="Escanear", command=self.acao_escanear)
        self.btn_escanear.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.btn_inventario = ttk.Button(frame_acoes, text="Ver Inventário", command=self.acao_inventario)
        self.btn_inventario.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.adicionar_ao_log(f"--- INICIANDO SIMULAÇÃO DE CAPTURA CONTRA {self.pato.nome} ---")
        self.atualizar_status()

    def adicionar_ao_log(self, texto):
        self.log_combate.config(state=tk.NORMAL)
        self.log_combate.insert(tk.END, f"{texto}\n")
        self.log_combate.config(state=tk.DISABLED)
        self.log_combate.see(tk.END)

    def atualizar_status(self):
        drone_txt = f"Drone: {self.drone.integridade}% Integridade | {self.drone.bateria}% Bateria"
        pato_txt = f"{self.pato.nome}: {self.pato.hp} HP"
        self.lbl_drone_status.config(text=drone_txt)
        self.lbl_pato_status.config(text=pato_txt)

    def desabilitar_botoes(self):
        self.btn_atacar.config(state=tk.DISABLED)
        self.btn_escanear.config(state=tk.DISABLED)
        self.btn_inventario.config(state=tk.DISABLED)

    def habilitar_botoes(self):
        self.btn_atacar.config(state=tk.NORMAL)
        self.btn_escanear.config(state=tk.NORMAL)
        self.btn_inventario.config(state=tk.NORMAL)

    def verificar_fim_de_jogo(self):
        if self.pato.hp <= 0:
            self.adicionar_ao_log(f"--- {self.pato.nome} NEUTRALIZADO! MISSÃO CUMPRIDA! ---")
            messagebox.showinfo("Vitória", "Alvo neutralizado! A missão foi um sucesso.", parent=self)
            self.desabilitar_botoes()
            self.destroy()
            return True
        elif self.drone.integridade <= 0:
            self.adicionar_ao_log("--- INTEGRIDADE DO DRONE EM 0%! MISSÃO FRACASSADA! ---")
            messagebox.showerror("Derrota", "O Drone foi destruído! Missão fracassada.", parent=self)
            self.desabilitar_botoes()
            self.destroy()
            return True
        return False
    
    def acao_atacar(self):
        from tkinter import simpledialog # Import local
        inventario_str = self.drone.listar_inventario_formatado()
        arma_idx_str = simpledialog.askstring("Atacar", f"{inventario_str}\n\nEscolha a arma (1, 2, 3...):", parent=self)
        try:
            arma_idx = int(arma_idx_str) - 1
            if not (0 <= arma_idx < len(self.drone.inventario)):
                raise ValueError("Índice de arma inválido.")
            self.desabilitar_botoes()
            self.adicionar_ao_log(f"\n--- TURNO {self.turno} (JOGADOR) ---")
            resultado = self.drone.atacar(self.pato, arma_idx)
            self.adicionar_ao_log(resultado['log'])
            self.atualizar_status()
            if not self.verificar_fim_de_jogo():
                self.processar_turno_pato()
        except (ValueError, TypeError):
            messagebox.showwarning("Entrada Inválida", "Por favor, insira um número de arma válido.", parent=self)
    
    def acao_escanear(self):
        self.desabilitar_botoes()
        self.adicionar_ao_log(f"\n--- TURNO {self.turno} (JOGADOR) ---")
        log_resultado = self.drone.escanear_pontos_fracos(self.pato)
        self.adicionar_ao_log(log_resultado)
        self.atualizar_status()
        if not self.verificar_fim_de_jogo():
            self.processar_turno_pato()
    
    def acao_inventario(self):
        log_resultado = self.drone.listar_inventario_formatado()
        self.adicionar_ao_log(log_resultado)
    
    def processar_turno_pato(self):
        self.adicionar_ao_log(f"\n--- TURNO {self.turno} (PATO) ---")
        log_efeitos, pode_agir = sistema_combate.gerenciar_efeitos(self.pato)
        if log_efeitos: self.adicionar_ao_log(log_efeitos)
        if pode_agir:
            acao_pato = self.pato.escolher_acao(self.drone)
            self.adicionar_ao_log(acao_pato['log'])
            dano_sofrido = acao_pato.get('dano', 0)
            if acao_pato['tipo'] == 'super_poder':
                usar_sgda = messagebox.askyesno("Alerta de Super-Poder!", 
                                                 "O Pato está usando um super-poder! Tentar usar o SGDA? (Custa 25 Bateria)", 
                                                 parent=self)
                if usar_sgda:
                    resultado_sgda = self.drone.usar_sgda(acao_pato.get('poder_info'))
                    self.adicionar_ao_log(resultado_sgda['log'])
                    if resultado_sgda['sucesso']:
                        dano_sofrido = 0
                else:
                    self.adicionar_ao_log("Drone não ativou o SGDA!")
            if dano_sofrido > 0:
                self.drone.integridade -= dano_sofrido
                self.adicionar_ao_log(f"O Drone sofreu {dano_sofrido} de dano!")
        self.turno += 1
        self.atualizar_status()
        if not self.verificar_fim_de_jogo():
            self.habilitar_botoes()

if __name__ == "__main__":
    database.criar_tabela()
    root = tk.Tk()
    app = AplicacaoDSIN(root)
    root.mainloop()