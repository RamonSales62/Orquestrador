# 📚 Exemplos Práticos - EPI Orchestrator

Este documento contém exemplos práticos de uso do EPI Orchestrator para diferentes cenários reais.

## 📋 Índice

1. [Cenários de Aprovação](#cenários-de-aprovação)
2. [Cenários de Rejeição](#cenários-de-rejeição)
3. [Casos de Uso por Setor](#casos-de-uso-por-setor)
4. [Exemplos de Integração](#exemplos-de-integração)

---

## Cenários de Aprovação

### ✅ Exemplo 1: Trabalhador em Conformidade Total

**Contexto:** Funcionário acessando área de construção com todos os EPIs obrigatórios.

```bash
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "face_event": {
      "detected": true,
      "confidence": 0.98,
      "quality_score": 0.95
    },
    "epi_events": [
      {
        "epi_type": "helmet",
        "detected": true,
        "confidence": 0.96,
        "properly_worn": true
      },
      {
        "epi_type": "safety_glasses",
        "detected": true,
        "confidence": 0.94,
        "properly_worn": true
      },
      {
        "epi_type": "gloves",
        "detected": true,
        "confidence": 0.91,
        "properly_worn": true
      },
      {
        "epi_type": "safety_shoes",
        "detected": true,
        "confidence": 0.93,
        "properly_worn": true
      }
    ],
    "person_id": "TRAB-001",
    "location": "Canteiro de Obras - Bloco A",
    "required_epis": ["helmet"]
  }'
```

**Resposta Esperada:**
```json
{
  "decision": "approved",
  "reason": "Acesso aprovado. Detecção facial aprovada. Todos os EPIs obrigatórios detectados e corretamente utilizados",
  "confidence_score": 0.91
}
```

---

### ✅ Exemplo 2: Entrada em Área de Baixo Risco

**Contexto:** Funcionário administrativo acessando escritório sem EPIs obrigatórios.

```bash
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "face_event": {
      "detected": true,
      "confidence": 0.92,
      "quality_score": 0.88
    },
    "epi_events": [],
    "person_id": "ADM-042",
    "location": "Escritório Central",
    "required_epis": []
  }'
```

**Resposta Esperada:**
```json
{
  "decision": "approved",
  "reason": "Acesso aprovado. Detecção facial aprovada. Todos os EPIs obrigatórios detectados e corretamente utilizados",
  "confidence_score": 1.0
}
```

---

### ✅ Exemplo 3: Área de Solda com EPIs Específicos

**Contexto:** Soldador entrando em área de solda com máscara e capacete.

```bash
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "face_event": {
      "detected": true,
      "confidence": 0.89,
      "quality_score": 0.82
    },
    "epi_events": [
      {
        "epi_type": "helmet",
        "detected": true,
        "confidence": 0.94,
        "properly_worn": true
      },
      {
        "epi_type": "mask",
        "detected": true,
        "confidence": 0.88,
        "properly_worn": true
      },
      {
        "epi_type": "gloves",
        "detected": true,
        "confidence": 0.90,
        "properly_worn": true
      }
    ],
    "person_id": "SOLD-015",
    "location": "Área de Solda",
    "required_epis": ["helmet", "mask", "gloves"]
  }'
```

---

## Cenários de Rejeição

### ❌ Exemplo 1: EPI Não Detectado

**Contexto:** Trabalhador sem capacete tentando acessar canteiro de obras.

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
        "detected": false,
        "confidence": 0.30,
        "properly_worn": false
      }
    ],
    "person_id": "TRAB-099",
    "location": "Entrada Principal",
    "required_epis": ["helmet"]
  }'
```

**Resposta Esperada:**
```json
{
  "decision": "rejected",
  "reason": "Acesso negado. EPIs não detectados: helmet",
  "confidence_score": 0.0
}
```

---

### ❌ Exemplo 2: EPI Mal Usado

**Contexto:** Capacete detectado mas não usado corretamente.

```bash
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "face_event": {
      "detected": true,
      "confidence": 0.93,
      "quality_score": 0.87
    },
    "epi_events": [
      {
        "epi_type": "helmet",
        "detected": true,
        "confidence": 0.88,
        "properly_worn": false
      }
    ],
    "person_id": "TRAB-123",
    "location": "Canteiro - Setor C",
    "required_epis": ["helmet"]
  }'
