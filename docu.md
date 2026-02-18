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

## 📋 Requisitos Funcionais e User Stories

### **Mapeamento de User Stories para Requisitos**

- **FR-1 (Empresas)**: Submissão de vagas → **US-1** ✅
- **FR-2 (Estudantes)**: Submissão de CV → **US-2** ✅
- **FR-3 (Filtros)**: Pesquisa de vagas e CVs → **US-3.1/3.2, US-4.1/4.2** ✅
- **FR-4 (CR/Admin)**: Validação de CVs → **US-5.1/5.2** ✅
- **FR-5 (Autenticação)**: Perfis e redirecionamento → **US-6** ✅
- **FR-6 (Segurança)**: Visualização sem download direto → **US-6.2** ✅
- **FR-7 (Administração)**: Gestão de empresas → **US-6.4** ✅

---

### **User Stories Detalhadas**

#### **US-1: Submissão de Vagas (Empresas)**

**Relacionada com**: FR-1
**Dev Responsável**: Dev 2
**Sprint**: 1

📝 **História**: Como Empresa, quero submeter vagas detalhadas (estágio, emprego ou projeto), para que possa divulgar oportunidades aos estudantes adequados.

**Critérios de Aceitação:**

- **C1**: Empresa autenticada preenche "Área de Atuação", "Conhecimentos Necessários", seleciona tipo (estágio/emprego/projeto) → Vaga registada com sucesso
- **C2**: Tentativa de submissão sem campos obrigatórios → Sistema impede e mostra erro

**Tasks Associadas**: T1.7, T1.8, T1.9, T1.10, T1.11, T1.12

---

#### **US-2: Submissão de Currículo (Estudantes)**

**Relacionada com**: FR-2
**Dev Responsável**: Dev 3
**Sprint**: 1-2

📝 **História**: Enquanto estudante, quero preencher os dados do meu perfil de forma simples e submeter o meu currículo para que este seja revisto pela equipa de CR e, de seguida, visualizado pelas empresas.

**2.1 - Submissão de CV:**

- **C1**: Ficheiro enviado → Sistema valida se é PDF
- **C2**: Tentativa de submissão sem campos obrigatórios (nome, área, grau, ano) → Sistema impede e alerta
- **C3**: Após finalização → CV marca como "Pendente de Validação"

**2.2 - Consentimento de Dados:**

📝 **História**: Como estudante, devo indicar a minha autorização expressa para a partilha dos dados, estando abrangido pela proteção dos meus dados.

**Critérios de Aceitação:**

- **C1**: Dado que estou a finalizar a minha submissão; Quando não consentir a partilha de dados; Então não deve ser efetuada a submissão.

**Tasks Associadas**: T1.14, T1.15, T1.16, T1.17

---

#### **US-3.1: Visualização de Vagas (Estudantes/CR)**

**Relacionada com**: FR-3
**Dev Responsável**: Dev 4
**Sprint**: 1-2

📝 **História**: Como estudante ou CR, quero visualizar as vagas disponíveis, com intuito procurar uma oportunidade de acordo com meu interesse.

**Critérios de Aceitação:**

- **C1**: Login com sucesso → Acesso página de vagas → Todas as vagas aparecem sem filtros

**Tasks Associadas**: T1.20

---

#### **US-3.2: Filtragem de Vagas (Estudantes/CR)**

**Relacionada com**: FR-3
**Dev Responsável**: Dev 4
**Sprint**: 2

📝 **História**: Como estudante ou CR, quero selecionar especificamente vagas de certo tipo (estágio, emprego, projeto) e área de interesse, com intuito de somente visualizar tal tipo de vagas.

**Critérios de Aceitação:**

- **C1**: Seleciona filtros → Submete → Vagas correspondentes aparecem
- **C2**: Filtros sem resultados → Mensagem "Não há vagas"

**Tasks Associadas**: T1.21

---

#### **US-4.1: Visualização de Currículos (Empresa/CR)**

