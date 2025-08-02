# Mini Blog Hub XP - Especificação Técnica

## Visão Geral

Este projeto consiste no desenvolvimento de um mini blog com integração de APIs externas, permitindo importação de posts do JSONPlaceholder, criação de posts próprios, adição de imagens do Unsplash e sistema de comentários.

**Tempo estimado:** 3-4 horas

## APIs Externas

### JSONPlaceholder
- **URL:** https://jsonplaceholder.typicode.com/
- **Propósito:** Importar posts iniciais para popular o blog
- **Endpoints utilizados:**
  - `GET /posts` - Listar todos os posts
  - `GET /posts/{id}` - Obter post específico
  - `GET /posts/{id}/comments` - Obter comentários do post

### Unsplash API
- **URL:** https://unsplash.com/developers
- **Propósito:** Adicionar imagens de alta qualidade aos posts
- **Endpoints utilizados:**
  - `GET /search/photos` - Buscar imagens por palavra-chave
  - `GET /photos/{id}` - Obter detalhes de uma imagem específica

## Stack Tecnológica

### Backend
- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0 + Alembic
- **Banco de Dados:** 
  - Desenvolvimento: SQLite
  - Produção: PostgreSQL
- **Autenticação:** JWT com python-jose + bcrypt
- **Validação:** Pydantic Models + Custom Validators

### Frontend
- **Framework:** Next.js com TypeScript
- **Rendering:** SSR/SSG onde apropriado
- **Styling:** CSS Modules ou Styled Components
- **State Management:** React Context API ou Zustand
- **Validação:** React Hook Form + Zod

## Funcionalidades Principais

### 1. Importação de Posts (JSONPlaceholder)
- [ ] Endpoint para importar posts do JSONPlaceholder
- [ ] Comando CLI com Typer para importação em lote
- [ ] Tratamento de duplicatas
- [ ] Mapeamento de dados (userId → author, etc.)

### 2. CRUD de Posts Próprios
- [ ] **Create:** Criar novos posts
- [ ] **Read:** Listar e visualizar posts
- [ ] **Update:** Editar posts existentes
- [ ] **Delete:** Remover posts (soft delete)

### 3. Sistema de Imagens (Unsplash)
- [ ] Busca de imagens por palavra-chave
- [ ] Seleção e vinculação de imagens aos posts
- [ ] Cache de URLs de imagens
- [ ] Otimização de imagens (lazy loading)

### 4. Sistema de Comentários
- [ ] Adicionar comentários em posts
- [ ] Listar comentários por post
- [ ] Editar/excluir comentários próprios
- [ ] Sistema de moderação básico

## Modelos de Dados

### Post
```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    image_url = Column(String, nullable=True)
    image_caption = Column(String(500), nullable=True)
    is_imported = Column(Boolean, default=False)
    external_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
```

### Comment
```python
class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
```

## Schemas Pydantic

### Post Schemas
```python
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str
    image_url: Optional[HttpUrl] = None
    image_caption: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    title: Optional[str] = None
    content: Optional[str] = None

class PostInDB(PostBase):
    id: int
    author_id: int
    is_imported: bool
    external_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class Post(PostInDB):
    author: "User"
    comments: List["Comment"] = []
```

### Comment Schemas
```python
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentUpdate(CommentBase):
    content: Optional[str] = None

class CommentInDB(CommentBase):
    id: int
    post_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class Comment(CommentInDB):
    author: "User"
```

## API Endpoints

### Posts
- `GET /api/posts/` - Listar posts (paginado)
- `POST /api/posts/` - Criar novo post
- `GET /api/posts/{id}/` - Obter post específico
- `PUT /api/posts/{id}/` - Atualizar post
- `DELETE /api/posts/{id}/` - Excluir post
- `POST /api/posts/import/` - Importar posts do JSONPlaceholder

### Comentários
- `GET /api/posts/{id}/comments/` - Listar comentários do post
- `POST /api/posts/{id}/comments/` - Adicionar comentário
- `PUT /api/comments/{id}/` - Editar comentário
- `DELETE /api/comments/{id}/` - Excluir comentário

### Imagens
- `GET /api/images/search/` - Buscar imagens no Unsplash
- `POST /api/images/select/` - Selecionar imagem para post

## Componentes Frontend (Reutilizáveis)

### 1. PostCard
- Exibição resumida do post
- Imagem, título, autor, data
- Link para post completo

### 2. PostForm
- Formulário para criar/editar posts
- Integração com busca de imagens
- Validação em tempo real

### 3. CommentList
- Lista de comentários
- Paginação
- Sistema de respostas (opcional)

### 4. ImagePicker
- Interface para buscar imagens no Unsplash
- Preview de imagens
- Seleção de imagem

### 5. Layout
- Header com navegação
- Footer
- Sidebar (opcional)

## Páginas Frontend

### 1. Home (`/`)
- Lista de posts (SSG)
- Paginação
- Filtros básicos

### 2. Post Detail (`/posts/[id]`)
- Visualização completa do post (SSR)
- Comentários
- SEO otimizado

### 3. Create/Edit Post (`/posts/new`, `/posts/[id]/edit`)
- Formulário de criação/edição
- Preview em tempo real
- Integração com Unsplash

### 4. Dashboard (`/dashboard`)
- Lista de posts do usuário
- Estatísticas básicas
- Links rápidos

