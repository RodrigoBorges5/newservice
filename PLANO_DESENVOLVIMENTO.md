# Plano de Desenvolvimento - Backend Plataforma Estudantes/Empresas

## 📋 Informações do Projeto

**Stack Tecnológica:**

- Django (Framework Backend)
- Django REST Framework (API)
- Supabase (PostgreSQL, Storage, Auth)

**Equipa:** 4 Desenvolvedores

**Metodologia:** Sprints de 2 semanas com reuniões de sync

**Duração Total:** 8 semanas (4 sprints)

---

## 📋 Requisitos Funcionais

- **FR-1 (Empresas)**: Submissão de vagas (área, competências, descrição)
- **FR-2 (Estudantes)**: Submissão de CV (PDF/Link) com consentimento de dados
- **FR-3 (Filtros)**: Pesquisa de vagas por estudantes e pesquisa de CVs por empresas
- **FR-4 (CR/Admin)**: Fluxo de validação de CVs pela equipa de "Career Services"
- **FR-5 (Segurança)**: Visualização de documentos via Storage com URLs assinadas (sem download direto)

---

## 🔐 Estratégia de Autenticação (Fase Inicial)

- Utilizadores já existem no Supabase com UUIDs e Roles
- Sem login/registo no Django nesta fase
- Testes via Postman com header `X-User-ID`
- Django valida user e role no Supabase antes de permitir acesso

---

## 📊 Estrutura de Tasks Detalhada

### **FASE 0: Configuração Base (Pré-Sprint 1)**

#### Tasks Iniciais (Críticas - Bloqueadoras)

- **T0.1** - ✅ **COMPLETO** - Configurar projeto Django + DRF + Supabase Client
  - ✅ Django REST Framework instalado e configurado
  - ✅ Supabase Client (supabase-py) instalado
  - ✅ Helper `supabase_client.py` criado
  - ✅ Apps `rest_framework` e `service` adicionados ao INSTALLED_APPS
- **T0.2** - ✅ **COMPLETO** - Configurar variáveis de ambiente (Supabase URL, Keys)
  - ✅ Variáveis `SUPABASE_URL` e `SUPABASE_KEY` configuradas no .env
  - ✅ Variáveis carregadas no settings.py via python-dotenv
  - ⚠️ **AÇÃO NECESSÁRIA**: Substitua `your_supabase_anon_key_here` pela chave real do Supabase
- **T0.3** - Criar modelos base (User Proxy/Profile se necessário)
- **T0.4** - ✅ **COMPLETO** - Configurar CORS e Settings de Segurança
  - ✅ django-cors-headers instalado e configurado
  - ✅ CORS Middleware adicionado
  - ✅ ALLOWED_HOSTS configurado (127.0.0.1, localhost)
  - ✅ CORS_ALLOWED_ORIGINS configurado para frontend local

---

## 🎯 **SPRINT 1** (Semanas 1-2): Autenticação Mock + Modelos Core

### **Dev 1: Middleware de Autenticação Mock**

| Task           | Descrição                                                                             | Dependências |
| -------------- | --------------------------------------------------------------------------------------- | ------------- |
| **T1.1** | Criar Middleware para intercetar `X-User-ID` header                                   | T0.1, T0.2    |
| **T1.2** | Implementar lógica de consulta ao Supabase (verificar user + role)                     | T1.1          |
| **T1.3** | Adicionar cache de roles (Redis/Memory) para otimização                               | T1.2          |
| **T1.4** | Criar decoradores/permissions customizados DRF (`IsStudent`, `IsCompany`, `IsCR`) | T1.2          |
| **T1.5** | Escrever testes unitários do middleware                                                | T1.4          |
| **T1.6** | Documentar usage do header para Postman                                                 | T1.4          |

**Entregável**: Middleware funcional + Postman Collection com exemplos

---

### **Dev 2: Modelo de Vagas (FR-1)**

