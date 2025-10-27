# Sistema de Controle de Patos Primordiais (DSIN) 🦆✨

**Versão:** 2.0 (Aplicação Interface gráfica - GUI)

---

## 📖 Descrição do Projeto

Este projeto simula um sistema para a **Etapa Bônus do Desáfio Coder Challenge - DSIN)**, encarregado de catalogar, analisar e, eventualmente, capturar entidades interdimensionais conhecidas como "Patos Primordiais".

O projeto nasceu como um desafio acadêmico dividido em três missões principais e evoluiu significativamente:

1.  **Protótipo Inicial:** Um script Python (`main.py`) com interface de linha de comando (CLI) para catalogar dados em um arquivo JSON (`catalogo_patos.json`).
2.  **Aplicação Desktop v2.0:** Migração para uma arquitetura robusta com banco de dados SQLite (`patos.db`), camada de acesso a dados (`database.py`), modelos de objetos (`modelos.py`), e uma interface gráfica completa (`gui.py`) utilizando Tkinter, incluindo formulários com abas e campos dinâmicos.
3.  **Inteligência e Simulação:** Implementação de um módulo de análise de risco/custo/prioridade (`analisador_risco.py`) baseado em regras configuráveis (`config.json`) e um sistema de simulação de combate por turnos (`sistema_combate.py`), ambos integrados à GUI.
4.  **Visualização e Distribuição:** Adição de visualização geoespacial dos avistamentos (`folium`, `mapa_global_patos.html`) e capacidade de empacotamento em um executável (`pyinstaller`, `helpers_app.py`).

Este repositório serve como um portfólio demonstrando a evolução de um sistema, desde a concepção até uma aplicação desktop funcional e distribuível, utilizando diversas tecnologias e conceitos de engenharia de software.

---

## ✨ Funcionalidades Principais

* **Catalogação Completa:**
    * Interface gráfica amigável (Tkinter) para adicionar, visualizar, editar e remover registros de Patos Primordiais.
    * Formulários organizados em abas (`ttk.Notebook`).
    * Suporte a múltiplas unidades de medida (cm/pés, g/libras, m/jardas) com conversão automática.
    * Campos dinâmicos que se adaptam ao status do Pato (BPM para Transe/Hibernação, Super-poder para Desperto).
* **Persistência Robusta:**
    * Utilização de banco de dados SQLite (`patos.db`) para armazenamento seguro e eficiente dos dados.
    * Camada de Acesso a Dados (`database.py`) para abstrair as interações SQL.
* **Análise Inteligente:**
    * Módulo (`analisador_risco.py`) que calcula Custo Operacional, Grau de Risco, Valor Científico e Índice de Prioridade de Captura.
    * Regras de análise totalmente configuráveis via `config.json` (sem hardcoding).
    * Análise de fatores ambientais com base na localização.
    * Exibição clara do relatório de análise na interface.
* **Simulação de Combate:**
    * Módulo (`sistema_combate.py`) com lógica de combate por turnos, incluindo:
        * Inventário de armas com atributos (dano, custo, usos, efeitos).
        * Sistema de efeitos de status (imobilizar, desorientar).
        * IA básica para o Pato com reações contextuais (modo fúria, alvo fraco).
    * Interface de combate gráfica (Tkinter) com HUD (dados do drone), log de combate e ações interativas.
* **Visualização Geoespacial:**
    * Geração de mapa HTML interativo (`folium`) mostrando a localização de todos os Patos catalogados, com marcadores coloridos por status.
* **Distribuição:**
    * Empacotamento em um único executável (`pyinstaller`) para fácil distribuição e uso em máquinas sem Python instalado.
    * Inclusão de arquivos de dados (configuração, banco de dados, imagens) no executável.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Banco de Dados:** SQLite 3
* **Interface Gráfica:**
    * Tkinter (para a versão de gerenciamento `gui.py`)
* **Bibliotecas Principais:**
    * `sqlite3` (DB)
    * `json` (Configuração)
    * `tkinter` (GUI)
    * `Pillow` (Manipulação de Imagens na GUI)
    * `folium` (Geração de Mapas)
    * `webbrowser` (Abrir Mapa)
    * `geopy` (Cálculo de Distância Geodésica)
* **Empacotamento:** `pyinstaller`

---

## 🏗️ Arquitetura e Evolução

O projeto seguiu uma abordagem incremental, com foco na modularidade e separação de responsabilidades:

