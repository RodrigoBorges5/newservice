# API Documentation

Guia para endpoints com exemplos e respostas:

**Base URL:** `http://localhost:8000/service/`

**T.1.1 - Base Authentication - Qualquer URL menos os incluidos no EXCLUDED_PATH em middleware.py**

Resposta sem Header:
{
"detail": "Header X-User-ID em falta"
}

Resposta com Header X-User_ID:
X-User-ID = [ID]
{
"status": "ok",
"user_id": [ID]
"user_role": [tipo de utilizador]
}

**T.1.4 - Role Authentication - Qualquer URL com limitação de role**
**Exemplo: necessita de role estudante (permission_classes = [IsStudent])**

Resposta sem role estudante:
{
"detail": "Não possui permição para efetuar esta ação."
}

Resposta com Header X-User_ID:
X-User-ID = [ID]
{
"status": "ok",
"user_id": [ID],
"user_role": 2
}

---

## Endpoints de Currículo

### GET /curriculo/me/

**Descrição:** Retorna o currículo do estudante autenticado
**Permissão:** IsStudent (role=2)
**Headers:** X-User-ID = [ID do estudante]

**Resposta com sucesso (200 OK):**

```json
{
  "id": 1,
  "file": "path/to/curriculo.pdf",
  "status": 0,
  "descricao": "Currículo atualizado 2026",
  "validated_date": null,
  "estudante_utilizador_auth_user_supabase_field": "uuid-estudante"
}
```

**Resposta sem currículo (404 NOT FOUND):**

```json
{
  "detail": "Currículo não encontrado. Por favor, submeta o seu CV."
}
```

**Resposta sem perfil de estudante (404 NOT FOUND):**

```json
{
  "detail": "Perfil de estudante não encontrado."
}
```

---

### POST /curriculo/me/

**Descrição:** Cria novo currículo para o estudante autenticado (US-2.2)
**Permissão:** IsStudent (role=2)
**Headers:** X-User-ID = [ID do estudante]

**Body (exemplo):**

```json
{
  "file": "path/to/meu_curriculo.pdf",
  "descricao": "Currículo com experiência em Python e Django"
}
```

**Resposta com sucesso (201 CREATED):**

```json
{
  "message": "Currículo submetido com sucesso! Aguarde validação da equipa CR.",
  "data": {
    "id": 1,
    "file": "path/to/meu_curriculo.pdf",
    "status": 0,
    "descricao": "Currículo com experiência em Python e Django",
    "validated_date": null,
    "estudante_utilizador_auth_user_supabase_field": "uuid-estudante"
  }
}
```

**Resposta com CV duplicado (400 BAD REQUEST):**

```json
{
  "detail": "Já existe um currículo associado a este estudante."
}
```

**Resposta sem aceitar termos (400 BAD REQUEST):**

```json
{
  "detail": "Erro ao submeter currículo: deves aceitar."
}
```

ou

```json
{
  "estudante_utilizador_auth_user_supabase_field": [
    "Deves aceitar a partilhar os dados a submeter o curriculo. Por favor, aceite os termos de dados."
  ]
}
```

**Resposta com ficheiro não-PDF (400 BAD REQUEST):**

```json
{
  "file": ["O ficheiro do curriculo deve estar em formato PDF."]
}
```

**Resposta com caminho muito longo (400 BAD REQUEST):**

```json
{
  "file": ["O caminho do ficheiro é demasiado longo."]
}
```

---

### DELETE /curriculo/me/

**Descrição:** Remove o currículo do estudante autenticado
**Permissão:** IsStudent (role=2)
**Headers:** X-User-ID = [ID do estudante]

**Resposta com sucesso (204 NO CONTENT):**

```json
{
  "message": "Currículo eliminado com sucesso. Crie novo CV se desejar."
}
```

**Resposta sem currículo (404 NOT FOUND):**

```json
{
  "detail": "Currículo não encontrado. Por favor, submeta o seu CV."
}
```

---

## Task Assíncrona: Notificação de Email (CV Status)

### Descrição

Task `send_cv_status_notification` em `service/tasks.py` que envia automaticamente um email ao estudante quando o estado do seu currículo é alterado (aprovado ou rejeitado) pela equipa CR.

Utiliza o sistema de tasks nativo do Django (`django.tasks`) para execução assíncrona.

### Parâmetros

| Parâmetro      | Tipo | Obrigatório                    | Descrição                                    |
| -------------- | ---- | ------------------------------ | -------------------------------------------- |
| `curriculo_id` | int  | Sim                            | ID do currículo validado                     |
| `status`       | int  | Sim                            | Novo status: `1` = Aprovado, `2` = Rejeitado |
| `feedback`     | str  | Rejeição: Sim / Aprovação: Não | Comentário do CR                             |

