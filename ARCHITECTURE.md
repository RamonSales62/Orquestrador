# 🏗️ Arquitetura do EPI Orchestrator

## Visão Geral

O EPI Orchestrator é uma aplicação de orquestração de decisões baseada em eventos que processa informações de detecção facial e uso de EPIs para tomar decisões automatizadas sobre conformidade de segurança.

## Arquitetura de Alto Nível

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │  Dashboard  │  │  Simulador   │  │   Histórico      │   │
│  │   Stats     │  │  de Eventos  │  │   Decisões       │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Endpoints (routes.py)                │   │
│  │  • POST /api/orchestrate                             │   │
│  │  • GET  /api/stats                                   │   │
│  │  • GET  /api/decisions                               │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │      EpiOrchestrationService (business logic)        │   │
│  │  • evaluate_face_quality()                           │   │
│  │  • evaluate_epi_compliance()                         │   │
│  │  • process_orchestration()                           │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Data Models (Pydantic)                       │   │
│  │  • FaceDetectionEvent                                │   │
│  │  • EpiDetectionEvent                                 │   │
│  │  • OrchestrationDecision                             │   │
│  └──────────────────┬───────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │ Motor (async MongoDB driver)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      MONGODB                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ face_events  │  │  epi_events  │  │    decisions     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Componentes Principais

### 1. Frontend (React)

**Tecnologias:**
- React 19.0.0
- Shadcn/ui (componentes)
- Tailwind CSS (estilização)
- Axios (HTTP client)

**Componentes:**
- **Dashboard**: Exibe estatísticas em tempo real
- **Simulador de Eventos**: Interface para criar e testar eventos
- **Histórico**: Lista de decisões tomadas

**Responsabilidades:**
- Interface do usuário
- Validação de inputs
- Comunicação com backend via REST API
- Atualização em tempo real (polling a cada 5s)

### 2. Backend (FastAPI)

**Tecnologias:**
- FastAPI 0.110.1
- Pydantic para validação
- Motor 3.3.1 (MongoDB async)
- Uvicorn (ASGI server)

**Estrutura:**

```
backend/
├── server.py          # Aplicação principal
│   ├── Models         # Definições Pydantic
│   ├── Services       # Lógica de negócio
│   ├── Endpoints      # Rotas da API
│   └── Config         # Configurações
```

**Responsabilidades:**
- Receber e validar eventos
- Aplicar regras de negócio
- Processar orquestrações
- Persistir dados no MongoDB
- Fornecer APIs REST

### 3. Banco de Dados (MongoDB)

**Collections:**

#### face_events
```json
{
  "id": "uuid",
  "timestamp": "ISO-8601",
  "detected": boolean,
  "confidence": float,
  "quality_score": float,
  "person_id": "string",
  "location": "string",
  "metadata": {}
}
```

#### epi_events
```json
{
  "id": "uuid",
  "timestamp": "ISO-8601",
  "epi_type": "helmet|safety_glasses|...",
  "detected": boolean,
  "confidence": float,
  "properly_worn": boolean,
  "person_id": "string",
  "location": "string",
  "metadata": {}
}
```

#### decisions
```json
{
  "id": "uuid",
  "timestamp": "ISO-8601",
  "decision": "approved|rejected|pending",
  "person_id": "string",
  "location": "string",
  "face_event_id": "uuid",
  "epi_event_ids": ["uuid"],
  "reason": "string",
  "confidence_score": float,
  "metadata": {}
}
```

## Fluxo de Processamento

### 1. Recepção de Eventos

```
Cliente → POST /api/orchestrate
  ↓
Validação Pydantic
  ↓
EpiOrchestrationService
```

### 2. Avaliação de Qualidade Facial

```python
def evaluate_face_quality(face_event):
    if not face_event.detected:
        return False, "Face não detectada"
    
    if face_event.confidence < 0.7:
        return False, "Confiança baixa"
    
    if face_event.quality_score < 0.6:
        return False, "Qualidade insuficiente"
    
    return True, "Detecção facial aprovada"
```

**Critérios:**
- Face detectada: ✅ Sim
- Confiança mínima: ≥ 0.7 (70%)
- Qualidade mínima: ≥ 0.6 (60%)

### 3. Avaliação de Conformidade de EPI

```python
def evaluate_epi_compliance(epi_events, required_epis):
    missing = []
    improperly_worn = []
    low_confidence = []
    
    # Verifica EPIs obrigatórios
    for required in required_epis:
        if required not in detected_types:
            missing.append(required)
    
    # Verifica uso correto
    for epi in epi_events:
        if not epi.properly_worn:
            improperly_worn.append(epi.type)
        if epi.confidence < 0.7:
            low_confidence.append(epi.type)
    
    return all_ok, message, missing
```

**Critérios:**
- Todos EPIs obrigatórios detectados: ✅
- EPIs usados corretamente: ✅
- Confiança por EPI: ≥ 0.7 (70%)

### 4. Tomada de Decisão

```
Face OK? ───┐
            ├──→ Ambos OK? ──→ APROVADO ✅
EPIs OK? ───┘                    ↓
                            Salvar decisão
                                 ↓
                          Retornar resposta

Qualquer falha ──→ REJEITADO ❌
                       ↓
                 Salvar decisão
                       ↓
                 Retornar resposta
```

### 5. Persistência

```
Salvar no MongoDB:
1. face_events collection
2. epi_events collection  
3. decisions collection

Relacionamentos mantidos via IDs
```

## Regras de Negócio

### Configurações de Limiar

