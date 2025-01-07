import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod
import json
import sqlite3
import re

# ------------------------- CLASSES DO SISTEMA -------------------------

class Pessoa(ABC):
    """Classe base abstrata para representar pessoas."""
    def __init__(self, nome, email):
        self._nome = nome
        self._email = email

    @abstractmethod
    def exibir_dados(self):
        pass

    @property
    def nome(self):
        return self._nome

    @property
    def email(self):
        return self._email

class Participante(Pessoa):
    """Classe que representa um participante."""
    def __init__(self, nome, email, telefone, id=None):
        super().__init__(nome, email)
        self.telefone = telefone
        self.id = id

    def exibir_dados(self):
        return f"Nome: {self.nome}, Email: {self.email}, Telefone: {self.telefone}"

    def to_dict(self):
        """Converte o objeto Participante em um dicionário."""
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone
        }

class Evento:
    """Classe que representa um evento."""
    def __init__(self, titulo, data, local, capacidade, id=None):
        self.id = id
        self.titulo = titulo
        self.data = data
        self.local = local
        self.capacidade = capacidade
        self.participantes = []

    def adicionar_participante(self, participante):
        if len(self.participantes) < self.capacidade:
            self.participantes.append(participante)
            return True
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "data": self.data,
            "local": self.local,
            "capacidade": self.capacidade,
            "participantes": [p.to_dict() for p in self.participantes]
        }

# ------------------------- LÓGICA DE INTERFACE GRÁFICA -------------------------