| Task            | Descrição                                                                         | Dependências |
| --------------- | ----------------------------------------------------------------------------------- | ------------- |
| **T1.7**  | Criar modelo `JobPosting` (área, competências, descrição, empresa_id, status) | T0.3          |
| **T1.8**  | Criar migrations                                                                    | T1.7          |
| **T1.9**  | Criar Serializer para `JobPosting` (validações de campos obrigatórios)         | T1.7          |
| **T1.10** | Implementar ViewSet básico (CRUD) com permissão `IsCompany`                     | T1.4, T1.9    |
| **T1.11** | Adicionar filtro de "vagas criadas por mim" (empresa_id = X-User-ID)                | T1.10         |
| **T1.12** | Testes de integração (POST, GET, PUT, DELETE)                                     | T1.11         |

**Entregável**: API de Vagas funcional para Empresas

---

### **Dev 3: Modelo de CVs (FR-2 Parte 1)**

| Task            | Descrição                                                             | Dependências |
| --------------- | ----------------------------------------------------------------------- | ------------- |
| **T1.13** | Criar modelo `StudentCV` (estudante_id, cv_url, consent_date, status) | T0.3          |
| **T1.14** | Criar migrations                                                        | T1.13         |
| **T1.15** | Criar Serializer para `StudentCV` (validação de consentimento)      | T1.13         |
| **T1.16** | Implementar ViewSet básico (GET, POST) com permissão `IsStudent`    | T1.4, T1.15   |
| **T1.17** | Adicionar validação: estudante só pode ter 1 CV ativo                | T1.16         |
| **T1.18** | Testes de integração                                                  | T1.17         |

**Entregável**: API de CV (sem upload ainda, apenas URL mock)

---

### **Dev 4: Setup de Testes + CI/CD Base**

| Task            | Descrição                                          | Dependências |
| --------------- | ---------------------------------------------------- | ------------- |
| **T1.19** | Configurar pytest + pytest-django                    | Nenhuma       |
| **T1.20** | Criar fixtures reutilizáveis (mock users com roles) | T1.19         |
| **T1.21** | Configurar GitHub Actions para rodar testes          | T1.19         |
| **T1.22** | Documentar estrutura de testes no README             | T1.21         |
| **T1.23** | Criar script de seed de dados de teste no Supabase   | T0.2          |

**Entregável**: Pipeline CI + Fixtures

---

### ✅ **Demo Sprint 1**

- ✓ Middleware de auth a funcionar
- ✓ Empresa consegue criar/editar/listar vagas (Postman)
- ✓ Estudante consegue submeter CV (URL mock)
- ✓ Testes automatizados a correr no CI

---

## 🎯 **SPRINT 2** (Semanas 3-4): Upload Storage + Filtros Básicos

### **Dev 1: Integração Supabase Storage (FR-2 Parte 2)**

| Task           | Descrição                                                                     | Dependências     |
| -------------- | ------------------------------------------------------------------------------- | ----------------- |
| **T2.1** | Criar service layer `SupabaseStorageService` (upload, delete, get_signed_url) | T0.2              |
| **T2.2** | Implementar endpoint `POST /api/students/cv/upload/` (aceita PDF)             | T2.1, T1.13-T1.18 |
| **T2.3** | Validar tipo de ficheiro e tamanho (max 5MB)                                    | T2.2              |
| **T2.4** | Atualizar modelo `StudentCV` com campo `storage_path`                       | T1.13             |
| **T2.5** | Implementar lógica: upload → guardar path → gerar signed URL                 | T2.2, T2.4        |
| **T2.6** | Testes de upload (mock do Supabase)                                             | T2.5              |

**Entregável**: Upload de CV funcional

---

### **Dev 2: Visualização Segura de Documentos (FR-5)**

