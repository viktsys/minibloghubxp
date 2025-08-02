# Setup do Projeto Mini Blog Hub XP

Este guia explica como configurar e executar o projeto Mini Blog Hub XP, incluindo backend FastAPI e frontend.

## Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- SQLite (incluído no Python)

## Configuração do Backend

### 1. Navegue para o diretório do backend

```bash
cd backend
```

### 2. Instale as dependências

```bash
pip3 install -r requirements.txt
```

**Nota:** Se você estiver usando zsh (shell padrão no macOS), pode ser necessário usar aspas ao instalar pacotes com colchetes:

```bash
pip3 install "passlib[bcrypt]"
```

### 3. Configure o banco de dados

#### 3.1 Crie a migração inicial (se não existir)

```bash
alembic revision --autogenerate -m "Initial migration"
```

#### 3.2 Aplique as migrações

```bash
alembic upgrade head
```

### 4. Crie um usuário administrador

Execute o script para criar um usuário administrador:

```bash
python3 scripts/create_admin.py
```

Você será solicitado a fornecer:
- Username
- Email
- Nome completo (opcional)
- Senha
- Confirmação da senha

### 5. Execute o servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O backend estará disponível em: `http://localhost:8000`

## Dependências Principais

### Backend
- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para banco de dados
- **Alembic**: Ferramenta de migração de banco de dados
- **Passlib**: Biblioteca para hash de senhas
- **BCrypt**: Algoritmo de hash seguro para senhas
- **Python-JOSE**: Biblioteca para tokens JWT
- **Uvicorn**: Servidor ASGI

## Estrutura do Projeto

```
minibloghubxp/
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints da API
│   │   ├── core/         # Configurações e segurança
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── schemas/      # Schemas Pydantic
│   │   └── services/     # Lógica de negócio
│   ├── alembic/          # Migrações do banco
│   ├── scripts/          # Scripts utilitários
│   └── requirements.txt  # Dependências Python
└── frontend/             # Aplicação frontend
```

## Problemas Comuns e Soluções

### 1. Erro "ModuleNotFoundError: No module named 'passlib'"

**Solução:** Instale a biblioteca passlib com suporte ao bcrypt:
```bash
pip3 install "passlib[bcrypt]"
```

### 2. Erro no Alembic: "configparser.InterpolationSyntaxError"

**Problema:** O caractere `%` no arquivo `alembic.ini` precisa ser escapado.

**Solução:** No arquivo `alembic.ini`, altere:
```ini
version_num_format = %04d
```
Para:
```ini
version_num_format = %%04d
```

### 3. Erro "no such table: users"

**Problema:** O banco de dados não foi inicializado com as tabelas necessárias.

**Solução:** Execute as migrações do Alembic:
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. Problemas com shell zsh (macOS)

Se você estiver usando zsh e encontrar problemas com colchetes em comandos pip, use aspas:
```bash
pip3 install "package[extra]"
```

## Endpoints da API

Após iniciar o servidor, você pode acessar:

- **Documentação Swagger**: `http://localhost:8000/docs`
- **Documentação ReDoc**: `http://localhost:8000/redoc`
- **API Base**: `http://localhost:8000/api/v1/`

## Scripts Utilitários

### Criar usuário administrador
```bash
python3 scripts/create_admin.py
```

## Próximos Passos

1. Configure o frontend (instruções específicas dependem da tecnologia usada)
2. Configure variáveis de ambiente se necessário
3. Configure um servidor de produção (ex: nginx + gunicorn)
4. Configure backup do banco de dados

## Troubleshooting

Se você encontrar outros problemas:

1. Verifique se todas as dependências estão instaladas corretamente
2. Certifique-se de estar no diretório correto (`backend/`)
3. Verifique a versão do Python (`python3 --version`)
4. Consulte os logs do servidor para mensagens de erro detalhadas

## Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Implemente suas mudanças
4. Execute os testes
5. Submeta um pull request
