# CRReview Serializers

Documentação dos serializers utilizados para validação e resposta do fluxo de review de currículos por CR.

---

## 1. CRReviewSerializer

### Descrição

Serializer de entrada utilizado para validar e criar reviews de currículos pelo CR.

### Campos

| Campo          | Tipo                  | Obrigatório | Descrição                                                                                             |
| -------------- | --------------------- | ----------- | ----------------------------------------------------------------------------------------------------- |
| `curriculo_id` | IntegerField          | Sim         | ID do currículo a ser avaliado. Deve existir e estar em estado "pendente".                            |
| `status`       | ChoiceField           | Sim         | Novo status do currículo: `1` (aprovado) ou `2` (rejeitado).                                          |
| `feedback`     | CharField             | Não         | Comentário do CR. Obrigatório se `status=2` (rejeitado). Pode ser `null` ou string vazia se aprovado. |
| `review_date`  | DateField (read-only) | Não         | Data da validação, preenchida automaticamente durante a criação.                                      |

### Validações

* `curriculo_id`:

  * Verifica se o currículo existe.
  * Verifica se o currículo está em estado pendente.
* `validate()`:

  * Se `status=2` (rejeitado), `feedback` é obrigatório.
  * Não permite retornar para `status=0` (pendente).
  * Apenas permite `status=1` (aprovado) ou `status=2` (rejeitado).

### Método create()

* Recebe `validated_data`.
* Busca a instância do currículo (`Curriculo`) pelo `curriculo_id`.
* Busca a instância do CR (`Cr`) a partir do `request.user`.
* Atualiza o status do currículo chamando:

  * `curriculo.approve()` se aprovado.
  * `curriculo.reject(feedback)` se rejeitado.
* Cria um registro de review (`CrCurriculo`) com feedback e `review_date`.
* Retorna a instância criada de `CrCurriculo`.

---

## 2. CRReviewResponseSerializer

### Descrição

Serializer de saída utilizado para retornar os dados da review criada de forma legível.

### Campos

| Campo          | Tipo                  | Descrição                                                                              |
| -------------- | --------------------- | -------------------------------------------------------------------------------------- |
| `curriculo_id` | IntegerField          | ID do currículo avaliado.                                                              |
| `status`       | SerializerMethodField | Status do currículo com label legível (`"Aprovado pelo CR"` ou `"Rejeitado pelo CR"`). |
| `feedback`     | CharField             | Comentário fornecido pelo CR.                                                          |
| `review_date`  | DateField             | Data em que a validação foi realizada.                                                 |
| `validated_by` | CharField             | Nome do CR que realizou a validação.                                                   |

### Observações

* O campo `status` é calculado pelo método `get_status()` chamando `curriculo.get_status_display()`.
* Os dados são derivados do objeto `CrCurriculo` passado ao serializer.
* Não realiza nenhuma lógica de criação ou alteração de dados.

---

## 3. Exemplo de uso no endpoint

```python
# Serializer de entrada
serializer = CRReviewSerializer(
    data=request.data,
    context={"request": request}
)
serializer.is_valid(raise_exception=True)
review = serializer.save()

# Serializer de saída
response_serializer = CRReviewResponseSerializer(review)
return Response(response_serializer.data)
```

### Exemplo de payload de request

```json
{
  "curriculo_id": 12,
  "status": 2,
  "feedback": "Faltam informações sobre experiências anteriores"
}
```

### Exemplo de resposta

```json
{
  "curriculo_id": 12,
  "status": "Rejeitado pelo CR",
  "feedback": "Faltam informações sobre experiências anteriores",
  "review_date": "2024-11-28",
  "validated_by": "Ana Martins"
}
```

---

## 4. Regras de negócio principais

1. Apenas currículos **pendentes** podem ser validados.
2. Feedback é **obrigatório se rejeitado**.
3. Status inválidos ou voltar a pendente são bloqueados.
4. A atualização de status do currículo é feita via métodos do model (`approve()` / `reject()`), mantendo a lógica centralizada.