**Relacionada com**: FR-3, FR-5
**Dev Responsável**: Dev 4
**Sprint**: 2-3

📝 **História**: Como Empresa ou CR, quero consultar os currículos dos estudantes, para que encontre candidatos para as vagas que necessito.

**Critérios de Aceitação:**

- **C1**: Ator autenticado → Seleciona página de pesquisa de talentos → Lista de todos os candidatos aparece
- **C2**: Tenta descarregar PDF → Sistema bloqueia download (visualização only), conforme proteção de propriedade

**Tasks Associadas**: T2.1, T2.2

---

#### **US-4.2: Filtro de Currículos (Empresa/CR)**

**Relacionada com**: FR-3
**Dev Responsável**: Dev 4
**Sprint**: 3

📝 **História**: Como Empresa ou CR, quero filtrar os currículos dos estudantes, para que encontre candidatos com as competências específicas que procuro.

**Critérios de Aceitação:**

- **C1**: Seleciona filtros (Área, Grau, Ano, Disponibilidade, Competências) → Lista atualizada
- **C2**: Filtros sem currículos → Mensagem "Não existem currículos"

**Tasks Associadas**: T2.3

---

#### **US-5.1: Visualização de Currículos Submetidos (CR)**

**Relacionada com**: FR-4
**Dev Responsável**: Dev 2
**Sprint**: 3

📝 **História**: Como CR, quero visualizar todos os currículos submetidos pelos estudantes, com intuito de selecionar quais precisam ser revisados e validados.

**Critérios de Aceitação:**

- **C1**: Login como CR → Acesso página de validação → Todos os CVs sem filtros (mas com opção de filtrar)
- **C2**: CVs novos não revisados → Claramente sinalizados como "Pendentes"

**Tasks Associadas**: T2.4, T2.5

---

#### **US-5.2: Validação e Revisão de Currículo (CR)**

**Relacionada com**: FR-4
**Dev Responsável**: Dev 2
**Sprint**: 3

📝 **História**: Como CR, quero revisar o conteúdo de cada currículo, aprovando ou reprovando conforme as políticas de dados, com intuito de garantir que apenas currículos adequados sejam validados.

**Critérios de Aceitação:**

- **C1**: Seleciona CV da lista → Abre → Visualiza conteúdo completo
- **C2**: Clica "Aprovar" → CV marcado como válido, desaparece de pendentes
- **C3**: Clica "Reprovar" → Sistema exige justificativa, CV arquivado, notificação enviada ao estudante
- **C4**: Decisão submetida → Visualiza confirmação de sucesso

**Tasks Associadas**: T2.6, T2.7

---

#### **US-6: Autenticação e Perfis (Todos os Utilizadores)**

**Relacionada com**: FR-5, FR-6, FR-7
**Dev Responsável**: Dev 1 (6.1/6.3), Dev 2 (6.4)
**Sprint**: 1-4

📝 **6.1 - Autenticação por Perfil**

História: Enquanto utilizador (estudante, empresa ou CR) quero autenticar-me no sistema com o objetivo de aceder às funcionalidades exclusivas para o meu perfil.

**Critérios de Aceitação:**

- **C1**: Estudante login com sucesso → Redirecionado para "Vagas disponíveis" ou "O meu CV"
- **C2**: Empresa login com sucesso → Redirecionado para "Gestão de vagas" ou "Procura de talento"
- **C3**: Membro CR login → Acesso ao painel de gestão/validação/administração

**Tasks Associadas**: T1.1, T1.2, T1.3, T1.4

---

📝 **6.2 - Segurança de Dados (Visualização sem Download)**

História: Enquanto empresa, devo poder visualizar os currículos de estudantes com o intuito de avaliar candidatos, assegurando a integridade da proteção dos seus dados.

**Critérios de Aceitação:**

