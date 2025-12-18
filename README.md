# 🛡️ EPI Orchestrator

Sistema inteligente de orquestração de decisões baseado em eventos de detecção facial e EPI (Equipamentos de Proteção Individual).

## 📋 Visão Geral

O **EPI Orchestrator** é uma aplicação full-stack que processa eventos de detecção facial e uso de EPIs para tomar decisões automatizadas sobre acesso e conformidade de segurança.

### ✨ Características Principais

- ✅ **Detecção Facial Inteligente**: Avalia qualidade e confiança da detecção
- 🦺 **Validação de EPIs**: Verifica presença e uso correto de equipamentos obrigatórios
- 🎯 **Decisões Automatizadas**: Aprova ou rejeita acessos baseado em regras configuráveis
- 📊 **Dashboard em Tempo Real**: Visualização de estatísticas e histórico
- 🧪 **Simulador de Eventos**: Interface para testar diferentes cenários
- 💾 **SQLite Database**: Banco de dados leve e sem configuração

## 🏗️ Stack Tecnológica

### Backend
- **Python 3.11+**
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **SQLite** - Banco de dados leve (via aiosqlite)
- **Pydantic** - Validação de dados

### Frontend
- **React 19**
- **Shadcn/ui** - Componentes de interface
- **Tailwind CSS** - Framework CSS
- **Axios** - Cliente HTTP

## 📦 Pré-requisitos

### Backend
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Frontend
- Node.js 16+ e npm/yarn
- (Recomendado: yarn)

## 🚀 Instalação e Execução

### Método 1: Setup Automático (Recomendado)

#### Linux / macOS

```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd epi-orchestrator

# 2. Dê permissão de execução ao script
chmod +x setup.sh

# 3. Execute o script de setup
./setup.sh
```

#### Windows

```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd epi-orchestrator

# 2. Execute o script de setup
setup.bat
```

### Método 2: Setup Manual

#### 1. Setup do Backend

```bash
# Entre no diretório do backend
cd backend

# Crie um ambiente virtual Python
python3 -m venv venv

# Ative o ambiente virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure o arquivo .env (opcional, já tem valores padrão)
cp .env.example .env
# Edite .env se necessário

# Execute o servidor
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

O backend estará rodando em: `http://localhost:8001`

#### 2. Setup do Frontend

```bash
# Em outro terminal, entre no diretório do frontend
cd frontend

# Instale as dependências
yarn install
# ou
npm install

# Configure o arquivo .env
cp .env.example .env
# Edite .env e configure o REACT_APP_BACKEND_URL se necessário

# Execute o servidor de desenvolvimento
yarn start
# ou
npm start
```

O frontend estará rodando em: `http://localhost:3000`

## ⚙️ Configuração

### Backend (.env)

```env
# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./epi_orchestrator.db

# CORS Configuration
CORS_ORIGINS=*

# Server Configuration
HOST=0.0.0.0
PORT=8001
```

**Opções de DATABASE_URL:**
- Local: `sqlite+aiosqlite:///./epi_orchestrator.db`
- Caminho absoluto: `sqlite+aiosqlite:////path/to/database.db`
- Memória (teste): `sqlite+aiosqlite:///:memory:`

### Frontend (.env)

```env
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8001
```

**Importante:** Altere `REACT_APP_BACKEND_URL` para o endereço do seu backend:
- Desenvolvimento local: `http://localhost:8001`
- Servidor remoto: `http://seu-ip:8001` ou `https://seu-dominio.com`

## 📖 Como Usar

### 1. Acesse o Dashboard

Abra `http://localhost:3000` no navegador. Você verá:

- **Estatísticas em tempo real** (total de decisões, aprovações, rejeições)
- **Simulador de eventos** para testes
- **Histórico de decisões** tomadas

### 2. Simular Eventos

Na aba **Simulador**:

1. **Informações Gerais**:
   - ID da Pessoa (opcional): Ex: "FUNC-001"
   - Local: Ex: "Entrada Principal"

2. **Detecção Facial**:
   - Marque se a face foi detectada
   - Ajuste a confiança (0-100%)
   - Ajuste a qualidade (0-100%)

3. **EPIs**:
   - Clique em "Adicionar EPI"
   - Selecione o tipo (Capacete, Óculos, etc.)
   - Configure se foi detectado
   - Configure se está sendo usado corretamente
   - Ajuste a confiança da detecção

4. Clique em **"Processar Orquestração"**

### 3. Visualizar Resultados

- O sistema retornará ✅ **Aprovado** ou ❌ **Rejeitado**
- Acesse a aba **Histórico** para ver todas as decisões
- As estatísticas são atualizadas automaticamente

## 📡 API REST

### Documentação Interativa

Acesse: `http://localhost:8001/docs` (Swagger UI)

### Endpoints Principais

#### Informações
```bash
GET /api/
GET /api/stats
```

#### Eventos
```bash
POST /api/events/face        # Registrar evento facial
POST /api/events/epi         # Registrar evento de EPI
GET  /api/events/history     # Histórico completo
```

#### Orquestração
```bash
POST /api/orchestrate        # Processar decisão completa
GET  /api/decisions          # Listar decisões
```