```

**Resposta Esperada:**
```json
{
  "decision": "rejected",
  "reason": "Acesso negado. EPIs mal utilizados: helmet",
  "confidence_score": 0.0
}
```

---

### ❌ Exemplo 3: Qualidade Facial Insuficiente

**Contexto:** Face obscurecida ou imagem de baixa qualidade.

```bash
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "face_event": {
      "detected": true,
      "confidence": 0.45,
      "quality_score": 0.35
    },
    "epi_events": [
      {
        "epi_type": "helmet",
        "detected": true,
        "confidence": 0.95,
        "properly_worn": true
      }
    ],
    "person_id": "UNKN-000",
    "location": "Entrada Lateral",
    "required_epis": ["helmet"]
  }'
```

**Resposta Esperada:**
```json
{
  "decision": "rejected",
  "reason": "Acesso negado. Confiança da detecção facial muito baixa: 0.45",
  "confidence_score": 0.0
}
```

---

### ❌ Exemplo 4: Face Não Detectada

**Contexto:** Câmera não conseguiu detectar rosto.

```bash
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "face_event": {
      "detected": false,
      "confidence": 0.10,
      "quality_score": 0.15
    },
    "epi_events": [
      {
        "epi_type": "helmet",
        "detected": true,
        "confidence": 0.92,
        "properly_worn": true
      }
    ],
    "person_id": null,
    "location": "Portão de Emergência",
    "required_epis": ["helmet"]
  }'
```

**Resposta Esperada:**
```json
{
  "decision": "rejected",
  "reason": "Acesso negado. Face não detectada",
  "confidence_score": 0.0
}
```

---

### ❌ Exemplo 5: Múltiplos EPIs Faltando

**Contexto:** Área industrial exige vários EPIs mas trabalhador não está em conformidade.

```bash
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "face_event": {
      "detected": true,
      "confidence": 0.91,
      "quality_score": 0.85
    },
    "epi_events": [
      {
        "epi_type": "helmet",
        "detected": true,
        "confidence": 0.89,
        "properly_worn": true
      },
      {
        "epi_type": "safety_glasses",
        "detected": false,
        "confidence": 0.25,
        "properly_worn": false
      },
      {
        "epi_type": "gloves",
        "detected": false,
        "confidence": 0.20,
        "properly_worn": false
      }
    ],
    "person_id": "TRAB-456",
    "location": "Área Industrial",
    "required_epis": ["helmet", "safety_glasses", "gloves"]
  }'
```

**Resposta Esperada:**
```json
{
  "decision": "rejected",
  "reason": "Acesso negado. EPIs não detectados: safety_glasses, gloves",
  "confidence_score": 0.0
}
```

---

## Casos de Uso por Setor

### 🏗️ Construção Civil

#### Entrada em Canteiro de Obras
```bash
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "face_event": {
      "detected": true,
      "confidence": 0.96,
      "quality_score": 0.92
    },
    "epi_events": [
      {
        "epi_type": "helmet",
        "detected": true,
        "confidence": 0.95,
        "properly_worn": true
      },
      {
        "epi_type": "safety_shoes",
        "detected": true,
        "confidence": 0.91,
        "properly_worn": true
      },
      {
        "epi_type": "vest",
        "detected": true,
        "confidence": 0.93,
        "properly_worn": true
      }
    ],
    "person_id": "CONST-789",
    "location": "Obra Residencial - Fase 2",
    "required_epis": ["helmet", "safety_shoes", "vest"]
  }'