- **C1**: Visualizar CV → Sem botão/opção de "Download" do ficheiro original
- **C2**: Ver perfil do candidato → Marca d'água/banner indicando origem na plataforma

**Tasks Associadas**: T1.18, T1.19 (Storage com URLs assinadas)

---

📝 **6.3 - Gestão e Validação por CR**

História: Enquanto membro da equipa de CR, apenas eu posso validar os currículos submetidos de forma a garantir a qualidade e veracidade da informação antes desta estar visível para as empresas.

**Critérios de Aceitação:**

- **C1**: Acedo lista de tarefas → Vejo CVs novos com estado "Pendente"
- **C2**: Revendo CV com desconformidades → Opção de "Rejeitar" + inserir motivo
- **C3**: CV conforme → Clico "Aprovar" → Estado passa a "Ativo", pesquisável pelas empresas

**Tasks Associadas**: T2.4, T2.5, T2.6, T2.7

---

📝 **6.4 - Gestão de Empresas por CR**

História: Enquanto membro de CR, apenas eu posso gerir os dados das empresas registadas, com intuito de manter a base de dados de parceiros correta e atualizada.

**Critérios de Aceitação:**

- **C1**: No painel de administração → Pesquiso empresa parceira → Visualizo e edito campos de perfil
- **C2**: Altero informação → Guardo → Atualização reflete-se imediatamente no perfil público

**Tasks Associadas**: T3.1, T3.2

---

## 📋 Requisitos Funcionais Originais

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

## �️ Estrutura da Base de Dados

### **Visão Geral**

A base de dados está estruturada no Supabase (PostgreSQL) com as seguintes tabelas principais:

### **Tabelas Core**

#### **utilizador** (Tabela Base)

- **auth_user_supabase__id** (INTEGER, PK, FK): Referência ao user do Supabase
- **nome** (VARCHAR): Nome completo
- **descricao** (TEXT): Descrição/biografia
- **tipo** (SMALLINT): Tipo de utilizador (0=CR, 1=Empresa, 2=Estudante)

---

### **Perfis de Utilizadores**

#### **estudante**

- **utilizador_auth_user_supabase__id** (INTEGER, PK, FK): Referência ao utilizador
- **tipo** (SMALLINT, DEFAULT 2): Tipo fixo = Estudante
- **idade** (INTEGER): Idade do estudante
- **grau** (VARCHAR): Grau académico (Licenciatura, Mestrado, etc.)
- **ano** (INTEGER): Ano curricular
- **disponibilidade** (VARCHAR): Disponibilidade (Full-time, Part-time, etc.)
- **share_aceites** (BOOL): ✅ **Consentimento de partilha de dados (US-2.2)**

**Relacionamentos:**

- Relacionamento N:N com **area** via tabela `area_estudante`
- 1:1 com **curriculo**

#### **empresa**

- **utilizador_auth_user_supabase__id** (INTEGER, PK, FK): Referência ao utilizador
- **tipo** (SMALLINT, DEFAULT 1): Tipo fixo = Empresa
- **localizacao** (VARCHAR): Localização física
- **website** (VARCHAR): URL do website

**Relacionamentos:**

- Relacionamento N:N com **area** via tabela `empresa_area`
- 1:N com **vaga**

#### **cr** (Career Services)

- **utilizador_auth_user_supabase__id** (INTEGER, PK, FK): Referência ao utilizador
- **tipo** (SMALLINT, DEFAULT 0): Tipo fixo = CR

**Relacionamentos:**

- Relacionamento N:N com **curriculo** via tabela `cr_curriculo` (histórico de validações)

---

### **Entidades Principais**

#### **vaga** (Job Postings - US-1)

- **id** (SERIAL, PK): ID único da vaga
- **nome** (VARCHAR, UNIQUE): Título da vaga
- **descricao** (TEXT): Descrição detalhada
- **oportunidade** (VARCHAR): Tipo (estágio/emprego/projeto)
- **visualizacoes** (INTEGER): Contador de visualizações
- **candidaturas** (INTEGER): Contador de candidaturas
- **empresa_utilizador_auth_user_supabase__id** (INTEGER, FK): Empresa criadora

