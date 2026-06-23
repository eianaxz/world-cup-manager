# World Cup Manager 2026

Dashboard web interativo para gerenciamento e análise de dados da Copa do Mundo FIFA 2026 — desenvolvido com Python, Dash e MySQL.

---

## Visão Geral

O World Cup Manager 2026 é uma aplicação web completa que centraliza o gerenciamento de informações relacionadas à Copa do Mundo FIFA 2026. Por meio de uma interface moderna e responsiva, o sistema permite visualizar, cadastrar, editar e excluir dados sobre seleções, jogadores, estádios e partidas, com todos os dados persistidos em um banco de dados MySQL hospedado na nuvem via Railway.

A aplicação conta com um dashboard analítico, ranking dinâmico de vitórias e integração direta com o banco de dados, incluindo triggers que definem automaticamente o vencedor de cada partida com base nos gols registrados.

---

## Funcionalidades

- Cadastro, edição e exclusão de seleções participantes
- Gerenciamento completo de jogadores vinculados às seleções
- Controle de estádios e suas informações
- Registro e acompanhamento de partidas com atualização automática do vencedor
- Dashboard geral com visualizações analíticas
- Ranking de vitórias por seleção

---

## Tecnologias

| Categoria         | Tecnologia                    | Versão  |
|-------------------|-------------------------------|---------|
| Linguagem         | Python                        | 3.x     |
| Framework Web     | Dash                          | 4.1.0   |
| Componentes UI    | Dash Bootstrap Components     | 2.0.4   |
| Visualização      | Plotly                        | 6.7.0   |
| Manipulação de Dados | Pandas                     | 3.0.3   |
| Computação        | NumPy                         | 2.3.1   |
| Banco de Dados    | MySQL + mysql-connector-python| 9.7.0   |
| Variáveis de Ambiente | python-dotenv             | 1.1.0   |
| Servidor HTTP     | Flask                         | 3.1.3   |
| Infraestrutura    | Railway                       | —       |
| Frontend          | HTML, CSS, JavaScript         | —       |

---

## Acesso pelo Servidor

O sistema está hospedado e pode ser acessado diretamente pelo navegador, sem necessidade de instalação local:

```
https://world-cup-manager.onrender.com
```

Basta abrir o link acima em qualquer navegador moderno para utilizar a aplicação completa.

---

## Execução Local

Como alternativa, é possível rodar o projeto localmente seguindo os passos abaixo:

```bash
git clone https://github.com/eianaxz/world-cup-manager.git
cd world-cup-manager
pip install -r requirements.txt
python app.py
```

Antes de executar, crie um arquivo `.env` na raiz do projeto com as variáveis de conexão ao banco de dados:

```env
DB_HOST=seu_host
DB_PORT=sua_porta
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=nome_do_banco
```

As credenciais reais de acesso ao banco não são publicadas neste repositório.

---

## Estrutura do Projeto

```text
world-cup-manager-2026/
│
├── pages/
│   ├── dashboard.py
│   ├── selecoes.py
│   ├── jogadores.py
│   ├── estadios.py
│   ├── partidas.py
│   └── ranking.py
│
├── assets/
│   └── style.css
│
├── database/
│   └── connection.py
│
├── app.py
├── requirements.txt
└── README.md
```

---

## Páginas da Aplicação

| Rota         | Descrição                      |
|--------------|--------------------------------|
| `/`          | Dashboard geral                |
| `/selecoes`  | Gerenciamento de seleções      |
| `/jogadores` | Gerenciamento de jogadores     |
| `/estadios`  | Gerenciamento de estádios      |
| `/partidas`  | Registro e controle de partidas|
| `/ranking`   | Ranking de vitórias            |

---

## Banco de Dados

O banco de dados foi desenvolvido em MySQL e está hospedado no Railway. As tabelas principais são:

| Tabela      | Descrição                                                      |
|-------------|----------------------------------------------------------------|
| `selecoes`  | Dados das seleções participantes da Copa                       |
| `jogadores` | Jogadores cadastrados, vinculados às suas respectivas seleções |
| `estadios`  | Informações dos estádios que sediam as partidas                |
| `partidas`  | Partidas registradas, incluindo gols e vencedor               |

As tabelas se relacionam por meio de chaves estrangeiras. O banco conta com triggers que atualizam automaticamente o campo de vencedor em `partidas` com base nos gols registrados, eliminando a necessidade de atualização manual.

---

## Integrantes

| Nome                   |
|------------------------|
| Ana Clara Souza        |
| Beatriz Kaori          |
| Lucas Santana          |
| Luiz Vinícius Santos   |
| Maria Laura Cordeiro   |
| Pablo Guilherme Neves  |

---

## Objetivo Acadêmico

Este projeto foi desenvolvido como trabalho prático de curso, com o objetivo de aplicar conceitos de desenvolvimento web, modelagem de banco de dados relacional, integração entre front-end e back-end, e hospedagem de aplicações em nuvem. O tema da Copa do Mundo FIFA 2026 foi escolhido como contexto para tornar a aplicação representativa e próxima de um caso de uso real.