```

---

### 🏭 Indústria Química

#### Acesso a Laboratório
```bash
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "face_event": {
      "detected": true,
      "confidence": 0.94,
      "quality_score": 0.89
    },
    "epi_events": [
      {
        "epi_type": "safety_glasses",
        "detected": true,
        "confidence": 0.96,
        "properly_worn": true
      },
      {
        "epi_type": "gloves",
        "detected": true,
        "confidence": 0.92,
        "properly_worn": true
      },
      {
        "epi_type": "mask",
        "detected": true,
        "confidence": 0.88,
        "properly_worn": true
      }
    ],
    "person_id": "QUIM-321",
    "location": "Laboratório de Análises",
    "required_epis": ["safety_glasses", "gloves", "mask"]
  }'
```

---

### ⚡ Elétrica

#### Manutenção em Subestação
```bash
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "face_event": {
      "detected": true,
      "confidence": 0.97,
      "quality_score": 0.94
    },
    "epi_events": [
      {
        "epi_type": "helmet",
        "detected": true,
        "confidence": 0.98,
        "properly_worn": true
      },
      {
        "epi_type": "safety_glasses",
        "detected": true,
        "confidence": 0.95,
        "properly_worn": true
      },
      {
        "epi_type": "gloves",
        "detected": true,
        "confidence": 0.93,
        "properly_worn": true
      },
      {
        "epi_type": "safety_shoes",
        "detected": true,
        "confidence": 0.91,
        "properly_worn": true
      }
    ],
    "person_id": "ELET-555",
    "location": "Subestação Alpha",
    "required_epis": ["helmet", "safety_glasses", "gloves", "safety_shoes"]
  }'
```

---

### 🏥 Saúde (COVID-19)

#### Entrada em UTI
```bash
curl -X POST http://localhost:8001/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "face_event": {
      "detected": true,
      "confidence": 0.85,
      "quality_score": 0.78
    },
    "epi_events": [
      {
        "epi_type": "mask",
        "detected": true,
        "confidence": 0.94,
        "properly_worn": true
      },
      {
        "epi_type": "gloves",
        "detected": true,
        "confidence": 0.89,
        "properly_worn": true
      }
    ],
    "person_id": "MED-888",
    "location": "UTI - Bloco Norte",
    "required_epis": ["mask", "gloves"]
  }'
```

---

## Exemplos de Integração

### 🔗 Integração com Sistema de Câmeras

**Python Script de Integração:**

```python
import requests
import cv2
import json

# Configuração
API_URL = "http://localhost:8001/api/orchestrate"
CAMERA_ID = "CAM-001"
LOCATION = "Entrada Principal"

def process_camera_frame(frame):
    """Processa frame da câmera e envia para orquestrador"""
    
    # Simular detecção facial (integrar com seu modelo)
    face_detected = detect_face(frame)
    face_confidence = calculate_face_confidence(frame)
    face_quality = calculate_face_quality(frame)
    
    # Simular detecção de EPI (integrar com seu modelo)
    epis_detected = detect_epis(frame)
    
    # Montar payload
    payload = {
        "face_event": {
            "detected": face_detected,
            "confidence": face_confidence,
            "quality_score": face_quality
        },
        "epi_events": epis_detected,
        "location": LOCATION,
        "required_epis": ["helmet"]
    }
    
    # Enviar para orquestrador
    response = requests.post(API_URL, json=payload)
    decision = response.json()
    
    # Tomar ação baseada na decisão
    if decision["decision"] == "approved":
        open_gate()
        print(f"✅ Acesso aprovado: {decision['reason']}")
    else:
        trigger_alarm()
        print(f"❌ Acesso negado: {decision['reason']}")
    
    return decision