**Relacionamentos:**

- Relacionamento N:N com **area** via tabela `vaga_area`
- N:1 com **empresa**

#### **curriculo** (CV - US-2)

- **id** (SERIAL, PK): ID único do CV
- **file** (BYTEA): ⚠️ Ficheiro PDF em binário (considerar migrar para Storage URL)
- **status** (INTEGER): Estado de validação
  - `0` ou `NULL`: Pendente
  - `1`: Aprovado
  - `2`: Rejeitado
- **descricao** (TEXT): Descrição adicional do perfil
- **validated_date** (DATE): Data de validação pelo CR
- **estudante_utilizador_auth_user_supabase__id** (INTEGER, UNIQUE, FK): Estudante (1:1)

**Relacionamentos:**

- 1:1 com **estudante** (UNIQUE constraint)
- N:N com **cr** via tabela `cr_curriculo`

#### **area** (Áreas de Conhecimento)

- **id** (SERIAL, PK): ID único da área
- **nome** (VARCHAR): Nome da área (IT, Engenharia, Marketing, etc.)
- **descricao** (TEXT): Descrição da área

**Relacionamentos:**

- N:N com **estudante**, **empresa**, **vaga**

---

### **Tabelas de Relacionamento (Many-to-Many)**

| Tabela                   | Relaciona         | Campos PK                                            |
| ------------------------ | ----------------- | ---------------------------------------------------- |
| **area_estudante** | Area ↔ Estudante | area_id, estudante_utilizador_auth_user_supabase__id |
| **empresa_area**   | Empresa ↔ Area   | empresa_utilizador_auth_user_supabase__id, area_id   |
| **vaga_area**      | Vaga ↔ Area      | vaga_id, area_id                                     |
| **cr_curriculo**   | CR ↔ Currículo  | cr_utilizador_auth_user_supabase__id, curriculo_id   |

---

### **Mapeamento BD → User Stories**

| Tabela/Campo                        | User Story               | Descrição                                              |
| ----------------------------------- | ------------------------ | -------------------------------------------------------- |
| `vaga.*`                          | **US-1**           | Submissão de vagas por empresas                         |
| `curriculo.file`                  | **US-2.1**         | Upload de CV (PDF)                                       |
| `estudante.share_aceites`         | **US-2.2**         | ✅ Consentimento de partilha de dados                    |
| `vaga_area`, `area`             | **US-3.1, US-3.2** | Filtros de vagas por área                               |
| `curriculo.status`                | **US-5.1, US-5.2** | Estados de validação (Pendente/Aprovado/Rejeitado)     |
| `cr_curriculo`                    | **US-5.2**         | Histórico de validações por CR                        |
| `curriculo.validated_date`        | **US-5.2**         | Data de aprovação/rejeição                           |
| `area_estudante`, `estudante.*` | **US-4.1, US-4.2** | Filtros de CVs por área, grau, ano, disponibilidade     |
| `utilizador.tipo`                 | **US-6.1**         | Discriminação de perfis (CR=0, Empresa=1, Estudante=2) |

---

### **⚠️ Considerações Técnicas**

#### **1. Armazenamento de Ficheiros**

- ⚠️ Atualmente: `curriculo.file` usa **BYTEA** (binário na BD)
- ✅ **Recomendação (T2.1-T2.6)**: Migrar para **Supabase Storage**
  - Adicionar campo `storage_path` (VARCHAR)
  - Gerar **signed URLs** temporárias (15 min)
  - Remover campo `file` (BYTEA) em produção

#### **2. Consentimento de Dados (US-2.2)**

- ✅ Campo `estudante.share_aceites` (BOOL) já implementa requisito
- **Validação**: Estudante só pode submeter CV se `share_aceites = TRUE`
- **GDPR Compliance**: Registar timestamp de consentimento (adicionar campo `consent_date`)

