# 🛡️ EPI Orchestrator

Sistema inteligente de orquestração de decisões baseado em eventos de detecção facial e EPI (Equipamentos de Proteção Individual).

## 📋 Descrição

O **EPI Orchestrator** é uma aplicação full-stack que processa eventos de detecção facial e uso de EPIs para tomar decisões automatizadas sobre acesso e conformidade de segurança.

### Características Principais

- ✅ **Detecção Facial Inteligente**: Avalia qualidade e confiança da detecção
- 🦺 **Validação de EPIs**: Verifica presença e uso correto de equipamentos obrigatórios
- 🎯 **Decisões Automatizadas**: Aprova ou rejeita acessos baseado em regras configuráveis
- 📊 **Dashboard em Tempo Real**: Visualização de estatísticas e histórico
- 🧪 **Simulador de Eventos**: Interface para testar diferentes cenários
- 💾 **Armazenamento MongoDB**: Histórico completo de eventos e decisões

## 🏗️ Arquitetura

### Backend (FastAPI)
- Python 3.11+
- FastAPI para APIs REST
- MongoDB (Motor) para persistência
- Pydantic para validação de dados

### Frontend (React)
- React 19
- Shadcn/ui para componentes
- Tailwind CSS para estilização
- Axios para comunicação com API

## 🚀 Como Usar

### 1. Acesse o Dashboard

Abra seu navegador e acesse a aplicação. Você verá:

- **Estatísticas em tempo real** (total de decisões, aprovações, rejeições)
- **Simulador de eventos** para testes
- **Histórico de decisões** tomadas

### 2. Simular Eventos

Na aba **Simulador**:

1. Configure as **Informações Gerais**:
   - ID da Pessoa (opcional)
   - Local (ex: "Entrada Principal")

2. Configure a **Detecção Facial**:
   - Face Detectada (sim/não)
   - Confiança (0-100%)
   - Qualidade (0-100%)

3. Configure os **EPIs**:
   - Adicione EPIs necessários
   - Selecione o tipo (Capacete, Óculos, etc.)
   - Configure se foi detectado e usado corretamente
   - Ajuste a confiança da detecção

4. Clique em **Processar Orquestração**

### 3. Visualizar Resultados

- O sistema retornará uma decisão **Aprovado** ✅ ou **Rejeitado** ❌
- Acesse a aba **Histórico** para ver todas as decisões
- As estatísticas são atualizadas automaticamente

## 📡 API Endpoints

### Informações do Sistema

```bash
GET /api/
# Retorna informações da API

GET /api/stats
# Retorna estatísticas do sistema
```

### Eventos

```bash
POST /api/events/face
# Registra evento de detecção facial

POST /api/events/epi
# Registra evento de detecção de EPI

GET /api/events/history?limit=50
# Retorna histórico de eventos
```

### Orquestração

```bash
POST /api/orchestrate
# Processa orquestração completa e retorna decisão

GET /api/decisions?limit=50&status=approved
# Lista decisões tomadas
```

### Utilidades

```bash
DELETE /api/events/clear
# Limpa todos os eventos (apenas desenvolvimento)
```

## 🧪 Exemplos de Uso da API

### Exemplo 1: Acesso Aprovado

```bash
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

**Resposta:**
```json
{
  "id": "...",
  "decision": "approved",
  "reason": "Acesso aprovado. Detecção facial aprovada. Todos os EPIs obrigatórios detectados e corretamente utilizados",
  "confidence_score": 0.92
}
```

### Exemplo 2: Acesso Negado

```bash
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "face_event": {
      "detected": true,
      "confidence": 0.50,
      "quality_score": 0.40
    },
    "epi_events": [
      {
        "epi_type": "helmet",
        "detected": false,
        "confidence": 0.30,
        "properly_worn": false
      }
    ],
    "person_id": "FUNC-002",
    "location": "Entrada Principal",
    "required_epis": ["helmet"]
  }'