| Task            | Descrição                                                                       | Dependências |
| --------------- | --------------------------------------------------------------------------------- | ------------- |
| **T2.7**  | Criar endpoint `GET /api/students/cv/{id}/view/` (retorna signed URL)           | T2.1          |
| **T2.8**  | Validar permissões: Empresa vê CVs aprovados, CR vê todos, Estudante vê o seu | T1.4, T2.7    |
| **T2.9**  | Implementar expiração de URLs (15 min)                                          | T2.7          |
| **T2.10** | Adicionar logging de acessos (quem viu que CV quando)                             | T2.8          |
| **T2.11** | Testes de permissões (matriz de acessos)                                         | T2.10         |

**Entregável**: Sistema de visualização seguro

---

### **Dev 3: Filtros de Vagas (FR-3 Parte 1)**

| Task            | Descrição                                                      | Dependências |
| --------------- | ---------------------------------------------------------------- | ------------- |
| **T2.12** | Adicionar django-filter ao projeto                               | Nenhuma       |
| **T2.13** | Criar FilterSet para `JobPosting` (área, competências, data) | T1.7, T2.12   |
| **T2.14** | Implementar endpoint `GET /api/jobs/?area=IT&skills=Python`    | T2.13         |
| **T2.15** | Adicionar paginação (PageNumberPagination)                     | T2.14         |
| **T2.16** | Criar testes de filtros combinados                               | T2.15         |
| **T2.17** | Documentar query params no Postman                               | T2.16         |

**Entregável**: Pesquisa de vagas funcional

---

### **Dev 4: Filtros de CVs (FR-3 Parte 2)**

| Task            | Descrição                                                       | Dependências |
| --------------- | ----------------------------------------------------------------- | ------------- |
| **T2.18** | Criar modelo `StudentProfile` (competências, área, ano)       | T0.3          |
| **T2.19** | Criar migrations                                                  | T2.18         |
| **T2.20** | Criar FilterSet para `StudentProfile`                           | T2.18, T2.12  |
| **T2.21** | Implementar endpoint `GET /api/students/?skills=Django&area=CS` | T2.20         |
| **T2.22** | Validar permissão: só Empresas e CR podem filtrar CVs           | T1.4, T2.21   |
| **T2.23** | Testes de filtros + permissões                                   | T2.22         |

**Entregável**: Pesquisa de CVs funcional

---

### ✅ **Demo Sprint 2**

- ✓ Estudante faz upload de CV (PDF) → documento vai para Storage
- ✓ Empresa consegue pesquisar vagas por área/skills
- ✓ Empresa consegue pesquisar CVs aprovados
- ✓ CR consegue ver documento de CV com signed URL

---

## 🎯 **SPRINT 3** (Semanas 5-6): Fluxo de Validação CR + Notificações

### **Dev 1: Estados de CV e Fluxo CR (FR-4 Parte 1)**

| Task           | Descrição                                                                      | Dependências |
| -------------- | -------------------------------------------------------------------------------- | ------------- |
| **T3.1** | Adicionar campo `status` ao modelo `StudentCV` (pending, approved, rejected) | T1.13         |
| **T3.2** | Criar migration + data migration (CVs existentes → pending)                     | T3.1          |
| **T3.3** | Criar modelo `CVReview` (cv_id, reviewer_id, status, feedback, date)           | T0.3          |
| **T3.4** | Criar Serializer para `CVReview`                                               | T3.3          |
| **T3.5** | Implementar endpoint `POST /api/cr/cvs/{id}/review/` (aprovar/rejeitar)        | T3.4, T1.4    |
| **T3.6** | Validar: só CR pode fazer review                                                | T3.5          |
| **T3.7** | Atualizar status do CV automaticamente após review                              | T3.5          |

**Entregável**: Fluxo de aprovação funcional

---

### **Dev 2: Dashboard CR (FR-4 Parte 2)**

| Task            | Descrição                                                              | Dependências |
| --------------- | ------------------------------------------------------------------------ | ------------- |
| **T3.8**  | Criar endpoint `GET /api/cr/cvs/pending/` (listar CVs pendentes)       | T3.1, T1.4    |
| **T3.9**  | Adicionar estatísticas (total pending, approved, rejected)              | T3.8          |
| **T3.10** | Implementar filtros (data de submissão, estudante)                      | T3.8          |
| **T3.11** | Criar endpoint `GET /api/cr/cvs/{id}/history/` (histórico de reviews) | T3.3, T3.8    |
| **T3.12** | Testes de endpoints CR                                                   | T3.11         |