#### **3. Estados de CV**

```python
# Mapeamento proposto para curriculo.status
CV_STATUS_CHOICES = [
    (0, 'Pendente'),      # Submetido, aguarda validação
    (1, 'Aprovado'),      # Validado pelo CR, visível para empresas
    (2, 'Rejeitado'),     # Rejeitado pelo CR, não visível
]
```

#### **4. Otimizações Futuras (Sprint 4)**

- Adicionar índices em:
  - `curriculo.status` (queries de filtro)
  - `vaga.oportunidade` (filtros de tipo)
  - `area.nome` (pesquisas)
  - `utilizador.tipo` (queries de role)

---

## 🀽� Estrutura de Tasks Detalhada

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
- **T0.3** - Criar modelos Django base mapeando tabelas Supabase
  - Modelo `User` → tabela `utilizador` (auth_user_supabase__id, nome, descricao, tipo)
  - Modelo `Area` → tabela `area` (id, nome, descricao)
  - Configurar `managed = False` (tabelas geridas pelo Supabase)
  - Adicionar `db_table` explícito para cada modelo
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
|                |                                                                                         | T1.2          |
| **T1.4** | Criar decoradores/permissions customizados DRF (`IsStudent`, `IsCompany`, `IsCR`) | T1.2          |
| **T1.5** | Escrever testes unitários do middleware                                                | T1.4          |
| **T1.6** | Documentar usage do header para Postman                                                 | T1.4          |

**Entregável**: Middleware funcional + Postman Collection com exemplos

---

### **Dev 2: Modelo de Vagas (FR-1)**

| Task            | Descrição                                                                                                                                                   | Dependências |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| **T1.7**  | Criar modelo `Vaga` mapeando tabela `vaga` (nome UNIQUE, descricao, oportunidade, visualizacoes, candidaturas, empresa_utilizador_auth_user_supabase__id) | T0.3          |
| **T1.8**  | Criar modelo `Empresa` mapeando tabela `empresa` (tipo, localizacao, website, utilizador_auth_user_supabase__id)                                          | T1.7          |
| **T1.9**  | Criar Serializer para `Vaga` com validações (nome, descricao, oportunidade obrigatórios) + nested Areas via `vaga_area`                                | T1.8          |
| **T1.10** | Implementar ViewSet básico (CRUD) com permissão `IsCompany`                                                                                               | T1.4, T1.9    |
| **T1.11** | Adicionar filtro "minhas vagas" (empresa_utilizador_auth_user_supabase__id = X-User-ID)                                                                       | T1.10         |
| **T1.12** | Testes de integração (POST vaga + areas, GET, PUT, DELETE, validação UNIQUE nome)                                                                         | T1.11         |

**Entregável**: API de Vagas funcional para Empresas

---

### **Dev 3: Modelo de CVs (FR-2 Parte 1)**

| Task            | Descrição                                                                                                                                                                     | Dependências |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
|                 |                                                                                                                                                                                 | T0.3          |
| **T1.14** | Criar modelo `Estudante` mapeando tabela `estudante` (tipo=2, idade, grau, ano, disponibilidade, **share_aceites BOOL**) + relacionamento Area via `area_estudante` |               |
| **T1.15** | Criar Serializer `CurriculoSerializer` com **validação crítica US-2.2**: verificar `estudante.share_aceites = TRUE` antes de permitir submissão                   | T1.14         |
| **T1.16** | Implementar ViewSet `CurriculoViewSet` (GET meu CV, POST criar CV) com permissão `IsStudent`                                                                               | T1.4, T1.15   |
| **T1.17** | Validação adicional: verificar UNIQUE constraint (estudante só pode ter 1 CV) e retornar erro 400 se tentar criar duplicado                                                  | T1.16         |
| **T1.18** | Testes: (1) POST com share_aceites=FALSE → 403 Forbidden; (2) POST com share_aceites=TRUE → 201 Created; (3) POST duplicado → 400 Bad Request                                | T1.17         |