### Integração com o Modelo Curriculo

A task é disparada automaticamente pelos métodos `approve()` e `reject()` do modelo `Curriculo`:

```python
# Aprovar currículo (feedback opcional)
curriculo = Curriculo.objects.get(id=1)
curriculo.approve(feedback="Excelente currículo!")

# Rejeitar currículo (feedback obrigatório)
curriculo = Curriculo.objects.get(id=1)
curriculo.reject(feedback="Falta experiência profissional (...)")
```

### Fluxo da Task

1. Validação dos parâmetros (status válido, feedback obrigatório para rejeição)
2. Procura do currículo e dados do estudante na base de dados
3. Obtenção do email do estudante via Supabase Auth (admin API)
4. Renderização do template HTML apropriado (aprovação ou rejeição)
5. Envio do email via Django `send_mail`
6. Registo de log (sucesso ou falha)

### Templates de Email

- **Aprovação** (`service/templates/email/cv_aprovado.html`): Mensagem de parabéns, próximos passos, link para a plataforma
- **Rejeição** (`service/templates/email/cv_rejeitado.html`): Feedback do CR, orientações de correção, instruções de re-submissão

### Configuração

Variáveis de ambiente necessárias:

| Variável             | Descrição                                    | Default                          |
| -------------------- | -------------------------------------------- | -------------------------------- |
| `SITE_URL`           | URL base da plataforma (usado nos templates) | `http://localhost:8000`          |
| `DEFAULT_FROM_EMAIL` | Remetente dos emails                         | `noreply@plataforma-estagios.pt` |

Settings em `newservice/settings.py`:

```python
# Console backend (dev) – Em produção usar smtp.EmailBackend
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

### Logs

A task regista logs com o prefixo `[CV Notification]`:

```
INFO  [CV Notification] curriculo_id=1 A iniciar envio – status=Aprovado, estudante=João
INFO  [CV Notification] curriculo_id=1 Email enviado com sucesso para joao@email.com (status=Aprovado)
ERROR [CV Notification] curriculo_id=1 Falha ao enviar email para joao@email.com: ...
```

### Retorno

A task retorna um dicionário com o resultado:

```json
{
  "success": true,
  "curriculo_id": 1,
  "status": "Aprovado",
  "email": "estudante@email.com",
  "message": "Email enviado com sucesso."
}
```

---

## Endpoints de Vagas

### Visão Geral

O endpoint `/vagas` permite gerir oportunidades de trabalho (vagas) no sistema. Suporta operações CRUD com controlo de acesso baseado em roles e propriedade.

### Permissões por Role

| Role          | Código | Permissões                                                    |
| ------------- | ------ | ------------------------------------------------------------- |
| **CR**        | 0      | CRUD completo (admin) - pode modificar/eliminar QUALQUER vaga |
| **Empresa**   | 1      | CRUD próprio - pode modificar/eliminar apenas SUAS vagas      |
| **Estudante** | 2      | Apenas leitura (GET)                                          |

#### Matriz de Permissões

| Método | Endpoint       | CR  | Empresa (própria) | Empresa (de outro) | Estudante |
| ------ | -------------- | :-: | :---------------: | :----------------: | :-------: |
| GET    | `/vagas/`      | ✅  |        ✅         |         ✅         |    ✅     |
| GET    | `/vagas/{id}/` | ✅  |        ✅         |         ✅         |    ✅     |
| POST   | `/vagas/`      | ✅  |        ✅         |         ✅         |    ❌     |
| PUT    | `/vagas/{id}/` | ✅  |        ✅         |      ❌ (403)      |    ❌     |
| PATCH  | `/vagas/{id}/` | ✅  |        ✅         |      ❌ (403)      |    ❌     |
| DELETE | `/vagas/{id}/` | ✅  |        ✅         |      ❌ (403)      |    ❌     |

#### Regras de Propriedade

- **CR (role=0)**: Administrador - pode criar, editar e eliminar **qualquer vaga** do sistema
- **Empresa (role=1)**: Só pode editar/eliminar vagas onde `empresa_utilizador_auth_user_supabase_field == X-User-ID`
- **Estudante (role=2)**: Apenas leitura, não pode criar/editar/eliminar

---

### GET /vagas/

**Descrição:** Lista todas as vagas ou filtra por parâmetros de query  
**Permissões:** Qualquer role autenticado (CR, Empresa, Estudante)  
**Headers:** X-User-ID = [ID do utilizador]

**Parâmetros de Query Disponíveis:**

| Parâmetro           | Tipo    | Descrição                                                                               |
| ------------------- | ------- | --------------------------------------------------------------------------------------- |
| `mine`              | boolean | Filtra vagas pela empresa do utilizador logado                                          |
| `oportunidade`      | string  | Filtra por tipo (case-insensitive): estagio, emprego, projeto                           |
| `area`              | string  | Filtra por nome(s) de área (case-insensitive), separados por vírgula                    |
| `area_match`        | string  | Modo de correspondência: `or` (padrão) ou `and`                                         |
| `visualizacoes_min` | int     | Mínimo de visualizações                                                                 |
| `visualizacoes_max` | int     | Máximo de visualizações                                                                 |
| `ordering`          | string  | Ordenação: `id`, `nome`, `visualizacoes`, `candidaturas` (prefixo `-` para descendente) |
| `page`              | int     | Número da página (padrão: 1)                                                            |
| `page_size`         | int     | Itens por página (padrão: 20)                                                           |

**Exemplo 1 - Listar todas:**

```http
GET /service/vagas/
X-User-ID: uuid-do-utilizador
```

**Resposta (200 OK):**

```json
{
  "count": 150,
  "next": "http://localhost:8000/service/vagas/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "nome": "Desenvolvedor Python",
      "descricao": "Vaga para desenvolvedor backend",
      "oportunidade": "emprego",
      "visualizacoes": 45,
      "candidaturas": 12,
      "empresa_utilizador_auth_user_supabase_field": "uuid-da-empresa",
      "areas": [
        { "id": 1, "nome": "Python", "descricao": "Linguagem Python" },
        { "id": 2, "nome": "Django", "descricao": "Framework Django" }
      ]
    }
  ]
}
```

**Exemplo 2 - Minhas vagas (empresa):**

```http
GET /service/vagas/?mine=true
X-User-ID: uuid-da-empresa
```

**Exemplo 3 - Filtros combinados:**

```http
GET /service/vagas/?oportunidade=estagio&area=Python,Django&area_match=and&visualizacoes_min=50&ordering=-visualizacoes
X-User-ID: uuid-do-utilizador
```

**Resultado:** Estágios que têm Python **E** Django, com pelo menos 50 visualizações, ordenados por visualizações (mais populares primeiro).

---

### GET /vagas/{id}/

**Descrição:** Obtém detalhes de uma vaga específica  
**Permissões:** Qualquer role autenticado  
**Headers:** X-User-ID = [ID do utilizador]

**Resposta (200 OK):**

```json
{
  "id": 1,
  "nome": "Desenvolvedor Python",
  "descricao": "Vaga para desenvolvedor backend com experiência em Django",
  "oportunidade": "emprego",
  "visualizacoes": 45,
  "candidaturas": 12,
  "empresa_utilizador_auth_user_supabase_field": "uuid-da-empresa",
  "areas": [
    { "id": 1, "nome": "Python", "descricao": "Linguagem Python" },
    { "id": 2, "nome": "Django", "descricao": "Framework Django" },
    { "id": 3, "nome": "Backend", "descricao": "Desenvolvimento backend" }
  ]
}
```

**Resposta de erro (404 NOT FOUND):**

```json
{
  "detail": "Not found."
}
```

---

### POST /vagas/

**Descrição:** Cria nova vaga  
**Permissões:** CR (role=0), Empresa (role=1)  
**Headers:** X-User-ID = [ID da empresa/CR]

**Body (exemplo):**

```json
{
  "nome": "Desenvolvedor Frontend",
  "descricao": "Vaga para desenvolvedor frontend com experiência em React",
  "oportunidade": "emprego",
  "empresa_utilizador_auth_user_supabase_field": "uuid-da-empresa",
  "areas": [{ "nome": "React" }, { "nome": "JavaScript" }, { "id": 5 }]
}
```

**Campos Obrigatórios:**

| Campo          | Tipo   | Validação                                      |
| -------------- | ------ | ---------------------------------------------- |
| `nome`         | string | Obrigatório, não vazio, único                  |
| `descricao`    | string | Obrigatório, não vazio                         |
| `oportunidade` | string | Obrigatório: `estagio`, `emprego` ou `projeto` |

**Campos Opcionais:**

| Campo                                         | Tipo  | Descrição                       |
| --------------------------------------------- | ----- | ------------------------------- |
| `empresa_utilizador_auth_user_supabase_field` | uuid  | UUID da empresa dona da vaga    |
| `areas`                                       | array | Lista de áreas (por nome ou id) |

**Formato das Áreas:**

As áreas podem ser especificadas por **nome** ou **id**:

```json
// Por nome (cria se não existir)
{"areas": [{"nome": "Python"}, {"nome": "Django"}]}