**Entregável**: Dashboard CR funcional

---

### **Dev 3: Sistema de Notificações (Email/Webhook)**

| Task            | Descrição                                                     | Dependências |
| --------------- | --------------------------------------------------------------- | ------------- |
| **T3.13** | Configurar Celery + Redis para tasks assíncronas               | Nenhuma       |
| **T3.14** | Criar task `send_cv_status_notification` (email ao estudante) | T3.13         |
| **T3.15** | Integrar com Supabase Auth para obter emails                    | T0.2, T3.14   |
| **T3.16** | Criar template de email (aprovado/rejeitado)                    | T3.14         |
| **T3.17** | Trigger notificação após review de CV                        | T3.5, T3.14   |
| **T3.18** | Criar endpoint `GET /api/notifications/` (histórico)         | T3.17         |

**Entregável**: Notificações automáticas

---

### **Dev 4: Auditoria e Logs (Compliance)**

| Task            | Descrição                                                      | Dependências |
| --------------- | ---------------------------------------------------------------- | ------------- |
| **T3.19** | Criar modelo `AuditLog` (user_id, action, resource, timestamp) | T0.3          |
| **T3.20** | Criar middleware de auditoria (log de todas as ações)          | T3.19         |
| **T3.21** | Implementar endpoint `GET /api/admin/audit/` (só CR)          | T3.20, T1.4   |
| **T3.22** | Adicionar retenção de logs (GDPR compliance)                   | T3.21         |
| **T3.23** | Criar relatório de acessos a CVs                                | T2.10, T3.19  |
| **T3.24** | Testes de auditoria                                              | T3.23         |

**Entregável**: Sistema de auditoria completo

---

### ✅ **Demo Sprint 3**

- ✓ Estudante submete CV → fica pendente
- ✓ CR aprova/rejeita CV → estudante recebe email
- ✓ CR vê dashboard com CVs pendentes
- ✓ Sistema de logs a registar todas as ações

---

## 🎯 **SPRINT 4** (Semanas 7-8): Refinamentos + Produção

### **Dev 1: Performance e Otimização**

| Task           | Descrição                                             | Dependências                |
| -------------- | ------------------------------------------------------- | ---------------------------- |
| **T4.1** | Adicionar índices na BD (área, competências, status) | Todas as features anteriores |
| **T4.2** | Implementar caching de queries frequentes (Redis)       | T4.1                         |
| **T4.3** | Otimizar serializers (select_related, prefetch_related) | T4.1                         |
| **T4.4** | Configurar rate limiting (throttling DRF)               | Nenhuma                      |
| **T4.5** | Testes de carga (Locust/JMeter)                         | T4.3                         |

**Entregável**: API otimizada para produção

---

### **Dev 2: Documentação API (OpenAPI/Swagger)**

| Task            | Descrição                                 | Dependências |
| --------------- | ------------------------------------------- | ------------- |
| **T4.6**  | Configurar drf-spectacular                  | Nenhuma       |
| **T4.7**  | Adicionar docstrings a todos os endpoints   | T4.6          |
| **T4.8**  | Gerar documentação automática            | T4.7          |
| **T4.9**  | Criar guia de quick start para novos devs   | T4.8          |
| **T4.10** | Documentar fluxos completos (user journeys) | T4.9          |

**Entregável**: Documentação completa

---

### **Dev 3: Validações Avançadas + Edge Cases**