**Entregável**: API de CV com validação de consentimento (US-2.2) ✅

---

### **Dev 4: Setup de Testes + CI/CD Base**

| Task            | Descrição                                          | Dependências |
| --------------- | ---------------------------------------------------- | ------------- |
| **T1.19** | Configurar pytest + pytest-django                    | Nenhuma       |
| **T1.20** | Criar fixtures reutilizáveis (mock users com roles) | T1.19         |
| **T1.21** | Configurar GitHub Actions usar testes               | T1.19         |
| **T1.22** | Documentar estrutura de testes                       | T1.21         |
|                 |                                                      |               |

**Entregável**: Pipeline CI + Fixtures

---

### ✅ **Demo Sprint 1**

- ✓ Middleware de auth a funcionar
- ✓ Empresa consegue criar/editar/listar vagas
- ✓ Estudante consegue submeter CV (URL mock)
- ✓ Testes automatizados a correr

---

## 🎯 **SPRINT 2** (Semanas 3-4): Upload Storage + Filtros Básicos

### **Dev 1: Integração Supabase Storage (FR-2 Parte 2)**

| Task           | Descrição                                                                                                | Dependências |
| -------------- | ---------------------------------------------------------------------------------------------------------- | ------------- |
| **T2.1** | Criar service layer `SupabaseStorageService` (upload, delete, get_signed_url)                            | T0.2          |
| **T2.2** | Implementar endpoint `POST /api/curriculo/upload/` (aceita PDF, max 5MB)                                 | T2.1,T1.15    |
| **T2.3** | Validar tipo de ficheiro (PDF) e tamanho (max 5MB) antes do upload                                         | T2.2          |
|                |                                                                                                            |               |
| **T2.4** | Implementar lógica: upload PDF → Supabase Storage → guardar `storage_path` → gerar signed URL (15 m) | T2.2, T2.4    |
| **T2.5** | Testes de meer (mock do Supabase Storage, validar rejeição de ficheiros não-PDF)                        | T2.5          |

**Entregável**: Upload de CV funcional com Storage

---

### **Dev 2: Visualização Segura de Documentos (FR-5)**

| Task            | Descrição                                                                                  | Dependências |
| --------------- | -------------------------------------------------------------------------------------------- | ------------- |
| **T2.7**  | Criar endpoint `GET /curriculo/{id}/view/` (retorna signed URL do Storage)                 | T2.1          |
| **T2.8**  | Validar permissões: Empresa vê CVs aprovados (status=1), CR vê todos, Estudante vê o seu | T1.4, T2.7    |
| **T2.9**  | Implementar expiração de URLs (15 min via Supabase Storage)                                | T2.7          |
| **T2.10** | Criar tabela audit `cv_access_log` (quem viu que CV quando) e registar acessos             | T2.8          |
| **T2.11** | Testes de permissões: matriz completa (Estudante/Empresa/CR vs Status CV)                   | T2.10         |

**Entregável**: Sistema de visualização seguro

---

### **Dev 3: Filtros de Vagas (FR-3 Parte 1)**

| Task            | Descrição                                                                          | Dependências |
| --------------- | ------------------------------------------------------------------------------------ | ------------- |
| **T2.12** | Criar FilterSet para `Vaga` (oportunidade, areas via `vaga_area`, visualizacoes) |               |
|                 |                                                                                      |               |
| **T2.14** | Implementar endpoint `GET /api/vaga/?oportunidade=estagio&area=Informática`       |               |
| **T2.15** | Adicionar paginação (PageNumberPagination) + ordenar por data de criação         | T2.14         |
| **T2.16** | Criar testes de filtros combinados (oportunidade + área + empresa)                  | T2.15         |
| **T2.17** | Documentar query params no Postman Collection                                        | T2.16         |