1.  **`main.py` (obsoleto):** Ponto de partida monolítico (CLI + JSON).
2.  **`modelos.py`:** Define a estrutura de dados (`RegistroPatoPrimordial`), validação e conversões.
3.  **`config.json` / `configuracao.py`:** Externaliza as regras de negócio.
4.  **`analisador_risco.py`:** Módulo de análise inteligente, consome `config.json` e `modelos.py`.
5.  **`database.py` / `patos.db`:** Camada de persistência com SQLite.
6.  **`gui.py`:** Interface gráfica principal (Tkinter), orquestra as chamadas aos outros módulos. Contém as classes `AplicacaoDSIN`, `JanelaFormulario`, `JanelaCombate` (versão Tkinter).
7.  **`sistema_combate.py`:** Backend da simulação, agnóstico de interface.
8.  **`conversor.py`:** Funções utilitárias reutilizáveis.
9.  **`helpers_app.py`:** Função `resource_path` essencial para o `pyinstaller` encontrar arquivos de dados.
10. **Artefatos:** `mapa_global_patos.html` (gerado), `logo_dsin.png` / `sprites` (recursos), `gui.exe` / `jogo.exe` (produto final).

---

## 📸 Screenshots (Exemplos)

**Tela Principal (Tkinter):**
`<img width="899" height="627" alt="image" src="https://github.com/user-attachments/assets/4c0b1803-30ec-462c-a0f1-ec53edeb4868" />`

**Formulário de Adicionar/Editar (com Abas):**
`<img width="491" height="472" alt="image" src="https://github.com/user-attachments/assets/f128535b-9b37-4b5c-947a-e175407a0a47" />`

**Relatório de Análise:**
`<img width="569" height="379" alt="image" src="https://github.com/user-attachments/assets/5b89c0c5-0609-45f1-b9d4-8aaf04c1b19f" />`

**Mapa Global:**
`<img width="1197" height="791" alt="image" src="https://github.com/user-attachments/assets/cf7ed49a-bbec-4662-aaa4-2f07baed52ce" />`

**Tela de Combate :**
`<img width="658" height="718" alt="image" src="https://github.com/user-attachments/assets/516978fc-a915-4145-b0af-3425d241de38" />`
`<img width="786" height="721" alt="image" src="https://github.com/user-attachments/assets/c1eacd0d-67d8-422c-8115-19772a94e694" />`

---

## ⚙️ Instalação e Configuração (Para Desenvolvedores)

1.  **Pré-requisitos:**
    * Python 3.8 ou superior instalado.
    * `pip` (gerenciador de pacotes do Python).

2.  **Clonar o Repositório:**
    ```bash
    git clone [URL_DO_SEU_REPOSITORIO_GITHUB]
    cd [NOME_DA_PASTA_DO_PROJETO]
    ```

3.  **(Recomendado) Criar um Ambiente Virtual:**
    ```bash
    python -m venv venv
    # No Windows:
    .\venv\Scripts\activate
    # No Linux/macOS:
    source venv/bin/activate
    ```

4.  **Instalar Dependências:**
    * Primeiro, gere o arquivo `requirements.txt` se ainda não o fez:
        ```bash
        pip freeze > requirements.txt
        ```
        *(Certifique-se de que ele contenha pelo menos: `pygame`, `Pillow`, `folium`, `geopy`, `pyinstaller`)*
    * Instale as dependências:
        ```bash
        pip install -r requirements.txt
        ```

---

## ▶️ Como Usar

**1. Executando a partir do Código Fonte:**

* **Versão Tkinter (Gerenciamento):**
    ```bash
    python gui.py
    ```

**2. Usando o Executável (se gerado com PyInstaller):**

* Navegue até a pasta `dist` gerada pelo PyInstaller.
* Execute o arquivo `gui.exe` com dois cliques.

**Funcionalidades:**

* **Gerenciamento:** Use os botões "Adicionar", "Editar", "Remover" na interface principal. Selecione um Pato na lista para ver detalhes e habilitar ações.
* **Análise:** Selecione um Pato e clique em "Analisar Risco".
* **Mapa:** Clique em "Ver Mapa Global" para abrir o mapa no navegador.
* **Combate (Tkinter):** Selecione um Pato com status "Desperto" e clique em "Iniciar Missão de Captura". Siga as instruções na tela/console para lutar.

---

## 📄 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 👋 Contato

**Marcio Hernani** - 
[GitHub](https://github.com/mhbsZSS)
[LinkedIn](https://www.linkedin.com/in/marcio-hernani-barbosa-da-silva)