| Task            | Descrição                                                        | Dependências |
| --------------- | ------------------------------------------------------------------ | ------------- |
| **T4.11** | Implementar validação de duplicados de vagas (empresa + título) | T1.7          |
| **T4.12** | Adicionar soft delete em vez de hard delete                        | Nenhuma       |
| **T4.13** | Criar endpoint de "arquivar vaga" (fecha mas não apaga)           | T4.12         |
| **T4.14** | Validar datas (vagas não podem expirar no passado)                | T1.7          |
| **T4.15** | Testes de edge cases (payloads inválidos, etc)                    | T4.14         |

**Entregável**: API robusta contra erros

---

### **Dev 4: Deploy e Monitorização**

| Task            | Descrição                                          | Dependências |
| --------------- | ---------------------------------------------------- | ------------- |
| **T4.16** | Configurar Docker + docker-compose (já existe)      | Nenhuma       |
| **T4.17** | Criar script de deploy (Railway/Render/DigitalOcean) | T4.16         |
| **T4.18** | Configurar Sentry para error tracking                | T4.17         |
| **T4.19** | Configurar healthcheck endpoint `GET /api/health/` | Nenhuma       |
| **T4.20** | Setup de logs estruturados (JSON logging)            | T4.18         |
| **T4.21** | Criar guia de troubleshooting                        | T4.20         |

**Entregável**: Ambiente de produção

---

### ✅ **Demo Sprint 4 (Final)**

- ✓ API completa e documentada
- ✓ Performance testada (>100 req/s)
- ✓ Deploy em produção funcional
- ✓ Monitorização ativa (Sentry + Logs)

---

## 📊 Caminho Crítico (Bloqueadores)

```
T0.1 → T0.2 (Setup Supabase)
  ↓
T1.1 → T1.4 (Middleware Auth) ← ⚠️ CRÍTICO
  ↓
T1.7-T1.12 (Vagas) || T1.13-T1.18 (CVs) ← Paralelo
  ↓
T2.1-T2.6 (Upload) ← ⚠️ CRÍTICO
  ↓
T2.7-T2.11 (Signed URLs) ← ⚠️ CRÍTICO
  ↓
T3.1-T3.7 (Fluxo CR) ← ⚠️ CRÍTICO
  ↓
T4.1-T4.5 (Otimização) → Deploy
```

### Tasks Bloqueadoras (Prioridade Máxima)

1. **T1.1-T1.4**: Middleware de Autenticação (bloqueia TUDO)
2. **T2.1**: Supabase Storage Service (bloqueia upload e visualização)
3. **T3.5**: Endpoint de Review (bloqueia workflow CR)

---

## 👥 Distribuição por Desenvolvedor

### **Sprint 1**

| Dev 1 (Backend Core)     | Dev 2 (Features)         | Dev 3 (Integração)     | Dev 4 (Infra)             |
| ------------------------ | ------------------------ | ------------------------ | ------------------------- |
| T1.1 - Criar Middleware  | T1.7 - Modelo JobPosting | T1.13 - Modelo StudentCV | T1.19 - Configurar pytest |
| T1.2 - Lógica Supabase  | T1.8 - Migrations Vagas  | T1.14 - Migrations CVs   | T1.20 - Criar fixtures    |
| T1.3 - Cache de roles    | T1.9 - Serializer Vagas  | T1.15 - Serializer CVs   | T1.21 - GitHub Actions    |
| T1.4 - Permissions DRF   | T1.10 - ViewSet Vagas    | T1.16 - ViewSet CVs      | T1.22 - Doc Testes        |
| T1.5 - Testes Middleware | T1.11 - Filtros base     | T1.17 - Validação 1 CV | T1.23 - Seed dados        |
| T1.6 - Doc Postman       | T1.12 - Testes Vagas     | T1.18 - Testes CVs       | -                         |

### **Sprint 2**

