# EventSync - Sistema de Gerenciamento de Eventos

**EventSync** é um sistema de gerenciamento de eventos desenvolvido em Python, utilizando a biblioteca Tkinter para a interface gráfica e SQLite para o armazenamento de dados. Ele facilita o cadastro e a gestão de eventos, participantes e inscrições.

---

## 📋 Funcionalidades

- **Cadastro de Eventos**: Cadastre eventos com título, data, local e capacidade.
- **Cadastro de Participantes**: Cadastre participantes com nome, email e telefone.
- **Inscrições**: Inscreva participantes em eventos e gerencie essas inscrições.
- **Remoção de Dados**: Exclua eventos e participantes cadastrados.
- **Salvar Dados**: Exporte eventos, participantes e inscrições em arquivos JSON e TXT.
- **Validação de Dados**: Verifique duplicatas e valide informações como email e telefone.

---

## 🛠️ Tecnologias Utilizadas

- **Python**: Linguagem principal do projeto.
- **Tkinter**: Biblioteca para a criação de interfaces gráficas.
- **SQLite**: Banco de dados leve para armazenamento de dados.
- **JSON**: Utilizado para exportar dados de forma estruturada.

---

## ⚙️ Instalação

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/marcosfilhopq/EventSync.git
   cd EventSync
   ```

2. **Instale as dependências**:  
   Não há dependências externas, apenas bibliotecas padrão do Python.

3. **Execute o programa**:
   ```bash
   python EventSync.py
   ```

---

## 🖥️ Uso

### Interface Gráfica
Ao iniciar o programa, a interface gráfica apresenta abas com as seguintes funcionalidades:

- **Gerenciar Eventos**: Cadastro e gerenciamento de eventos.
- **Gerenciar Participantes**: Cadastro e gerenciamento de participantes.
- **Inscrições**: Inscreva participantes em eventos e visualize as inscrições.
- **Salvar Arquivos**: Exporte dados para arquivos JSON ou TXT.

### Fluxo de Operação

1. **Cadastro de Eventos**:
   - Preencha os campos obrigatórios: Título, Data, Local, Capacidade.
   - Clique em **"Cadastrar Evento"**.
   - Os eventos cadastrados aparecerão na lista.

2. **Cadastro de Participantes**:
   - Preencha os campos obrigatórios: Nome, Email, Telefone.
   - Clique em **"Cadastrar Participante"**.
   - Os participantes cadastrados aparecerão na lista.

3. **Inscrições**:
   - Selecione um evento e um participante.
   - Clique em **"Inscrever"** para registrar a inscrição.
   - As inscrições aparecerão na tabela correspondente.

4. **Remoção**:
   - Selecione um evento ou participante e clique em **"Remover"** para excluí-lo.

5. **Salvar Dados**:
   - Use a aba **Salvar Arquivos** para exportar e atualizar dados em JSON ou TXT. Caso já tenha exportado arquivos e queira adicionar novos dados no JSON e no TXT simplesmente clique nos botoes na aba de Salvar Arquivos para que os acervos sejam atualizados.

---

## 📂 Estrutura do Código

### Classes Principais

#### **`Pessoa`** (Classe Abstrata)
- **Descrição**: Base para representar pessoas.
- **Propriedades**: 
  - `nome`: Retorna o nome da pessoa.
  - `email`: Retorna o email da pessoa..
- **Métodos**: 
  - `exibir_dados()`: Método abstrato que deve ser implementado nas subclasses..

#### **`Participante`** (Herda de `Pessoa`)
- **Descrição**: Representa os participantes.
- **Propriedades**: 
  - `telefone`: Telefone do participante.
  - `id`: ID do participante no banco de dados.
- **Métodos**:
  - `exibir_dados()`: Retorna os dados do participante.
  - `to_dict()`: Converte o objeto para dicionário.

#### **`Evento`**
- **Descrição**: Representa os eventos.
- **Propriedades**: 
  - `titulo`: Título do evento.
  - `data`: Data do evento.
  - `local`: Local do evento.
  - `capacidade`: Capacidade do evento.
  - `participantes`: Lista de participantes inscritos no evento.
- **Métodos**:
  - `adicionar_participante(participante)`: Adiciona um participante se houver capacidade.
  - `to_dict()`: Converte o objeto para dicionário.

#### **`SistemaGerenciamentoEventos`**
- **Descrição**: Gerencia a interface gráfica e a lógica do sistema.
- **Propriedades**: 
  - `root`: A janela principal da interface gráfica.
  - `eventos`: Lista de eventos cadastrados.
  - `participantes`: Lista de participantes cadastrados.
  - `conn`: Conexão com o banco de dados SQLite.
  - `cursor`: Cursor para executar comandos SQL.
- **Métodos Principais**:
  - `criar_tabelas()`: Cria as tabelas no banco de dados, se não existirem.
  - `carregar_dados()`: Carrega dados do banco de dados para as listas de eventos e participantes.
  - `setup_ui()`: Configura a interface do usuário.
  - `setup_aba_eventos(aba)`: Configura a aba de gerenciamento de eventos.
  - `setup_aba_participantes(aba)`: Configura a aba de gerenciamento de participantes.
  - `setup_aba_inscricoes(aba)`: Configura a aba de gerenciamento de inscrições.
  - `setup_aba_serializar(aba)`: Configura a aba para salvar arquivos.
  - `atualizar_tabelas()`: Atualiza as tabelas de eventos e participantes na interface.
  - `atualizar_comboboxes()`: Atualiza os comboboxes de eventos e participantes.
  - `cadastrar_evento()`: Cadastra um novo evento.
  - `remover_evento()`: Remove um evento selecionado.
  - `cadastrar_participante()`: Cadastra um novo participante.
  - `remover_participante()`: Remove um participante selecionado.
  - `realizar_inscricao()`: Realiza a inscrição de um participante em um evento.
  - `remover_inscricao()`: Remove uma inscrição selecionada.
  - `salvar_eventos_json()`: Salva eventos em um arquivo JSON.
  - `salvar_participantes_json()`: Salva participantes em um arquivo JSON.
  - `salvar_inscricoes_json()`: Salva inscrições em um arquivo JSON.
  - `salvar_eventos_txt()`: Salva eventos em um arquivo TXT.
  - `salvar_participantes_txt()`: Salva participantes em um arquivo TXT.
  - `salvar_inscricoes_txt()`: Salva inscrições em um arquivo TXT.
  - `salvar_tudo_json()`: Salva todos os dados em um arquivo JSON.
  - `salvar_tudo_txt()`: Salva todos os dados em um arquivo TXT.

---

## 🌟 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. **Faça um fork** do repositório.
2. Crie uma branch para sua funcionalidade:
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```
3. Faça suas alterações e realize o commit:
   ```bash
   git commit -m 'Adiciona nova funcionalidade'
   ```
4. Envie a branch para o repositório remoto:
   ```bash
   git push origin feature/nova-funcionalidade
   ```
5. Abra um **Pull Request**.

---

## 📜 Licença

Este projeto está licenciado sob a [MIT License]. Veja o arquivo LICENSE para mais detalhes.

---

## Personalização

### Como Personalizar o Projeto

  - **Substitua os links e informações**: Certifique-se de substituir os links do repositório, seu nome de usuário, e-mail e qualquer outra informação específica do seu projeto.

  - **Adicione mais funcionalidades**: Caso o projeto tenha funcionalidades adicionais ou exclusivas, detalhe-as nas seções apropriadas.

  - **Adapte para outros idiomas**: Se necessário, traduza o README para atender a um público-alvo diferente.

  - **Modifique o design da interface gráfica**: Atualize o layout ou a aparência da interface gráfica para atender às necessidades específicas do seu público.

  - **Configure para diferentes bancos de dados**: Altere o suporte ao banco de dados SQLite para outro banco, como MySQL ou PostgreSQL, se necessário.

---

## 📧 Contato

- **Email**: marcosfpq@gmail.com