// Por ID (usa área existente)
{"areas": [{"id": 1}, {"id": 2}]}

// Misto
{"areas": [{"id": 1}, {"nome": "Nova Área"}]}
```

**Resposta (201 CREATED):**

```json
{
  "id": 5,
  "nome": "Desenvolvedor Frontend",
  "descricao": "Vaga para desenvolvedor frontend com experiência em React",
  "oportunidade": "emprego",
  "visualizacoes": null,
  "candidaturas": null,
  "empresa_utilizador_auth_user_supabase_field": "uuid-da-empresa",
  "areas": [
    { "id": 8, "nome": "React", "descricao": null },
    { "id": 9, "nome": "JavaScript", "descricao": null },
    { "id": 5, "nome": "Backend", "descricao": "Desenvolvimento backend" }
  ]
}
```

**Respostas de erro (400 BAD REQUEST):**

```json
{
  "nome": ["Este campo é obrigatório."],
  "oportunidade": [
    "Oportunidade inválida. Opções válidas: estagio, emprego, projeto"
  ]
}
```

**Resposta sem permissão (403 FORBIDDEN):**

```json
{
  "detail": "Não possui permissão para efetuar esta ação."
}
```

---

### PUT /vagas/{id}/

**Descrição:** Atualiza todos os campos de uma vaga (substituição completa)  
**Permissões:** CR (qualquer vaga), Empresa (apenas suas vagas)  
**Headers:** X-User-ID = [ID da empresa/CR]

Substitui todos os campos da vaga. Todos os campos obrigatórios devem ser enviados.

**Body (exemplo):**

```json
{
  "nome": "Novo Nome da Vaga",
  "descricao": "Nova descrição completa",
  "oportunidade": "estagio",
  "empresa_utilizador_auth_user_supabase_field": "uuid-da-empresa",
  "areas": [{ "nome": "Frontend" }, { "nome": "React" }]
}
```

**Resposta (200 OK):** Objeto atualizado completo

**Resposta sem propriedade (403 FORBIDDEN):**

```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### PATCH /vagas/{id}/

**Descrição:** Atualiza campos específicos de uma vaga (atualização parcial)  
**Permissões:** CR (qualquer vaga), Empresa (apenas suas vagas)  
**Headers:** X-User-ID = [ID da empresa/CR]

Atualiza apenas os campos enviados. Campos não incluídos permanecem inalterados.

**Exemplo 1 - Atualizar apenas o nome:**

```json
{
  "nome": "Nome Atualizado"
}
```

**Exemplo 2 - Atualizar áreas:**

```json
{
  "areas": [{ "nome": "Docker" }, { "nome": "Kubernetes" }]
}
```

**Nota:** Ao atualizar `areas`, as áreas antigas são substituídas pelas novas.

**Resposta (200 OK):** Objeto atualizado completo

---

### DELETE /vagas/{id}/

**Descrição:** Elimina uma vaga  
**Permissões:** CR (qualquer vaga), Empresa (apenas suas vagas)  
**Headers:** X-User-ID = [ID da empresa/CR]

**Resposta (204 NO CONTENT):** Sucesso, sem corpo de resposta

**Resposta sem propriedade (403 FORBIDDEN):**

```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Resposta vaga não encontrada (404 NOT FOUND):**

```json
{
  "detail": "Not found."
}
```

---

### Filtros Avançados

#### Filtrar por Oportunidade

O filtro de oportunidade é **case-insensitive**:

```http
GET /service/vagas/?oportunidade=ESTAGIO     ✅ Funciona
GET /service/vagas/?oportunidade=emprego     ✅ Funciona
GET /service/vagas/?oportunidade=Projeto     ✅ Funciona
```

Valores válidos: `estagio`, `emprego`, `projeto`

---

#### Filtrar por Área

Filtra pelo **nome** da área (não pelo ID), também **case-insensitive**:

```http
# Uma área
GET /service/vagas/?area=Python

# Múltiplas áreas (modo OR - padrão)
GET /service/vagas/?area=Python,Django,React

