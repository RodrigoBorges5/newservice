# API de Vagas - Documentação

## Visão Geral

O endpoint `/vagas` permite gerir oportunidades de trabalho (vagas) no sistema. Suporta operações CRUD com controlo de acesso baseado em roles e propriedade.

---

## Base URL

```
http://localhost:8000/service/vagas/
```

---

## Permissões por Role

| Role          | Código | Permissões                                                    |
| ------------- | ------ | ------------------------------------------------------------- |
| **CR**        | 0      | CRUD completo (admin) - pode modificar/eliminar QUALQUER vaga |
| **Empresa**   | 1      | CRUD próprio - pode modificar/eliminar apenas SUAS vagas      |
| **Estudante** | 2      | Apenas leitura (GET)                                          |

### Matriz de Permissões

| Método | Endpoint       | CR  | Empresa (própria) | Empresa (de outro) | Estudante |
| ------ | -------------- | :-: | :---------------: | :----------------: | :-------: |
| GET    | `/vagas/`      | ✅  |        ✅         |         ✅         |    ✅     |
| GET    | `/vagas/{id}/` | ✅  |        ✅         |         ✅         |    ✅     |
| POST   | `/vagas/`      | ✅  |        ✅         |         ✅         |    ❌     |
| PUT    | `/vagas/{id}/` | ✅  |        ✅         |      ❌ (403)      |    ❌     |
| PATCH  | `/vagas/{id}/` | ✅  |        ✅         |      ❌ (403)      |    ❌     |
| DELETE | `/vagas/{id}/` | ✅  |        ✅         |      ❌ (403)      |    ❌     |

### Regras de Propriedade

- **CR (role=0)**: Administrador - pode criar, editar e eliminar **qualquer vaga** do sistema
- **Empresa (role=1)**: Só pode editar/eliminar vagas onde `empresa_utilizador_auth_user_supabase_field == X-User-ID`
- **Estudante (role=2)**: Apenas leitura, não pode criar/editar/eliminar

---

## Endpoints

### 1. Listar Vagas

```http
GET /service/vagas/
```

**Parâmetros de Query:**

| Parâmetro | Tipo    | Descrição                                      |
| --------- | ------- | ---------------------------------------------- |
| `mine`    | boolean | Filtra vagas pela empresa do utilizador logado |

**Exemplo - Listar todas:**

```http
GET /service/vagas/
X-User-ID: uuid-do-utilizador
```

**Exemplo - Minhas vagas:**

```http
GET /service/vagas/?mine=true
X-User-ID: uuid-da-empresa
```

**Resposta (200 OK):**

```json
[
  {
    "id": 1,
    "nome": "Desenvolvedor Python",
    "descricao": "Vaga para desenvolvedor backend",
    "oportunidade": "emprego",
    "empresa_utilizador_auth_user_supabase_field": "uuid-da-empresa",
    "areas": [
      { "id": 1, "nome": "Python" },
      { "id": 2, "nome": "Django" }
    ]
  }
]
```

---

### 2. Ver Detalhes de uma Vaga

```http
GET /service/vagas/{id}/
```

**Resposta (200 OK):**

```json
{
  "id": 1,
  "nome": "Desenvolvedor Python",
  "descricao": "Vaga para desenvolvedor backend com experiência em Django",
  "oportunidade": "emprego",
  "empresa_utilizador_auth_user_supabase_field": "uuid-da-empresa",
  "areas": [
    { "id": 1, "nome": "Python" },
    { "id": 2, "nome": "Django" },
    { "id": 3, "nome": "Backend" }
  ]
}
```

**Erros:**

- `404 Not Found` - Vaga não encontrada

---

### 3. Criar Vaga

```http
POST /service/vagas/
```

**Permissões:** CR, Empresa

**Cabeçalhos:**

```http
X-User-ID: uuid-da-empresa
Content-Type: application/json
```

**Corpo:**

```json
{
  "nome": "Nome da Vaga",
  "descricao": "Descrição detalhada da vaga",
  "oportunidade": "emprego",
  "empresa_utilizador_auth_user_supabase_field": "uuid-da-empresa",
  "areas": [{ "nome": "Python" }, { "nome": "Django" }]
}
```

**Campos Obrigatórios:**

| Campo          | Tipo   | Validação                                      |
| -------------- | ------ | ---------------------------------------------- |
| `nome`         | string | Obrigatório, não vazio                         |
| `descricao`    | string | Obrigatório, não vazio                         |
| `oportunidade` | string | Obrigatório: `estagio`, `emprego` ou `projeto` |

**Campos Opcionais:**

| Campo                                         | Tipo  | Descrição                    |
| --------------------------------------------- | ----- | ---------------------------- |
| `empresa_utilizador_auth_user_supabase_field` | uuid  | UUID da empresa dona da vaga |
| `areas`                                       | array | Lista de áreas associadas    |

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

**Resposta (201 Created):**