```

**Resposta:**
```json
{
  "id": "...",
  "decision": "rejected",
  "reason": "Acesso negado. Confiança da detecção facial muito baixa: 0.50 EPIs não detectados: helmet",
  "confidence_score": 0.0
}
```

## ⚙️ Regras de Decisão

### Detecção Facial
- ✅ Face deve ser detectada
- ✅ Confiança mínima: 70%
- ✅ Qualidade mínima: 60%

### EPIs
- ✅ Todos os EPIs obrigatórios devem ser detectados
- ✅ EPIs devem estar sendo usados corretamente
- ✅ Confiança mínima por EPI: 70%

### Decisão Final
- **Aprovado**: Face OK + Todos EPIs OK
- **Rejeitado**: Qualquer falha na detecção ou conformidade

## 🎨 Tipos de EPI Suportados

- 🪖 **helmet**: Capacete
- 👓 **safety_glasses**: Óculos de Segurança
- 🧤 **gloves**: Luvas
- 👢 **safety_shoes**: Botas de Segurança
- 🦺 **vest**: Colete
- 😷 **mask**: Máscara

## 📊 Estrutura de Dados

### FaceDetectionEvent
```json
{
  "detected": true,
  "confidence": 0.95,
  "quality_score": 0.90,
  "person_id": "FUNC-001",
  "location": "Entrada Principal"
}
```

### EpiDetectionEvent
```json
{
  "epi_type": "helmet",
  "detected": true,
  "confidence": 0.92,
  "properly_worn": true,
  "person_id": "FUNC-001",
  "location": "Entrada Principal"
}
```

### OrchestrationDecision
```json
{
  "id": "uuid",
  "timestamp": "2025-12-17T17:40:43.227448Z",
  "decision": "approved",
  "person_id": "FUNC-001",
  "location": "Entrada Principal",
  "face_event_id": "uuid",
  "epi_event_ids": ["uuid"],
  "reason": "Motivo da decisão",
  "confidence_score": 0.92,
  "metadata": {}
}
```

## 🔧 Serviços

O sistema utiliza supervisor para gerenciar os serviços:

```bash
# Reiniciar todos os serviços
sudo supervisorctl restart all

# Verificar status
sudo supervisorctl status

# Logs do backend
tail -f /var/log/supervisor/backend.err.log

# Logs do frontend
tail -f /var/log/supervisor/frontend.out.log
```

## 🌐 Portas

- **Backend**: `http://localhost:8001`
- **Frontend**: `http://localhost:3000`
- **MongoDB**: `mongodb://localhost:27017`

## 📝 Casos de Uso

### 1. Controle de Acesso a Áreas Restritas
- Validação facial + EPI obrigatório
- Registro de tentativas de acesso
- Auditoria completa

### 2. Conformidade de Segurança
- Verificação de uso correto de EPIs
- Alertas em tempo real
- Relatórios de conformidade

### 3. Monitoramento de Canteiros de Obras
- Detecção de trabalhadores sem EPIs
- Análise de padrões de segurança
- Estatísticas de conformidade

## 🛠️ Tecnologias Utilizadas

### Backend
- FastAPI 0.110.1
- Motor 3.3.1 (MongoDB async)
- Pydantic 2.6.4
- Uvicorn 0.25.0

### Frontend
- React 19.0.0
- Shadcn/ui
- Tailwind CSS 3.4.17
- Axios 1.8.4
- Lucide React (ícones)

## 📈 Melhorias Futuras

- [ ] Integração com câmeras em tempo real
- [ ] Machine Learning para detecção automática
- [ ] Notificações em tempo real (WebSocket)
- [ ] Relatórios exportáveis (PDF/Excel)
- [ ] Múltiplos níveis de permissão
- [ ] Dashboard administrativo avançado
- [ ] API de webhooks para integrações

## 📄 Licença

Este projeto foi criado para demonstração do sistema de orquestração de EPIs.

---

**Desenvolvido com ❤️ usando FastAPI + React + MongoDB**