# Múltiplas áreas (modo AND)
GET /service/vagas/?area=Python,Django&area_match=and
```

**Modo de Correspondência (`area_match`):**

| Valor | Descrição                                                   |
| ----- | ----------------------------------------------------------- |
| `or`  | (Padrão) Retorna vagas que têm **pelo menos uma** das áreas |
| `and` | Retorna vagas que têm **todas** as áreas especificadas      |

**Exemplos:**

```http
# Vagas com Python OU Django
GET /service/vagas/?area=Python,Django

# Vagas com Python E Django (obrigatoriamente ambas)
GET /service/vagas/?area=Python,Django&area_match=and
```

---

#### Filtrar por Visualizações

```http
# Mínimo de 100 visualizações
GET /service/vagas/?visualizacoes_min=100

# Máximo de 500 visualizações
GET /service/vagas/?visualizacoes_max=500

# Range de visualizações
GET /service/vagas/?visualizacoes_min=100&visualizacoes_max=500
```

---

#### Ordenação

A listagem suporta ordenação customizada:

```http
# Ordenar por nome ascendente
GET /service/vagas/?ordering=nome

# Ordenar por visualizações descendente
GET /service/vagas/?ordering=-visualizacoes

# Ordenar por candidaturas descendente
GET /service/vagas/?ordering=-candidaturas
```

**Campos disponíveis:** `id`, `nome`, `visualizacoes`, `candidaturas`  
**Padrão:** `id` (ascendente)  
**Nota:** Prefixo `-` inverte a ordenação (descendente)

---

#### Paginação

A listagem é paginada automaticamente:

```http
GET /service/vagas/?page=1&page_size=10
```

| Parâmetro   | Padrão | Descrição                                       |
| ----------- | ------ | ----------------------------------------------- |
| `page`      | 1      | Número da página                                |
| `page_size` | 20     | Itens por página (máximo definido nas settings) |

**Estrutura da resposta paginada:**

| Campo      | Descrição                                   |
| ---------- | ------------------------------------------- |
| `count`    | Total de vagas que correspondem aos filtros |
| `next`     | URL da próxima página (null se não houver)  |
| `previous` | URL da página anterior (null se não houver) |
| `results`  | Array de vagas da página atual              |

---

### Valores Válidos para Oportunidade

| Valor     | Descrição                          |
| --------- | ---------------------------------- |
| `estagio` | Estágio curricular ou profissional |
| `emprego` | Vaga de emprego efetivo            |
| `projeto` | Projeto temporário                 |

---

### Comportamento das Áreas

**Criação/Atualização:**

1. **Por nome:** Se a área não existir, será criada automaticamente
2. **Por ID:** Usa a área existente com o ID especificado
3. **Atualização:** Substitui todas as áreas anteriores pelas novas

**Resposta:**

As áreas são sempre retornadas com `id`, `nome` e `descricao`:

```json
"areas": [
    {"id": 1, "nome": "Python", "descricao": "Linguagem Python"},
    {"id": 2, "nome": "Django", "descricao": "Framework Django"}
]
```

---

### Notas Importantes

1. **CR como Admin:** O role CR (código 0) tem permissões administrativas completas, podendo criar, editar e eliminar **qualquer vaga** do sistema.

2. **Empresas e Propriedade:** Empresas só podem editar/eliminar vagas onde o campo `empresa_utilizador_auth_user_supabase_field` corresponde ao seu `X-User-ID`. Tentativas de modificar vagas de outras empresas retornam 403.

3. **Verificação de Propriedade:** A verificação ocorre ao nível do objeto. Uma empresa pode aceder ao endpoint `/vagas/{id}/` com PUT/PATCH/DELETE, mas receberá 403 se a vaga não lhe pertencer.

4. **Criação de Vagas:** Ao criar uma vaga, a empresa deve passar o seu próprio UUID em `empresa_utilizador_auth_user_supabase_field` para depois poder editá-la.

5. **Áreas Automáticas:** Áreas passadas por nome são criadas automaticamente se não existirem.

6. **Filtro mine:** O filtro `mine=true` usa o UUID do header `X-User-ID` para filtrar.

7. **Campos Read-Only:** `id`, `visualizacoes` e `candidaturas` são campos read-only e não podem ser definidos/modificados via API.

---

## Códigos de Resposta HTTP

| Código | Significado                         |
| ------ | ----------------------------------- |
| 200    | Sucesso (GET, PUT, PATCH)           |
| 201    | Criado com sucesso (POST)           |
| 204    | Eliminado com sucesso (DELETE)      |
| 400    | Erro de validação                   |
| 401    | Não autenticado (X-User-ID ausente) |
| 403    | Sem permissão para a ação           |
| 404    | Recurso não encontrado              |

---