#### Utilidades
```bash
DELETE /api/events/clear     # Limpar todos os dados (dev)
```

### Exemplo de Uso

```bash
# Processar uma orquestração completa
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "face_event": {
      "detected": true,
      "confidence": 0.95,
      "quality_score": 0.90
    },
    "epi_events": [
      {
        "epi_type": "helmet",
        "detected": true,
        "confidence": 0.92,
        "properly_worn": true
      }
    ],
    "person_id": "FUNC-001",
    "location": "Entrada Principal",
    "required_epis": ["helmet"]
  }'
```

## 🗄️ Banco de Dados

### SQLite

A aplicação usa **SQLite**, um banco de dados leve e sem servidor que:
- ✅ Não requer instalação ou configuração
- ✅ Armazena tudo em um único arquivo (`epi_orchestrator.db`)
- ✅ Perfeito para desenvolvimento e produção de pequeno/médio porte
- ✅ Fácil backup (copie o arquivo .db)

### Localização do Banco

Por padrão: `backend/epi_orchestrator.db`

### Backup

```bash
# Fazer backup
cp backend/epi_orchestrator.db backend/epi_orchestrator.backup.db

# Restaurar backup
cp backend/epi_orchestrator.backup.db backend/epi_orchestrator.db
```

### Limpar Dados

```bash
# Via API
curl -X DELETE http://localhost:8001/api/events/clear

# Ou simplesmente delete o arquivo
rm backend/epi_orchestrator.db
# O banco será recriado automaticamente ao reiniciar
```

## 🔧 Desenvolvimento

### Estrutura do Projeto

```
epi-orchestrator/
├── backend/
│   ├── server.py           # Aplicação FastAPI principal
│   ├── database.py         # Configuração do SQLite
│   ├── models.py           # Modelos SQLAlchemy
│   ├── requirements.txt    # Dependências Python
│   ├── .env               # Configurações (não commitado)
│   └── .env.example       # Exemplo de configurações
├── frontend/
│   ├── src/
│   │   ├── App.js         # Componente principal React
│   │   ├── App.css        # Estilos
│   │   └── components/    # Componentes UI
│   ├── package.json       # Dependências Node
│   ├── .env              # Configurações (não commitado)
│   └── .env.example      # Exemplo de configurações
├── README.md
├── ARCHITECTURE.md
├── EXAMPLES.md
├── setup.sh              # Script de setup Linux/Mac
└── setup.bat             # Script de setup Windows
```

### Executar em Modo de Desenvolvimento

#### Backend
```bash
cd backend
source venv/bin/activate  # Linux/Mac
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

#### Frontend
```bash
cd frontend
yarn start  # ou npm start
```

## 🚢 Deploy em Produção

### Backend

1. **Configure variáveis de ambiente**:
```bash
export DATABASE_URL="sqlite+aiosqlite:///./production.db"
export CORS_ORIGINS="https://seu-dominio.com"
```

2. **Execute com Gunicorn** (recomendado):
```bash
pip install gunicorn uvicorn[standard]
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Frontend

1. **Build para produção**:
```bash
cd frontend
yarn build  # ou npm run build
```

2. **Sirva os arquivos estáticos** (exemplo com nginx, apache, ou qualquer servidor web)

### Docker (Opcional)

Arquivos Docker podem ser criados para facilitar o deploy:

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

## 🧪 Testes

### Testar API via cURL

```bash
# Teste básico
curl http://localhost:8001/api/

# Ver estatísticas
curl http://localhost:8001/api/stats

# Processar evento
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

### Interface de Teste

Use o simulador integrado no frontend para testes interativos!

## ⚡ Performance

- Backend assíncrono (FastAPI + async SQLAlchemy)
- Frontend com React 19 (renderização otimizada)
- SQLite com queries otimizadas
- Polling eficiente (5s)

## 🔒 Segurança

- ✅ Validação de dados com Pydantic
- ✅ CORS configurável
- ✅ Type checking automático
- ✅ SQL injection prevention (SQLAlchemy ORM)

## 📚 Documentação Adicional

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Documentação técnica detalhada
- [EXAMPLES.md](./EXAMPLES.md) - Exemplos práticos de uso

## ❓ Troubleshooting

### Erro: "ModuleNotFoundError"
```bash
# Certifique-se de ativar o ambiente virtual
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "Port already in use"
```bash
# Mude a porta no backend/.env ou frontend/.env
# Ou mate o processo:
# Linux/Mac:
lsof -ti:8001 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Erro: "CORS"
```bash
# Configure CORS_ORIGINS no backend/.env
CORS_ORIGINS=http://localhost:3000,https://seu-dominio.com
```

### Banco de dados corrompido
```bash
# Delete e recrie
rm backend/epi_orchestrator.db
# Reinicie o backend - o banco será recriado
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação
2. Consulte os exemplos em EXAMPLES.md
3. Abra uma issue no repositório

## 📄 Licença

Este projeto foi criado para demonstração do sistema de orquestração de EPIs.

---

**Desenvolvido com ❤️ usando FastAPI + React + SQLite**

**Versão:** 1.0.0  
**Última atualização:** Dezembro 2025
