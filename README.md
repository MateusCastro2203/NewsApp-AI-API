# NewsBot Backend

NewsBot é um backend em FastAPI para uma aplicação de chatbot sobre notícias, integrando a API da OpenAI. O sistema permite que usuários cadastrados façam perguntas sobre notícias, salvem notícias favoritas e mantenham contexto das conversas.

## 📋 Funcionalidades

- **Processamento de Notícias**: Extração automática de conteúdo a partir de URLs
- **Chatbot Inteligente**: Integração com OpenAI para respostas contextualizadas
- **Persistência de Conversas**: Histórico de conversas armazenado no MongoDB
- **Gerenciamento de Usuários**: Cadastro e autenticação de usuários
- **Favoritos**: Sistema para salvar e recuperar notícias favoritas

## 🛠️ Tecnologias

- [Python 3.8+](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [MongoDB](https://www.mongodb.com/) via [Motor](https://motor.readthedocs.io/)
- [OpenAI API](https://beta.openai.com/docs/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.8+
- MongoDB (local ou Atlas)
- Chave da API OpenAI

### Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/newsbot-backend.git
   cd newsbot-backend
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Crie um arquivo `.env` na raiz do projeto:
   ```
   MONGO_URL=mongodb+srv://seu-usuario:sua-senha@cluster.mongodb.net/newsbot
   OPENAI_API_KEY=sua-chave-da-api-openai
   ```

### Executando o projeto

```bash
uvicorn app.main:app --reload
```

O servidor será iniciado em `http://localhost:8000`

## 📝 Documentação da API

Após iniciar o servidor, acesse:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Principais Endpoints

#### Usuários

- `POST /users` - Criar novo usuário
- `GET /users/{user_id}` - Obter dados de um usuário

#### Chat

- `POST /chat` - Enviar mensagem e receber resposta da IA
- `GET /chat/{user_id}` - Obter histórico de conversas do usuário

#### Favoritos

- `POST /favorites` - Salvar notícia como favorita
- `GET /favorites/{user_id}` - Listar favoritos do usuário

## 📁 Estrutura do Projeto

```
newsbot-backend/
│
├── app/                      # Pacote principal
│   ├── main.py               # Ponto de entrada da aplicação
│   ├── routers/              # Rotas da API
│   │   ├── chat.py           # Endpoints de chat
│   │   ├── user.py           # Endpoints de usuário
│   │   └── favorites.py      # Endpoints de favoritos
│   │
│   ├── services/             # Lógica de negócios
│   │   ├── openai_services.py # Comunicação com OpenAI
│   │   └── news_services.py   # Processamento de notícias
│   │
│   ├── models/               # Modelos de dados
│   │   └── chat.py           # Modelo de requisições de chat
│   │
│   └── database/             # Configuração de banco de dados
│       └── mongo.py          # Conexão com MongoDB
│
├── .env                      # Variáveis de ambiente
└── requirements.txt          # Dependências do projeto
```

## 🌐 Deploy

### Deploy na Vercel

1. Configure `vercel.json` na raiz do projeto:

   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app/main.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app/main.py"
       }
     ]
   }
   ```

2. Faça o deploy:

   ```bash
   vercel login
   vercel
   ```

3. Configure as variáveis de ambiente no dashboard da Vercel.

## 🔮 Próximos Passos

- [ ] Autenticação JWT
- [ ] Análise de sentimento de notícias
- [ ] Sumarização automática
- [ ] Sistema de recomendação
- [ ] Integração com mais fontes de notícias

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

---

Desenvolvido como parte do projeto de chatbot para app de notícias.