```json
{
  "id": 5,
  "nome": "Nome da Vaga",
  "descricao": "Descrição detalhada da vaga",
  "oportunidade": "emprego",
  "empresa_utilizador_auth_user_supabase_field": "uuid-da-empresa",
  "areas": [
    { "id": 1, "nome": "Python" },
    { "id": 7, "nome": "Django" }
  ]
}
```

**Erros:**

- `400 Bad Request` - Campos obrigatórios faltando ou inválidos
- `403 Forbidden` - Sem permissão (Estudante tentando criar)

---

### 4. Atualizar Vaga Completa (PUT)

```http
PUT /service/vagas/{id}/
```

**Permissões:**

- CR: Qualquer vaga
- Empresa: Apenas suas próprias vagas

Substitui todos os campos da vaga. Todos os campos obrigatórios devem ser enviados.

**Corpo:**

```json
{
  "nome": "Novo Nome",
  "descricao": "Nova descrição completa",
  "oportunidade": "estagio",
  "empresa_utilizador_auth_user_supabase_field": "uuid-da-empresa",
  "areas": [{ "nome": "Frontend" }, { "nome": "React" }]
}
```

**Resposta (200 OK):** Objeto atualizado

---

### 5. Atualizar Vaga Parcial (PATCH)

```http
PATCH /service/vagas/{id}/
```

**Permissões:**

- CR: Qualquer vaga
- Empresa: Apenas suas próprias vagas

Atualiza apenas os campos enviados.

**Exemplo - Atualizar nome:**

```json
{ "nome": "Nome Atualizado" }
```

**Exemplo - Atualizar áreas:**

```json
{
  "areas": [{ "nome": "Docker" }, { "nome": "Kubernetes" }]
}
```

**Resposta (200 OK):** Objeto atualizado

---

### 6. Eliminar Vaga

```http
DELETE /service/vagas/{id}/
```

**Permissões:**

- CR: Qualquer vaga
- Empresa: Apenas suas próprias vagas

**Resposta (204 No Content):** Sucesso, sem corpo

**Erros:**

- `404 Not Found` - Vaga não encontrada
- `403 Forbidden` - Sem permissão (não é dono da vaga ou role insuficiente)

---

## Códigos de Resposta

| Código | Significado                         |
| ------ | ----------------------------------- |
| 200    | Sucesso                             |
| 201    | Criado com sucesso                  |
| 204    | Eliminado com sucesso               |
| 400    | Erro de validação                   |
| 401    | Não autenticado (X-User-ID ausente) |
| 403    | Sem permissão para a ação           |
| 404    | Recurso não encontrado              |

---

## Exemplos de Erros

### 400 - Validação de campos obrigatórios

```json
{
  "nome": ["Este campo é obrigatório."],
  "oportunidade": ["Valor inválido. Deve ser: estagio, emprego, projeto"]
}
```

### 401 - Utilizador não autenticado

```json
{
  "detail": "Header X-User-ID não fornecido"
}
```

### 403 - Sem permissão

```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## Valores Válidos para Oportunidade

| Valor     | Descrição                          |
| --------- | ---------------------------------- |
| `estagio` | Estágio curricular ou profissional |
| `emprego` | Vaga de emprego efetivo            |
| `projeto` | Projeto temporário                 |

---

## Comportamento das Áreas

### Criação/Atualização

1. **Por nome:** Se a área não existir, será criada automaticamente
2. **Por ID:** Usa a área existente com o ID especificado
3. **Atualização:** Substitui todas as áreas anteriores pelas novas

### Resposta

As áreas são sempre retornadas com `id` e `nome`:

```json
"areas": [
    {"id": 1, "nome": "Python"},
    {"id": 2, "nome": "Django"}
]
```

---

## Filtros e Paginação

### Filtro "Minhas Vagas"

O parâmetro `?mine=true` filtra vagas onde:

```
vaga.empresa_utilizador_auth_user_supabase_field == request.user_id
```

Só retorna vagas da empresa associada ao utilizador logado.

---

### Filtros por Parâmetros de Query

A listagem de vagas suporta filtros avançados através de parâmetros de query:

#### Filtrar por Oportunidade

```http
GET /service/vagas/?oportunidade=estagio
```

**Comportamento:**

- Case-insensitive (iexact): `estagio`, `ESTAGIO`, `Estagio` funcionam igual
- Valores válidos: `estagio`, `emprego`, `projeto`

**Exemplos:**

```
/vagas/?oportunidade=EMPREGO     ✅ Funciona
/vagas/?oportunidade=emprego     ✅ Funciona
/vagas/?oportunidade=Emprego     ✅ Funciona
```

---

#### Filtrar por Área

```http
GET /service/vagas/?area=Python
```

**Comportamento:**

- Filtra pelo **nome** da área (não pelo ID)
- Case-insensitive: `python`, `PYTHON`, `Python` funcionam igual
- Suporta múltiplos valores separados por vírgula

**Exemplos:**

```
# Uma área
/vagas/?area=Python

