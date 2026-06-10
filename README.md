# 🏆 World Cup Manager 2026

Dashboard web interativo para visualização e análise de dados da Copa do Mundo FIFA 2026. A aplicação conta com navegação multi-página, sidebar dinâmica e gráficos interativos, consumindo dados de um banco MySQL via Python.

---

## 📋 Sobre o Projeto

O **World Cup Manager 2026** é um painel de controle completo que permite explorar estatísticas do torneio de forma visual e interativa. A navegação é feita por uma sidebar com páginas dedicadas a seleções, jogadores, estádios, partidas e ranking de vitórias.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Finalidade |
|---|---|---|
| **Python** | 3.x | Linguagem principal |
| **Dash** | 4.1.0 | Framework do dashboard web multi-página |
| **Dash Bootstrap Components** | 2.0.4 | Componentes de layout responsivo |
| **Plotly** | 6.7.0 | Gráficos interativos |
| **Pandas** | 3.0.3 | Manipulação e transformação dos dados |
| **mysql-connector-python** | 9.7.0 | Conexão com o banco de dados MySQL |
| **MySQL Workbench** | — | Modelagem e administração do banco |
| **CSS** | — | Estilização customizada da interface |
| **python-dotenv** | 1.1.0 | Gerenciamento de variáveis de ambiente |
| **Flask** | 3.1.3 | Servidor subjacente ao Dash |

---

## 📁 Estrutura do Projeto

```
world-cup-manager-2026/
│
├── pages/                     # Páginas da aplicação (multi-page Dash)
│   ├── dashboard.py           # Página inicial com visão geral
│   ├── selecoes.py            # Dados das seleções
│   ├── jogadores.py           # Elencos e estatísticas de jogadores
│   ├── estadios.py            # Informações dos estádios
│   ├── partidas.py            # Resultados e calendário de partidas
│   └── ranking.py             # Ranking de vitórias
│
├── assets/
│   └── style.css              # Estilos customizados (sidebar, topbar, layout)
│
├── database/
│   └── connection.py          # Configuração da conexão com o MySQL
│
├── app.py                     # Entry point — layout principal e sidebar
├── requirements.txt           # Dependências do projeto
└── README.md
```

---

## 🗺️ Páginas da Aplicação

| Rota | Página | Descrição |
|---|---|---|
| `/` | Dashboard | Visão geral do torneio |
| `/selecoes` | Seleções | Estatísticas por seleção |
| `/jogadores` | Jogadores | Elencos e desempenho individual |
| `/estadios` | Estádios | Localização e informações das arenas |
| `/partidas` | Partidas | Calendário e resultados dos jogos |
| `/ranking` | Ranking de Vitórias | Classificação geral das seleções |

---

## ⚙️ Pré-requisitos

- [Python 3.9+](https://www.python.org/)
- [MySQL Server](https://dev.mysql.com/downloads/mysql/)
- [MySQL Workbench](https://www.mysql.com/products/workbench/)
- [pip](https://pip.pypa.io/en/stable/)

---

## 🚀 Como Executar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/world-cup-manager-2026.git
cd world-cup-manager-2026
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

O banco de dados MySQL está hospedado no **Railway**. O arquivo `.env` com as credenciais de acesso será **enviado separadamente** pela equipe — não está no repositório por razões de segurança.

Após receber o arquivo, coloque-o na raiz do projeto:

```
world-cup-manager-2026/
├── .env   ← aqui
├── app.py
└── ...
```

> ⚠️ O `.env` contém dados sensíveis. Não compartilhe nem versione esse arquivo.

### 5. Execute a aplicação

```bash
python app.py
```

Acesse no navegador: [http://localhost:8050](http://localhost:8050)

> Para deploy em produção, a aplicação expõe o objeto `server` (Flask) compatível com **Gunicorn**:
> ```bash
> gunicorn app:server
> ```

---

## 📦 Principais Dependências

```
dash==4.1.0
dash-bootstrap-components==2.0.4
plotly==6.7.0
pandas==3.0.3
mysql-connector-python==9.7.0
python-dotenv==1.1.0
Flask==3.1.3
numpy==2.3.1
```

> Lista completa em `requirements.txt`.

---

## 🗃️ Banco de Dados

O banco foi modelado e administrado via **MySQL Workbench**. As principais tabelas são:

- `selecoes` — Dados das seleções participantes
- `jogadores` — Elenco de cada seleção
- `estadios` — Arenas e localização
- `partidas` — Jogos realizados e resultados
- `fases` — Fases do torneio (grupos, mata-mata)

---

## 👥 Integrantes

| Nome |
|---|
| Ana Clara Souza |
| Beatriz Kaori |
| Lucas Santana |
| Luiz Vinícius Santos |
| Maria Laura Cordeiro |
| Pablo Guilherme Neves |

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.

---

> Desenvolvido com ⚽ durante a Copa do Mundo FIFA 2026.