# Exemplo de uso
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if ret:
        decision = process_camera_frame(frame)
        # Exibir resultado no frame
        cv2.imshow('EPI Orchestrator', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

### 📊 Dashboard Customizado

**JavaScript/React Integration:**

```javascript
import axios from 'axios';
import { useEffect, useState } from 'react';

const API_URL = 'http://localhost:8001/api';

function CustomDashboard() {
  const [stats, setStats] = useState(null);
  const [recentDecisions, setRecentDecisions] = useState([]);

  useEffect(() => {
    // Buscar dados a cada 3 segundos
    const interval = setInterval(async () => {
      // Estatísticas
      const statsRes = await axios.get(`${API_URL}/stats`);
      setStats(statsRes.data);
      
      // Decisões recentes
      const decisionsRes = await axios.get(`${API_URL}/decisions?limit=5`);
      setRecentDecisions(decisionsRes.data);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const processEvent = async (eventData) => {
    try {
      const response = await axios.post(`${API_URL}/orchestrate`, eventData);
      alert(`Decisão: ${response.data.decision}\n${response.data.reason}`);
    } catch (error) {
      alert('Erro ao processar evento');
    }
  };

  return (
    <div>
      <h1>Dashboard Personalizado</h1>
      
      {stats && (
        <div>
          <h2>Estatísticas</h2>
          <p>Total de Decisões: {stats.total_decisions}</p>
          <p>Aprovações: {stats.approved_decisions}</p>
          <p>Rejeições: {stats.rejected_decisions}</p>
        </div>
      )}
      
      <div>
        <h2>Decisões Recentes</h2>
        {recentDecisions.map(decision => (
          <div key={decision.id}>
            <span>{decision.decision}</span>
            <span>{decision.location}</span>
            <span>{new Date(decision.timestamp).toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CustomDashboard;
```

---

### 🔔 Sistema de Notificações

**WebHook Integration (Node.js):**

```javascript
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

// Endpoint para receber decisões
app.post('/webhook/decision', async (req, res) => {
  const decision = req.body;
  
  if (decision.decision === 'rejected') {
    // Enviar alerta para segurança
    await sendSecurityAlert(decision);
    
    // Enviar email para supervisor
    await sendEmailAlert(decision);
    
    // Log no sistema
    console.log(`⚠️ ALERTA: Acesso negado para ${decision.person_id}`);
    console.log(`Motivo: ${decision.reason}`);
  }
  
  res.json({ received: true });
});

async function sendSecurityAlert(decision) {
  // Integração com sistema de segurança
  await axios.post('http://security-system/alert', {
    type: 'access_denied',
    person_id: decision.person_id,
    location: decision.location,
    reason: decision.reason,
    timestamp: decision.timestamp
  });
}

async function sendEmailAlert(decision) {
  // Integração com serviço de email
  // Implementar envio de email
}

app.listen(3001, () => {
  console.log('Webhook server listening on port 3001');
});
```

---

## 📝 Notas de Implementação

### Limiares Recomendados

| Ambiente | Face Confidence | Face Quality | EPI Confidence |
|----------|----------------|--------------|----------------|
| Alta Segurança | 0.85 | 0.80 | 0.85 |
| Média Segurança | 0.70 | 0.60 | 0.70 |
| Baixa Segurança | 0.60 | 0.50 | 0.60 |

### Tratamento de Casos Especiais

1. **Visitantes**: Criar categoria especial sem EPIs obrigatórios
2. **Emergências**: Endpoint para bypass temporário
3. **Manutenção**: Sistema de liberação temporária
4. **Treinamento**: Modo de teste sem acionar alarmes

### Boas Práticas

1. ✅ Sempre incluir `location` para auditoria
2. ✅ Usar `person_id` quando disponível
3. ✅ Ajustar `required_epis` por local
4. ✅ Monitorar confiança média ao longo do tempo
5. ✅ Revisar decisões rejeitadas periodicamente

---

**Última atualização:** Dezembro 2025  
**Versão dos Exemplos:** 1.0.0