# Múltiplas áreas (modo OR - padrão)
/vagas/?area=Python,Django,React

# Múltiplas áreas (modo AND)
/vagas/?area=Python,Django&area_match=and
```

---

#### Modo de Correspondência de Áreas

```http
GET /service/vagas/?area=Python,Django&area_match=and
```

| Valor | Descrição                                                   |
| ----- | ----------------------------------------------------------- |
| `or`  | (Padrão) Retorna vagas que têm **pelo menos uma** das áreas |
| `and` | Retorna vagas que têm **todas** as áreas especificadas      |

**Exemplos:**

```
# Vagas com Python OU Django
/vagas/?area=Python,Django

# Vagas com Python E Django (obrigatoriamente ambas)
/vagas/?area=Python,Django&area_match=and
```

---

#### Filtrar por Visualizações

```http
GET /service/vagas/?visualizacoes_min=100&visualizacoes_max=500
```

| Parâmetro           | Descrição                    |
| ------------------- | ---------------------------- |
| `visualizacoes_min` | Mínimo de visualizações (>=) |
| `visualizacoes_max` | Máximo de visualizações (<=) |

**Exemplos:**

```
# Vagas com pelo menos 100 visualizações
/vagas/?visualizacoes_min=100

# Vagas com no máximo 500 visualizações
/vagas/?visualizacoes_max=500

# Range de visualizações
/vagas/?visualizacoes_min=100&visualizacoes_max=500
```

---

#### Combinar Filtros

Todos os filtros podem ser combinados:

```http
GET /service/vagas/?oportunidade=estagio&area=Python,Django&area_match=and&visualizacoes_min=50
```

**Resultado:** Estágios que têm Python E Django, com pelo menos 50 visualizações.

---

### Paginação

A listagem de vagas é paginada automaticamente.

```http
GET /service/vagas/?page=1&page_size=10
```

| Parâmetro   | Padrão | Descrição                                       |
| ----------- | ------ | ----------------------------------------------- |
| `page`      | 1      | Número da página                                |
| `page_size` | 20     | Itens por página (máximo definido nas settings) |

**Resposta Paginada:**

```json
{
    "count": 150,
    "next": "http://localhost:8000/service/vagas/?page=2",
    "previous": null,
    "results": [
        { "id": 1, "nome": "Vaga 1", ... },
        { "id": 2, "nome": "Vaga 2", ... }
    ]
}
```

| Campo      | Descrição                                   |
| ---------- | ------------------------------------------- |
| `count`    | Total de vagas que correspondem aos filtros |
| `next`     | URL da próxima página (null se não houver)  |
| `previous` | URL da página anterior (null se não houver) |
| `results`  | Array de vagas da página atual              |

---

### Ordenação

A listagem suporta ordenação customizada:

```http
GET /service/vagas/?ordering=nome
```

| Parâmetro  | Padrão | Campos Disponíveis                            |
| ---------- | ------ | --------------------------------------------- |
| `ordering` | `id`   | `id`, `nome`, `visualizacoes`, `candidaturas` |

**Exemplos:**

```
# Ordenar por nome ascendente
/vagas/?ordering=nome

# Ordenar por visualizações descendente
/vagas/?ordering=-visualizacoes

# Ordenar por candidaturas descendente
/vagas/?ordering=-candidaturas
```

**Nota:** Prefixo `-` inverte a ordenação (descendente).

---

### Exemplo Completo

```http
GET /service/vagas/?oportunidade=estagio&area=Python&visualizacoes_min=10&ordering=-visualizacoes&page=1&page_size=5
```

**Resultado:**

- Apenas estágios
- Com área Python
- Com pelo menos 10 visualizações
- Ordenados por visualizações (mais populares primeiro)
- 5 itens por página

---

## Notas Importantes

1. **CR como Admin:** O role CR (código 0) tem permissões administrativas completas, podendo criar, editar e eliminar **qualquer vaga** do sistema.

2. **Empresas e Propriedade:** Empresas só podem editar/eliminar vagas onde o campo `empresa_utilizador_auth_user_supabase_field` corresponde ao seu `X-User-ID`. Tentativas de modificar vagas de outras empresas retornam 403.

3. **Verificação de Propriedade:** A verificação ocorre ao nível do objeto. Uma empresa pode aceder ao endpoint `/vagas/{id}/` com PUT/PATCH/DELETE, mas receberá 403 se a vaga não lhe pertencer.

4. **Criação de Vagas:** Ao criar uma vaga, a empresa deve passar o seu próprio UUID em `empresa_utilizador_auth_user_supabase_field` para depois poder editá-la.

5. **Áreas Automáticas:** Áreas passadas por nome são criadas automaticamente se não existirem.

6. **Filtro mine:** O filtro `mine=true` usa o UUID do header `X-User-ID` para filtrar.