| Dev 1 (Backend Core)        | Dev 2 (Features)           | Dev 3 (Integração)     | Dev 4 (Infra)                |
| --------------------------- | -------------------------- | ------------------------ | ---------------------------- |
| T2.1 - Storage Service      | T2.7 - Endpoint Signed URL | T2.12 - Django Filter    | T2.18 - StudentProfile       |
| T2.2 - Endpoint Upload      | T2.8 - Permissões View    | T2.13 - FilterSet Vagas  | T2.19 - Migrations Profile   |
| T2.3 - Validação Ficheiro | T2.9 - Expiração URLs    | T2.14 - Endpoint Filtros | T2.20 - FilterSet Profile    |
| T2.4 - Campo storage_path   | T2.10 - Log Acessos        | T2.15 - Paginação      | T2.21 - Endpoint Filtros CVs |
| T2.5 - Lógica Upload       | T2.11 - Testes Permissões | T2.16 - Testes Filtros   | T2.22 - Validar Permissões  |
| T2.6 - Testes Upload        | -                          | T2.17 - Doc Postman      | T2.23 - Testes Filtros       |

### **Sprint 3**

| Dev 1 (Backend Core)     | Dev 2 (Features)           | Dev 3 (Integração)       | Dev 4 (Infra)              |
| ------------------------ | -------------------------- | -------------------------- | -------------------------- |
| T3.1 - Campo status CV   | T3.8 - Endpoint Pending    | T3.13 - Celery + Redis     | T3.19 - Modelo AuditLog    |
| T3.2 - Migrations status | T3.9 - Estatísticas CR    | T3.14 - Task Notificação | T3.20 - Middleware Audit   |
| T3.3 - Modelo CVReview   | T3.10 - Filtros Dashboard  | T3.15 - Integrar Supabase  | T3.21 - Endpoint Audit     |
| T3.4 - Serializer Review | T3.11 - Histórico Reviews | T3.16 - Template Email     | T3.22 - Retenção Logs    |
| T3.5 - Endpoint Review   | T3.12 - Testes CR          | T3.17 - Trigger Email      | T3.23 - Relatório Acessos |
| T3.6 - Validar CR only   | -                          | T3.18 - Endpoint Notif     | T3.24 - Testes Audit       |
| T3.7 - Atualizar status  | -                          | -                          | -                          |

### **Sprint 4**

| Dev 1 (Backend Core)        | Dev 2 (Features)       | Dev 3 (Integração)      | Dev 4 (Infra)           |
| --------------------------- | ---------------------- | ------------------------- | ----------------------- |
| T4.1 - Índices BD          | T4.6 - drf-spectacular | T4.11 - Valid Duplicados  | T4.16 - Docker config   |
| T4.2 - Cache queries        | T4.7 - Docstrings      | T4.12 - Soft Delete       | T4.17 - Script Deploy   |
| T4.3 - Otimizar Serializers | T4.8 - Doc Automática | T4.13 - Arquivar Vaga     | T4.18 - Sentry          |
| T4.4 - Rate Limiting        | T4.9 - Quick Start     | T4.14 - Valid Datas       | T4.19 - Healthcheck     |
| T4.5 - Testes Carga         | T4.10 - User Journeys  | T4.15 - Testes Edge Cases | T4.20 - JSON Logging    |
| -                           | -                      | -                         | T4.21 - Troubleshooting |

---

## ⚠️ Riscos e Mitigações

### Risco 1: Supabase API Lento

**Impacto**: Alto**Probabilidade**: Média**Mitigação**:

- Implementar cache de roles (T1.3)
- Adicionar índices na BD (T4.1)
- Monitorizar tempos de resposta desde Sprint 1

### Risco 2: Upload de Ficheiros Grandes Bloqueia Request

**Impacto**: Médio**Probabilidade**: Alta**Mitigação**:

- Validação de tamanho máximo (T2.3)
- Considerar Celery para uploads assíncronos (refinamento futuro)
- Implementar progress tracking

### Risco 3: Dependências Entre Tasks Atrasam Sprints

**Impacto**: Alto**Probabilidade**: Média**Mitigação**:

- Tasks críticas são sempre prioridade máxima
- Dev 1 foca em bloqueadores primeiro
- Reuniões diárias para identificar bloqueios cedo

### Risco 4: Problemas de Permissões em Produção