class SistemaGerenciamentoEventos:
    """Classe que gerencia a interface gráfica e a lógica do sistema."""
    def __init__(self, root):
        self.root = root
        self.root.title("EventSync (Sistema de Gerenciamento de Eventos)")
        self.root.geometry("800x600")
        # Configura o ícone da janela e da barra de tarefas
        self.root.iconbitmap("imagens/calendario.ico")  # Arquivo .ico para Windows
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="white")
        self.style.configure("TLabel", background="white", font=("Arial", 12))
        self.style.configure("TButton", background="#007BFF", foreground="white", font=("Arial", 12))
        self.style.map("TButton", background=[("active", "#0056b3")])
        self.style.configure("Treeview", rowheight=30, font=("Arial", 12), background="white", foreground="black")
        self.style.configure("Treeview.Heading", font=("Arial", 14, "bold"), background="#007BFF", foreground="white")
        self.style.map("Treeview.Heading", background=[("active", "#0056b3")])

        self.eventos = []
        self.participantes = []

        # Configurar banco de dados
        self.conn = sqlite3.connect("EventSync.db")
        self.cursor = self.conn.cursor()
        self.criar_tabelas()
        self.carregar_dados()
        self.setup_ui()

    def criar_tabelas(self):
        """Cria as tabelas no banco de dados, se não existirem."""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            data TEXT NOT NULL,
            local TEXT NOT NULL,
            capacidade INTEGER NOT NULL
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS participantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT NOT NULL
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS inscricoes (
            evento_id INTEGER NOT NULL,
            participante_id INTEGER NOT NULL,
            FOREIGN KEY (evento_id) REFERENCES eventos(id),
            FOREIGN KEY (participante_id) REFERENCES participantes(id)
        )
        ''')
        self.conn.commit()

    def carregar_dados(self):
        """Carrega dados do banco de dados."""
        self.cursor.execute("SELECT * FROM eventos")
        eventos_db = self.cursor.fetchall()
        self.eventos.clear()  # Limpa a lista antes de carregar novos dados
        for evento in eventos_db:
            evento_obj = Evento(evento[1], evento[2], evento[3], evento[4], evento[0])
            self.eventos.append(evento_obj)

        self.cursor.execute("SELECT * FROM participantes")
        participantes_db = self.cursor.fetchall()
        self.participantes.clear()  # Limpa a lista antes de carregar novos dados
        for participante in participantes_db:
            participante_obj = Participante(participante[1], participante[2], participante[3], participante[0])
            self.participantes.append(participante_obj)

    def setup_ui(self):
        """Configura a interface do usuário."""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True)

        # Aba de gerenciamento de eventos
        aba_eventos = ttk.Frame(notebook)
        notebook.add(aba_eventos, text="Gerenciar Eventos")
        self.setup_aba_eventos(aba_eventos)

        # Aba de gerenciamento de participantes
        aba_participantes = ttk.Frame(notebook)
        notebook.add(aba_participantes, text="Gerenciar Participantes")
        self.setup_aba_participantes(aba_participantes)

        # Aba de inscrições
        aba_inscricoes = ttk.Frame(notebook)
        notebook.add(aba_inscricoes, text="Inscrições")
        self.setup_aba_inscricoes(aba_inscricoes)

        # Aba para salvar arquivos
        aba_serializar = ttk.Frame(notebook)
        notebook.add(aba_serializar, text="Salvar Arquivos")
        self.setup_aba_serializar(aba_serializar)

        # Carregar dados nas tabelas
        self.atualizar_tabelas()
        self.atualizar_comboboxes()  # Atualiza os comboboxes após carregar os dados

    def setup_aba_serializar(self, aba):
        """Configura a aba para salvar arquivos."""
        ttk.Label(aba, text="Salvar Dados", font=("Arial", 14)).pack(pady=10)

        btn_salvar_eventos_json = ttk.Button(aba, text="Salvar Eventos (JSON)", command=self.salvar_eventos_json)
        btn_salvar_eventos_json.pack(pady=(5,10))

        btn_salvar_participantes_json = ttk.Button(aba, text="Salvar Participantes (JSON)", command=self.salvar_participantes_json)
        btn_salvar_participantes_json.pack(pady=(5, 10))

        btn_salvar_inscricoes_json = ttk.Button(aba, text="Salvar Inscrições (JSON)", command=self.salvar_inscricoes_json)
        btn_salvar_inscricoes_json.pack(pady=(5, 10))

        btn_salvar_tudo_json = ttk.Button(aba, text="Salvar Tudo (JSON)", command=self.salvar_tudo_json)
        btn_salvar_tudo_json.pack(pady=(5, 50))

        btn_salvar_eventos_txt = ttk.Button(aba, text="Salvar Eventos (TXT)", command=self.salvar_eventos_txt)
        btn_salvar_eventos_txt.pack(pady=(5, 10))

        btn_salvar_participantes_txt = ttk.Button(aba, text="Salvar Participantes (TXT)", command=self.salvar_participantes_txt)
        btn_salvar_participantes_txt.pack(pady=(5, 10))

        btn_salvar_inscricoes_txt = ttk.Button(aba, text="Salvar Inscrições (TXT)", command=self.salvar_inscricoes_txt)
        btn_salvar_inscricoes_txt.pack(pady=(5, 10))

        btn_salvar_tudo_txt = ttk.Button(aba, text="Salvar Tudo (TXT)", command=self.salvar_tudo_txt)
        btn_salvar_tudo_txt.pack(pady=(5, 10))

    def atualizar_comboboxes(self):
        """Atualiza os comboboxes de eventos e participantes."""
        self.combo_eventos['values'] = [evento.titulo for evento in self.eventos]
        self.combo_participantes['values'] = [participante.nome for participante in self.participantes]

    def atualizar_tabelas(self):
        """Atualiza as tabelas de eventos e participantes na interface."""
        self.tree_eventos.delete(*self.tree_eventos.get_children())
        for evento in self.eventos:
            self.tree_eventos.insert("", "end", values=(evento.titulo, evento.data, evento.local, evento.capacidade))

        self.tree_participantes.delete(*self.tree_participantes.get_children())
        for participante in self.participantes:
            self.tree_participantes.insert("", "end", values=(participante.nome, participante.email, participante.telefone))

    def setup_aba_eventos(self, aba):
        """Configura a aba de gerenciamento de eventos."""
        frame_form = ttk.LabelFrame(aba, text="Cadastrar Evento")
        frame_form.pack(padx=10, pady=10, fill='x')

        ttk.Label(frame_form, text="Título:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_titulo = ttk.Entry(frame_form, width=30)
        self.entry_titulo.grid(row=0, column=1, padx=5, pady=5)

        # Combobox para selecionar o dia
        ttk.Label(frame_form, text="Data:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.combo_dia = ttk.Combobox(frame_form, values=[str(i).zfill(2) for i in range(1, 32)], state='readonly')
        self.combo_dia.grid(row=1, column=1, padx=5, pady=5)
        self.combo_dia.set("01")  # Valor padrão

        # Combobox para selecionar o mês
        self.combo_mes = ttk.Combobox(frame_form, values=["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", 
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"], state='readonly')
        self.combo_mes.grid(row=1, column=2, padx=5, pady=5)
        self.combo_mes.set("Janeiro")  # Valor padrão

        # Combobox para selecionar o ano
        self.combo_ano = ttk.Combobox(frame_form, values=[str(i) for i in range(2023, 2033)], state='readonly')
        self.combo_ano.grid(row=1, column=3, padx=5, pady=5)
        self.combo_ano.set("2023")  # Valor padrão

        # Combobox para selecionar a hora
        ttk.Label(frame_form, text="Hora:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.combo_hora = ttk.Combobox(frame_form, values=[f"{str(i).zfill(2)}" for i in range(24)], state='readonly')
        self.combo_hora.grid(row=2, column=1, padx=5, pady=5)
        self.combo_hora.set("00")  # Valor padrão

        # Combobox para selecionar os minutos
        self.combo_minuto = ttk.Combobox(frame_form, values=[f"{str(i).zfill(2)}" for i in range(0, 60, 5)], state='readonly')
        self.combo_minuto.grid(row=2, column=2, padx=5, pady=5)
        self.combo_minuto.set("00")  # Valor padrão

        ttk.Label(frame_form, text="Local:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.entry_local = ttk.Entry(frame_form, width=30)
        self.entry_local.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Capacidade:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.entry_capacidade = ttk.Entry(frame_form, width=30)
        self.entry_capacidade.grid(row=4, column=1, padx=5, pady=5)

        btn_cadastrar_evento = ttk.Button(frame_form, text="Cadastrar Evento", command=self.cadastrar_evento)
        btn_cadastrar_evento.grid(row=5, column=0, columnspan=2, pady=10)

        btn_remover_evento = ttk.Button(frame_form, text="Remover Evento", command=self.remover_evento)
        btn_remover_evento.grid(row=6, column=0, columnspan=2, pady=10)

        # Adicionando aviso para remover
        ttk.Label(frame_form, text="Selecione um evento na lista para remover.", foreground="gray", font=("Arial", 10)).grid(row=7, column=0, columnspan=2, sticky='w', padx=5, pady=(5, 15))
        frame_lista = ttk.LabelFrame(aba, text="Lista de Eventos")
        frame_lista.pack(padx=10, pady=10, fill='both', expand=True)

        self.tree_eventos = ttk.Treeview(frame_lista, columns=("#1", "#2", "#3", "#4"), show="headings")
        self.tree_eventos.heading("#1", text="Título")
        self.tree_eventos.heading("#2", text="Data")
        self.tree_eventos.heading("#3", text="Local")
        self.tree_eventos.heading("#4", text="Capacidade")
        self.tree_eventos.pack(fill='both', expand=True)
        
    def setup_aba_participantes(self, aba):
        """Configura a aba de gerenciamento de participantes."""
        frame_form = ttk.LabelFrame(aba, text="Cadastrar Participante")
        frame_form.pack(padx=10, pady=10, fill='x')

        ttk.Label(frame_form, text="Nome:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.entry_nome = ttk.Entry(frame_form, width=30)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Email:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.entry_email = ttk.Entry(frame_form, width=30)
        self.entry_email.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(frame_form, text="(exemplo@dominio.com)", foreground="gray", font=("Arial", 10)).grid(row=1, column=2, sticky='w', padx=5, pady=5)

        ttk.Label(frame_form, text="Telefone:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.entry_telefone = ttk.Entry(frame_form, width=30)
        self.entry_telefone.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(frame_form, text="(+5511999999999)", foreground="gray", font=("Arial", 10)).grid(row=2, column=2, sticky='w', padx=5, pady=5)


        btn_cadastrar_participante = ttk.Button(frame_form, text="Cadastrar Participante", command=self.cadastrar_participante)
        btn_cadastrar_participante.grid(row=3, column=0, columnspan=2, pady=10)

        btn_remover_participante = ttk.Button(frame_form, text="Remover Participante", command=self.remover_participante)
        btn_remover_participante.grid(row=4, column=0, columnspan=2, pady=10)

        # Adicionando aviso para remover
        ttk.Label(frame_form, text="Selecione um participante na lista para remover.", foreground="gray", font=("Arial", 10)).grid(row=5, column=0, columnspan=2, sticky='w', padx=5, pady=(5, 15))

        frame_lista = ttk.LabelFrame(aba, text="Lista de Participantes")
        frame_lista.pack(padx=10, pady=10, fill='both', expand=True)

        self.tree_participantes = ttk.Treeview(frame_lista, columns=("#1", "#2", "#3"), show="headings")
        self.tree_participantes.heading("#1", text="Nome")
        self.tree_participantes.heading("#2", text="Email")
        self.tree_participantes.heading("#3", text="Telefone")
        self.tree_participantes.pack(fill='both', expand=True)

    def setup_aba_inscricoes(self, aba):
        """Configura a aba de gerenciamento de inscrições."""
        frame_form = ttk.LabelFrame(aba, text="Realizar Inscrição")
        frame_form.pack(padx=10, pady=10, fill='x')

        ttk.Label(frame_form, text="Evento:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.combo_eventos = ttk.Combobox(frame_form)
        self.combo_eventos.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_form, text="Participante:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.combo_participantes = ttk.Combobox(frame_form)
        self.combo_participantes.grid(row=1, column=1, padx=5, pady=5)

        btn_realizar_inscricao = ttk.Button(frame_form, text="Inscrever", command=self.realizar_inscricao)
        btn_realizar_inscricao.grid(row=2, column=0, columnspan=2, pady=10)

        # Mova o botão de remover inscrição para a linha 3
        btn_remover_inscricao = ttk.Button(frame_form, text="Remover Inscrição", command=self.remover_inscricao)
        btn_remover_inscricao.grid(row=3, column=0, columnspan=2, pady=10)

        # Adicionando aviso para remover
        ttk.Label(frame_form, text="Selecione uma inscrição na lista para remover.", foreground="gray", font=("Arial", 10)).grid(row=4, column=0, columnspan=2, sticky='w', padx=5, pady=(5, 15))

        # Tabela de Inscrições
        frame_lista = ttk.LabelFrame(aba, text="Lista de Inscrições")
        frame_lista.pack(padx=10, pady=10, fill='both', expand=True)

        self.tree_inscricoes = ttk.Treeview(frame_lista, columns=("#1", "#2", "#3"), show="headings")
        self.tree_inscricoes.heading("#1", text="Evento")
        self.tree_inscricoes.heading("#2", text="Participante")
        self.tree_inscricoes.heading("#3", text="Capacidade (Atual/Total)")
        self.tree_inscricoes.pack(fill='both', expand=True)

        self.carregar_inscricoes()  # Carregar inscrições ao inicializar a aba
    
    def carregar_inscricoes(self):
        """Carrega as inscrições do banco de dados e exibe na tabela."""
        self.cursor.execute('''SELECT e.titulo, p.nome, e.capacidade,
                                      (SELECT COUNT(*) FROM inscricoes i WHERE i.evento_id = e.id)
                               FROM eventos e
                               LEFT JOIN inscricoes i ON e.id = i.evento_id
                               LEFT JOIN participantes p ON p.id = i.participante_id''')
        inscricoes_db = self.cursor.fetchall()

        # Limpa a tabela antes de preencher
        self.tree_inscricoes.delete(*self.tree_inscricoes.get_children())

        # Preenche a tabela com as inscrições e o status de capacidade
        for evento, participante, capacidade, inscritos in inscricoes_db:
            if evento and capacidade:
                capacidade_str = f"({inscritos}/{capacidade})"
                self.tree_inscricoes.insert("", "end", values=(evento, participante or "", capacidade_str))

    def cadastrar_evento(self):
        """Cadastra um novo evento."""
        titulo = self.entry_titulo.get()
    
        # Obter a data a partir dos comboboxes
        dia = self.combo_dia.get()
        mes = self.combo_mes.get()
        ano = self.combo_ano.get()
        data = f"{dia}/{mes}/{ano}"  # Formato de data: DD/MM/YYYY

        local = self.entry_local.get()
        try:
            capacidade = int(self.entry_capacidade.get())
        except ValueError:
            messagebox.showerror("Erro", "A capacidade deve ser um número inteiro.")
            return

        # Inserir evento no banco de dados
        self.cursor.execute("INSERT INTO eventos (titulo, data, local, capacidade) VALUES (?, ?, ?, ?)", (titulo, data, local, capacidade))
        self.conn.commit()

        # Recuperar o id gerado para o evento
        evento_id = self.cursor.lastrowid

        # Criar o objeto evento e atribuir o id
        evento = Evento(titulo, data, local, capacidade, evento_id)

        # Adicionar o evento à lista
        self.eventos.append(evento)

        # Atualizar a interface gráfica com o novo evento
        self.atualizar_tabelas()
        self.atualizar_comboboxes()  # Atualiza os comboboxes após cadastrar um novo evento
        messagebox.showinfo("Sucesso", "Evento cadastrado com sucesso!")

    def remover_evento(self):
        """Remove um evento selecionado."""
        selected_item = self.tree_eventos.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione um evento para remover.")
            return

        evento_titulo = self.tree_eventos.item(selected_item, 'values')[0]
        evento = next((e for e in self.eventos if e.titulo == evento_titulo), None)

        if evento:
            # Remover todas as inscrições associadas ao evento
            self.cursor.execute("DELETE FROM inscricoes WHERE evento_id = ?", (evento.id,))
            self.conn.commit()

            # Agora remover o evento
            self.cursor.execute("DELETE FROM eventos WHERE id = ?", (evento.id,))
            self.conn.commit()

            # Remover o evento da lista local
            self.eventos.remove(evento)

            # Atualizar tabelas e comboboxes
            self.atualizar_tabelas()
            self.atualizar_comboboxes()

            # Atualizar a tabela de inscrições para refletir a remoção
            self.carregar_inscricoes()

            messagebox.showinfo("Sucesso", "Evento removido com sucesso!")


    def cadastrar_participante(self):
        """Cadastra um novo participante."""
        nome = self.entry_nome.get()
        email = self.entry_email.get()
        telefone = self.entry_telefone.get()

        # Verificar se o email é válido usando uma expressão regular
        if not self.email_valido(email):
            messagebox.showerror("Erro", "O email fornecido é inválido.")
            return
        
        # Verificar se o telefone é válido
        if not self.telefone_valido(telefone):
            messagebox.showerror("Erro", "O telefone fornecido é inválido. Deve conter entre 10 a 15 dígitos.")
            return
        
        # Verificar se o email já está cadastrado
        self.cursor.execute("SELECT COUNT(*) FROM participantes WHERE email = ?", (email,))
        if self.cursor.fetchone()[0] > 0:
            messagebox.showerror("Erro", "Já existe um participante cadastrado com este email.")
            return

        # Verificar se o telefone já está cadastrado
        self.cursor.execute("SELECT COUNT(*) FROM participantes WHERE telefone = ?", (telefone,))
        if self.cursor.fetchone()[0] > 0:
            messagebox.showerror("Erro", "Já existe um participante cadastrado com este telefone.")
            return

        # Inserir participante no banco de dados
        self.cursor.execute("INSERT INTO participantes (nome, email, telefone) VALUES (?, ?, ?)", (nome, email, telefone))
        self.conn.commit()

        # Recuperar o id gerado para o participante
        participante_id = self.cursor.lastrowid

        # Criar o objeto participante com o id
        participante = Participante(nome, email, telefone, participante_id)

        # Adicionar o participante à lista
        self.participantes.append(participante)

        # Atualizar a lista de participantes na interface
        self.atualizar_tabelas()
        self.atualizar_comboboxes()  # Atualiza os comboboxes após cadastrar um novo participante
        messagebox.showinfo("Sucesso", "Participante cadastrado com sucesso!")

    def remover_participante(self):
        """Remove um participante selecionado."""
        selected_item = self.tree_participantes.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione um participante para remover.")
            return

        participante_nome = self.tree_participantes.item(selected_item, 'values')[0]
        participante = next((p for p in self.participantes if p.nome == participante_nome), None)

        if participante:
            # Remover todas as inscrições associadas ao participante
            self.cursor.execute("DELETE FROM inscricoes WHERE participante_id = ?", (participante.id,))
            self.conn.commit()

            # Agora remover o participante
            self.cursor.execute("DELETE FROM participantes WHERE id = ?", (participante.id,))
            self.conn.commit()
            self.participantes.remove(participante)
            self.atualizar_tabelas()
            self.atualizar_comboboxes()
            self.carregar_inscricoes()  # Atualiza a lista de inscrições
            messagebox.showinfo("Sucesso", "Participante removido com sucesso!")
    
    def email_valido(self, email):
        """Verifica se o email fornecido tem um formato válido."""
        regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(regex, email) is not None
    
    def telefone_valido(self, telefone):
        """Verifica se o telefone fornecido tem um formato válido."""
        regex = r'^\+?[0-9]{10,15}$'  # Exemplo de regex para validar números de telefone
        return re.match(regex, telefone) is not None

    def realizar_inscricao(self):
        """Realiza a inscrição de um participante em um evento."""
        evento_titulo = self.combo_eventos.get()
        participante_nome = self.combo_participantes.get()

        if not evento_titulo or not participante_nome:
            messagebox.showerror("Erro", "Selecione um evento e um participante.")
            return

        evento = next((e for e in self.eventos if e.titulo == evento_titulo), None)
        participante = next((p for p in self.participantes if p.nome == participante_nome), None)

        if evento and participante:
            # Verificar se o evento já atingiu sua capacidade
            self.cursor.execute("SELECT COUNT(*) FROM inscricoes WHERE evento_id = ?", (evento.id,))
            inscricoes_count = self.cursor.fetchone()[0]
            if inscricoes_count >= evento.capacidade:
                messagebox.showerror("Erro", "O evento já atingiu sua capacidade máxima.")
                return

            # Verificar se o participante já está inscrito no evento
            self.cursor.execute(
                "SELECT 1 FROM inscricoes WHERE evento_id = ? AND participante_id = ?",
                (evento.id, participante.id)
            )
            if self.cursor.fetchone():
                messagebox.showerror("Erro", "O participante já está inscrito neste evento.")
                return

            # Inserir inscrição no banco de dados
            self.cursor.execute(
                "INSERT INTO inscricoes (evento_id, participante_id) VALUES (?, ?)",
                (evento.id, participante.id)
            )
            self.conn.commit()

            # Atualizar a lista de inscrições na interface
            self.carregar_inscricoes()
            messagebox.showinfo("Sucesso", "Inscrição realizada com sucesso!")
        else:
            messagebox.showerror("Erro", "Evento ou participante não encontrado.")

    def remover_inscricao(self):
        """Remove uma inscrição selecionada."""
        selected_item = self.tree_inscricoes.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Selecione uma inscrição para remover.")
            return

        # Descompactar os valores corretamente
        evento_titulo, participante_nome, _ = self.tree_inscricoes.item(selected_item, 'values')

        # Localizar o evento e o participante com base nos títulos e nomes
        evento = next((e for e in self.eventos if e.titulo == evento_titulo), None)
        participante = next((p for p in self.participantes if p.nome == participante_nome), None)

        if evento and participante:
            # Remover a inscrição do banco de dados
            self.cursor.execute("DELETE FROM inscricoes WHERE evento_id = ? AND participante_id = ?", (evento.id, participante.id))
            self.conn.commit()

            # Atualizar a lista de inscrições na interface
            self.carregar_inscricoes()
            messagebox.showinfo("Sucesso", "Inscrição removida com sucesso!")
        else:
            messagebox.showerror("Erro", "Evento ou participante não encontrado.")

    def salvar_eventos_json(self, filename="EventSync_Eventos.json"):
        """Serializa os eventos em um arquivo JSON."""
        eventos_serializados = [evento.to_dict() for evento in self.eventos]
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(eventos_serializados, file, ensure_ascii=False, indent=4)
        messagebox.showinfo("Sucesso", f"Eventos salvos em {filename}!")

    def salvar_participantes_json(self, filename="EventSync_Participantes.json"):
        """Serializa os participantes em um arquivo JSON."""
        participantes_serializados = [participante.to_dict() for participante in self.participantes]
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(participantes_serializados, file, ensure_ascii=False, indent=4)
        messagebox.showinfo("Sucesso", f"Participantes salvos em {filename}!")

    def salvar_inscricoes_json(self, filename="EventSync_Inscricoes.json"):
        """Serializa as inscrições em um arquivo JSON."""
        self.cursor.execute('''SELECT e.titulo AS evento, p.nome AS participante 
                               FROM inscricoes i
                               JOIN eventos e ON i.evento_id = e.id
                               JOIN participantes p ON i.participante_id = p.id''')
        inscricoes = self.cursor.fetchall()
        inscricoes_serializadas = [{"evento": evento, "participante": participante} for evento, participante in inscricoes]

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(inscricoes_serializadas, file, ensure_ascii=False, indent=4)
        messagebox.showinfo("Sucesso", f"Inscrições salvas em {filename}!")

    def salvar_eventos_txt(self, filename="EventSync_Eventos.txt"):
        """Serializa os eventos em um arquivo TXT."""
        with open(filename, "w", encoding="utf-8") as file:
            for evento in self.eventos:
                file.write(f"Título: {evento.titulo}, Data: {evento.data}, Local: {evento.local}, Capacidade: {evento.capacidade}\n")
        messagebox.showinfo("Sucesso", f"Eventos salvos em {filename}!")

    def salvar_participantes_txt(self, filename="EventSync_Participantes.txt"):
        """Serializa os participantes em um arquivo TXT."""
        with open(filename, "w", encoding="utf-8") as file:
            for participante in self.participantes:
                file.write(f"Nome: {participante.nome}, Email: {participante.email}, Telefone: {participante.telefone}\n")
        messagebox.showinfo("Sucesso", f"Participantes salvos em {filename}!")

    def salvar_inscricoes_txt(self, filename="EventSync_Inscricoes.txt"):
        """Serializa as inscrições em um arquivo TXT."""
        self.cursor.execute('''SELECT e.titulo AS evento, p.nome AS participante 
                               FROM inscricoes i
                               JOIN eventos e ON i.evento_id = e.id
                               JOIN participantes p ON i.participante_id = p.id''')
        inscricoes = self.cursor.fetchall()

        with open(filename, "w", encoding="utf-8") as file:
            for evento, participante in inscricoes:
                file.write(f"Evento: {evento}, Participante: {participante}\n")
        messagebox.showinfo("Sucesso", f"Inscrições salvas em {filename}!")

    def salvar_tudo_json(self, filename="EventSync_Todos_Dados.json"):
        """Salva todos os dados (eventos, participantes e inscrições) em um arquivo JSON."""
        dados = {
            "eventos": [evento.to_dict() for evento in self.eventos],
            "participantes": [participante.to_dict() for participante in self.participantes],
            "inscricoes": []
        }

        self.cursor.execute('''SELECT e.titulo AS evento, p.nome AS participante 
                           FROM inscricoes i
                           JOIN eventos e ON i.evento_id = e.id
                           JOIN participantes p ON i.participante_id = p.id''')
        inscricoes = self.cursor.fetchall()
        for evento, participante in inscricoes:
            dados["inscricoes"].append({"evento": evento, "participante": participante})

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(dados, file, ensure_ascii=False, indent=4)
        messagebox.showinfo("Sucesso", f"Todos os dados salvos em {filename}!")

    def salvar_tudo_txt(self, filename="EventSync_Todos_Dados.txt"):
        """Salva todos os dados (eventos, participantes e inscrições) em um arquivo TXT."""
        with open(filename, "w", encoding="utf-8") as file:
            file.write("Eventos:\n")
            for evento in self.eventos:
                file.write(f"Título: {evento.titulo}, Data: {evento.data}, Local: {evento.local}, Capacidade: {evento.capacidade}\n")

            file.write("\nParticipantes:\n")
            for participante in self.participantes:
                file.write(f"Nome: {participante.nome}, Email: {participante.email}, Telefone: {participante.telefone}\n")

            file.write("\nInscrições:\n")
            self.cursor.execute('''SELECT e.titulo AS evento, p.nome AS participante 
                               FROM inscricoes i
                               JOIN eventos e ON i.evento_id = e.id
                               JOIN participantes p ON i.participante_id = p.id''')
            inscricoes = self.cursor.fetchall()
            for evento, participante in inscricoes:
                file.write(f"Evento: {evento}, Participante: {participante}\n")

        messagebox.showinfo("Sucesso", f"Todos os dados salvos em {filename}!")

# ------------------------- EXECUÇÃO DO PROGRAMA -------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaGerenciamentoEventos(root)
    root.mainloop()