| Parâmetro | Valor Mínimo | Descrição |
|-----------|--------------|-----------|
| `face_confidence` | 0.70 | Confiança da detecção facial |
| `face_quality` | 0.60 | Qualidade da imagem facial |
| `epi_confidence` | 0.70 | Confiança por EPI detectado |

### Tipos de EPI Suportados

| Enum | Nome | Descrição |
|------|------|-----------|
| `helmet` | Capacete | Proteção craniana |
| `safety_glasses` | Óculos | Proteção ocular |
| `gloves` | Luvas | Proteção das mãos |
| `safety_shoes` | Botas | Proteção dos pés |
| `vest` | Colete | Visibilidade |
| `mask` | Máscara | Proteção respiratória |

### Status de Decisão

| Status | Descrição |
|--------|-----------|
| `approved` | Acesso aprovado, todos os requisitos atendidos |
| `rejected` | Acesso negado, requisitos não atendidos |
| `pending` | Aguardando processamento (não usado atualmente) |

## APIs REST

### Endpoints Principais

#### 1. Processar Orquestração
```http
POST /api/orchestrate
Content-Type: application/json

{
  "face_event": {...},
  "epi_events": [...],
  "person_id": "string",
  "location": "string",
  "required_epis": ["helmet"]
}

Response: OrchestrationDecision
```

#### 2. Obter Estatísticas
```http
GET /api/stats

Response: {
  "total_face_events": int,
  "total_epi_events": int,
  "total_decisions": int,
  "approved_decisions": int,
  "rejected_decisions": int,
  "pending_decisions": int
}
```

#### 3. Listar Decisões
```http
GET /api/decisions?limit=50&status=approved

Response: [OrchestrationDecision]
```

#### 4. Histórico Completo
```http
GET /api/events/history?limit=50

Response: {
  "face_events": [...],
  "epi_events": [...],
  "decisions": [...]
}
```

## Padrões de Projeto

### 1. Service Layer Pattern
- `EpiOrchestrationService`: Lógica de negócio isolada
- Separação entre endpoints e regras
- Facilita testes e manutenção

### 2. Repository Pattern (Implícito)
- Acesso ao MongoDB através de Motor
- Abstração da persistência
- Queries centralizadas

### 3. DTO Pattern
- Pydantic models como DTOs
- Validação automática
- Serialização/deserialização

### 4. Event-Driven Architecture
- Eventos como primeira classe
- Decisões baseadas em eventos
- Histórico completo auditável

## Segurança

### Validação de Dados
- Pydantic valida todos os inputs
- Type checking automático
- Ranges validados (0.0 - 1.0 para scores)

### CORS
- Configurado via middleware
- Permite origens específicas
- Controle de headers e métodos

### MongoDB
- Exclusão de campo `_id` do MongoDB
- IDs próprios (UUID)
- Prevenção de injeção via Motor

## Performance

### Backend
- FastAPI assíncrono
- Motor (async MongoDB driver)
- Non-blocking I/O

### Frontend
- Lazy loading de componentes
- Debouncing em inputs
- Polling eficiente (5s)

### Database
- Índices automáticos em `_id`
- Queries com limite (`limit`)
- Projeção de campos (`{"_id": 0}`)

## Escalabilidade

### Horizontal
- Backend stateless
- Pode rodar múltiplas instâncias
- Load balancer ready

### Vertical
- MongoDB suporta sharding
- Índices configuráveis
- Agregações otimizáveis

### Cache (Futuro)
- Redis para estatísticas
- Cache de decisões frequentes
- Rate limiting

## Monitoramento

### Logs
```bash
# Backend
tail -f /var/log/supervisor/backend.err.log

# Frontend
tail -f /var/log/supervisor/frontend.out.log
```

### Métricas
- Total de eventos
- Taxa de aprovação/rejeição
- Confiança média
- Eventos por local/pessoa

### Health Check
```http
GET /api/
Response: {"status": "operational"}
```

## Testes

### Backend (Exemplo)
```bash
# Teste de aprovação
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{...}'

# Teste de rejeição
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Frontend
- Interface visual para testes
- Simulador com presets
- Validação em tempo real

## Extensibilidade

### Adicionar Novos EPIs
1. Adicionar ao enum `EpiType`
2. Atualizar `EPI_TYPES` no frontend
3. Sem mudanças no banco (schema-less)

### Customizar Regras
1. Modificar `EpiOrchestrationService`
2. Ajustar limiares de confiança
3. Adicionar novas validações

### Integrações Futuras
- Webhooks para notificações
- WebSocket para tempo real
- APIs externas de detecção
- Machine Learning models

## Deployment

### Desenvolvimento
```bash
sudo supervisorctl restart all
```

### Produção (Recomendações)
- Docker containers
- Kubernetes orchestration
- MongoDB Atlas (cloud)
- CDN para frontend
- Load balancer
- SSL/TLS certificates

## Dependências

### Backend
```
fastapi==0.110.1
uvicorn==0.25.0
motor==3.3.1
pydantic>=2.6.4
python-dotenv>=1.0.1
```

### Frontend
```
react@19.0.0
axios@1.8.4
tailwindcss@3.4.17
lucide-react@0.507.0
```

## Considerações Finais

O EPI Orchestrator foi projetado para ser:
- ✅ **Simples**: Fácil de entender e usar
- ✅ **Escalável**: Pronto para crescer
- ✅ **Extensível**: Fácil de adicionar features
- ✅ **Robusto**: Validação e tratamento de erros
- ✅ **Auditável**: Histórico completo de eventos

---

**Versão:** 1.0.0  
**Última atualização:** Dezembro 2025