## Validações

### Backend (FastAPI)
- Validação automática com Pydantic models
- Sanitização de HTML
- Validação de URLs
- Rate limiting com slowapi
- Middleware de validação customizado

### Frontend (Next.js)
- Validação de formulários com Zod
- Feedback visual de erros
- Validação em tempo real
- Prevenção de submissões duplicadas

## SEO e Performance

### SSR/SSG Strategy
- **SSG:** Páginas estáticas (home, posts populares)
- **SSR:** Páginas dinâmicas (post detail, dashboard)
- **ISR:** Regeneração incremental para posts

### SEO Optimization
- Meta tags dinâmicas
- Open Graph tags
- Schema.org markup
- URLs amigáveis
- Sitemap automático

### Performance
- Lazy loading de imagens
- Code splitting
- Caching de API responses
- Otimização de imagens (Next.js Image)

## Recursos Diferenciais

### 1. Rich Text Editor
- [ ] Integração com editor WYSIWYG (ex: Quill.js, TinyMCE)
- [ ] Suporte a markdown
- [ ] Preview em tempo real
- [ ] Inserção de imagens inline

### 2. Tags e Categorias
- [ ] Sistema de tags
- [ ] Categorias hierárquicas
- [ ] Filtros por tag/categoria
- [ ] Tag cloud

### 3. SEO Avançado
- [ ] Meta tags personalizáveis
- [ ] Análise de SEO score
- [ ] Sugestões de otimização
- [ ] Canonical URLs

## Configuração de Desenvolvimento

### Backend Setup
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Instalar dependências
pip install fastapi[all] uvicorn sqlalchemy alembic python-decouple requests typer bcrypt python-jose[cryptography] slowapi

# Configurar banco de dados
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Criar usuário admin (script personalizado)
python scripts/create_admin.py

# Importar posts iniciais
python -m typer app.cli run import-posts
```

### Frontend Setup
```bash
# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local

# Executar desenvolvimento
npm run dev
```

## Variáveis de Ambiente

### Backend (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key-for-jwt
DATABASE_URL=sqlite:///./blog.db
UNSPLASH_ACCESS_KEY=your-unsplash-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_UNSPLASH_ACCESS_KEY=your-unsplash-key
```

## Estrutura de Pastas

```
minibloghubxp/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── post.py
│   │   │   ├── user.py
│   │   │   └── comment.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── post.py
│   │   │   ├── user.py
│   │   │   └── comment.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── posts.py
│   │   │   │   ├── comments.py
│   │   │   │   ├── images.py
│   │   │   │   └── auth.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── post_service.py
│   │   │   ├── unsplash_service.py
│   │   │   └── jsonplaceholder_service.py
│   │   ├── cli.py
│   │   └── main.py
│   ├── alembic/
│   ├── scripts/
│   │   └── create_admin.py
│   ├── requirements.txt
│   └── alembic.ini
├── frontend/
│   ├── components/
│   │   ├── PostCard.tsx
│   │   ├── PostForm.tsx
│   │   └── ImagePicker.tsx
│   ├── pages/
│   │   ├── index.tsx
│   │   ├── posts/
│   │   └── dashboard/
│   ├── utils/
│   └── styles/
├── docs/
├── README.md
└── SPECIFICATION.md
```

## Critérios de Aceite

### Funcionalidades Básicas
- [ ] Importação bem-sucedida de posts do JSONPlaceholder
- [ ] CRUD completo de posts funcionando
- [ ] Busca e seleção de imagens do Unsplash
- [ ] Sistema de comentários operacional
- [ ] API RESTful documentada (OpenAPI/Swagger automático)

### Qualidade de Código
- [ ] Componentes reutilizáveis implementados
- [ ] Validações front e back funcionando
- [ ] Testes unitários básicos
- [ ] Code coverage > 70%

### Performance e SEO
- [ ] SSR/SSG implementado corretamente
- [ ] Métricas de performance (Lighthouse) > 80
- [ ] Meta tags e SEO básico implementado
- [ ] Responsividade mobile

### Documentação
- [ ] README detalhado com instruções
- [ ] Documentação da API
- [ ] Comentários no código
- [ ] Guia de deploy

## Cronograma Sugerido

### Hora 1: Setup e Backend Base
- Configuração do ambiente FastAPI
- Modelos SQLAlchemy
- API básica (CRUD posts)
- Configuração Alembic

### Hora 2: Integração APIs Externas
- Importação JSONPlaceholder
- Integração Unsplash
- Sistema de comentários

### Hora 3: Frontend Base
- Setup Next.js
- Componentes básicos
- Páginas principais

### Hora 4: Refinamentos e Deploy
- Validações
- SEO básico
- Testes
- Deploy e documentação

## Considerações de Deploy

### Backend (FastAPI)
- Usar Uvicorn com Gunicorn como ASGI server
- Configurar banco PostgreSQL
- Variáveis de ambiente seguras
- Configuração de CORS para produção

### Frontend (Next.js)
- Build otimizado para produção
- Configuração de domínio
- Cache strategies
- CDN para assets

---

**Autor:** Desenvolvido como parte do teste técnico Mini Blog Hub XP  
**Data:** 30 de Julho de 2025  
**Versão:** 1.0