**Entregável**: Pesquisa de vagas funcional

---

### **Dev 4: Filtros de CVs (FR-3 Parte 2)**

| Task            | Descrição                                                                                                | Dependências |
| --------------- | ---------------------------------------------------------------------------------------------------------- | ------------- |
| **T2.18** | Criar FilterSet para `Estudante` (grau, ano, disponibilidade) + Areas via `area_estudante`             | T1.14, T2.12  |
| **T2.19** | Criar FilterSet para `Curriculo` (status, validated_date) integrado com filtro de Estudante              | T2.18         |
| **T2.20** | Implementar endpoint `GET /api/curriculo/?grau=Mestrado&area=Engenharia&status=1` (apenas CVs aprovados) | T2.19         |
| **T2.21** | Validar permissão:**só Empresas e CR** podem filtrar/listar CVs (IsCompany OR IsCR)                | T1.4, T2.20   |
| **T2.22** | Adicionar paginação + ordenar por `validated_date DESC`                                                | T2.21         |
| **T2.23** | Teste: (1) Filtros combinados; (2) Estudante tenta acessar lista → 403 Forbidden;                         | T2.22         |

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

| Task           | Descrição                                                                                                                                                | Dependências |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
|                |                                                                                                                                                            |               |
| **T3.2** | Adicionar constantes Python `CV_STATUS_PENDING=0, CV_STATUS_APPROVED=1, CV_STATUS_REJECTED=2` ao modelo `Curriculo`                                    |               |
| **T3.3** | Usar tabela `cr_curriculo` (já existe) para mapear histórico CR ↔ Currículo + adicionar campo `feedback TEXT` e `review_date DATE` via migration | T0.3          |
| **T3.4** | Criar Serializer `CRReviewSerializer` (curriculo_id, feedback, status, review_date)                                                                      | T3.3          |
| **T3.5** | endpoint `POST /api/cr/curriculo/{id}/review/` (aprovar/rejeitar) com permission `IsCR`                                                                | T3.4, T1.4    |
| **T3.6** | Validar: apenas utilizadores com `tipo=0` (CR) podem fazer review                                                                                        | T3.5          |
| **T3.7** | Ao aprovar/rejeitar: (1) Atualizar `curriculo.status`; (2) Inserir em `cr_curriculo`; (3) Preencher `validated_date`                                 | T3.5          |

**Entregável**: Fluxo de aprovação funcional

---

### **Dev 2: Dashboard CR (FR-4 Parte 2)**

| Task            | Descrição                                                                                                                     | Dependências |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| **T3.8**  | Criar endpoint `GET /api/cr/curriculo/pending/` (listar `curriculo.status=0`) permission `IsCR`                           | T1.4          |
| **T3.9**  | Adicionar endpoint `GET /api/cr/curriculo/stats/` retornando contadores: {pending: N, approved: N, rejected: N}               | T3.8          |
| **T3.10** | Adicionar filtros ao endpoint T3.8: ?grau=Mestrado&area=Informática&data_submissao_after=2025-01-01                            | T3.8          |
| **T3.11** | Criar endpoint `GET /api/cr/curriculo/{id}/history/` retornando registos de `cr_curriculo` (quem validou, quando, feedback) | T3.3, T3.8    |
| **T3.12** | Testes: (1) Listar pendentes; (2) Stats corretas; (3) Histórico completo; (4) Estudante tenta acessar → 403                   | T3.11         |

**Entregável**: Dashboard CR funcional

---

### **Dev 3: Sistema de Notificações (Email/Webhook)**

| Task            | Descrição                                                     | Dependências |
| --------------- | --------------------------------------------------------------- | ------------- |
|                 |                                                                 |               |
| **T3.14** | Criar task `send_cv_status_notification` (email ao estudante) |               |
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

### **Dev 2: Documentação API**

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
|                 | Criar endpoint de "arquivar vaga"                                  | T4.12         |
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