**Impacto**: Crítico**Probabilidade**: Baixa**Mitigação**:

- Testes extensivos de matriz de permissões (T2.11)
- Sistema de auditoria (Sprint 3)
- Logs detalhados de acessos (T2.10)

---

## 📝 Cerimónias Scrum

### Daily Standup (15 min)

- O que fiz ontem?
- O que vou fazer hoje?
- Tenho bloqueios?

### Sprint Planning (2h - Início de cada Sprint)

- Review do plano
- Atribuição final de tasks
- Estimativas de esforço
- Definição de DoD (Definition of Done)

### Sprint Review/Demo (1h - Fim de cada Sprint)

- Demo ao vivo das features
- Feedback da equipa
- Validação com stakeholders (se aplicável)

### Sprint Retrospective (1h - Fim de cada Sprint)

- O que correu bem?
- O que correu mal?
- Ações de melhoria para próximo sprint

---

## 📋 Definition of Done (DoD)

Uma task só está completa quando:

- ✅ Código implementado e funcional
- ✅ Testes unitários/integração escritos e a passar
- ✅ Code review feito por outro dev
- ✅ Documentação atualizada (docstrings + README se aplicável)
- ✅ Testado no Postman (endpoints)
- ✅ Sem erros no CI/CD pipeline
- ✅ Merged na branch `develop`

---

## 🚀 Próximos Passos Imediatos

### Hoje (19 Dezembro 2025)

1. ✅ Confirmar estrutura de roles no Supabase (Student, Company, CR)
2. ✅ Dev 4 executa T0.1-T0.4 (setup base do projeto)
3. ✅ Criar repositório Git e branch `develop`
4. ✅ Configurar Postman Workspace partilhado

### Amanhã (20 Dezembro)

1. Sprint Planning Meeting
2. Dev 1 começa T1.1 (middleware crítico)
3. Devs 2-4 começam tasks paralelas (T1.7, T1.13, T1.19)
4. Distribuir tasks detalhadas no Jira/Trello/GitHub Projects

### Esta Semana

- Ter middleware de auth funcional (bloqueador)
- Ter modelos base criados
- Ter setup de testes a funcionar

---

## 📚 Recursos e Referências

### Documentação Técnica

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Supabase Python Client](https://supabase.com/docs/reference/python)
- [Django-filter](https://django-filter.readthedocs.io/)
- [Celery](https://docs.celeryproject.org/)

### Templates de Código

- Middleware de autenticação custom
- Permissions DRF personalizadas
- Service layer pattern para Storage
- Fixtures de teste

### Convenções de Código

- PEP 8 para Python
- Docstrings em formato Google
- Commits semânticos: `feat:`, `fix:`, `docs:`, `test:`
- Branch naming: `feature/T1.1-create-middleware`

---

## 📞 Contactos da Equipa

| Dev   | Responsabilidade Principal | Slack/Email |
| ----- | -------------------------- | ----------- |
| Dev 1 | Backend Core + Middleware  | @dev1       |
| Dev 2 | Features + Endpoints       | @dev2       |
| Dev 3 | Integrações Externas     | @dev3       |
| Dev 4 | Infra + DevOps             | @dev4       |

---

## 📊 Métricas de Sucesso

### Sprint 1

- [ ] 100% das tasks críticas completas (T1.1-T1.6)
- [ ] Cobertura de testes > 80%
- [ ] 0 bugs críticos

### Sprint 2

- [ ] Upload de CV funcional em produção
- [ ] Performance de signed URLs < 200ms
- [ ] Filtros com paginação a funcionar

### Sprint 3

- [ ] Workflow CR completo end-to-end
- [ ] Emails enviados com sucesso
- [ ] Sistema de logs a capturar 100% das ações

### Sprint 4

- [ ] API em produção com 99% uptime
- [ ] Documentação completa no Swagger
- [ ] Performance > 100 req/s

---

**Última Atualização**: 19 Dezembro 2025
**Versão**: 1.0
**Status**: Planeamento Aprovado ✅
