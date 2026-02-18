# T3.2: Adicionar Constantes de Estado ao Modelo Curriculo

## 📋 Informações da Task

**Sprint**: 3
**Dev Responsável**: Dev 1 (Backend Core)
**Dependências**: T3.1 (Migração campo `status` em `curriculo`)
**User Story Relacionada**: US-5.1, US-5.2 (Validação e Revisão de CV por CR)
**Requisito Funcional**: FR-4 (CR/Admin - Validação de CVs)

---

## 📝 Descrição

Adicionar constantes Python ao modelo `Curriculo` para representar os diferentes estados de validação de um CV. Estas constantes devem ser usadas em toda a aplicação para garantir consistência e evitar valores mágicos (magic numbers) no código.

### Objetivo

Criar uma abstração clara e type-safe para os estados de CV, facilitando a manutenção, legibilidade do código e prevenção de erros ao usar valores inválidos.

---

## ✅ Critérios de Aceitação

- **C1**: Constantes criadas no model `Curriculo`:
  - `CV_STATUS_PENDING = 0` (Pendente de validação)
  - `CV_STATUS_APPROVED = 1` (Aprovado pelo CR)
  - `CV_STATUS_REJECTED = 2` (Rejeitado pelo CR)
- **C2**: Constante `CV_STATUS_CHOICES` criada como tupla de tuplas para uso em forms/serializers:
  ```python
  CV_STATUS_CHOICES = [
      (0, 'Pendente'),
      (1, 'Aprovado'),
      (2, 'Rejeitado'),
  ]
  ```
- **C3**: Campo `status` do modelo usa `choices=CV_STATUS_CHOICES` para validação
- **C4**: Método helper `get_status_display()` funcional (fornecido automaticamente pelo Django)
- **C5**: Métodos de conveniência adicionados:
  - `is_pending()` → retorna `True` se status == 0
  - `is_approved()` → retorna `True` se status == 1
  - `is_rejected()` → retorna `True` se status == 2
- **C6**: Docstrings adicionadas explicando cada constante
- **C7**: Testes unitários criados validando:
  - Valores das constantes
  - Métodos helper funcionando corretamente
  - Atribuição de status inválido falha

---

## 🎯 Tasks Relacionadas

| Task | Descrição                                                  | Status  |
| ---- | ------------------------------------------------------------ | ------- |
| T3.1 | Migração: adicionar campo `status INTEGER DEFAULT 0`     | Blocked |
| T3.3 | Usar tabela `cr_curriculo` para histórico de validações | Blocked |
| T3.4 | Criar Serializer `CRReviewSerializer`                      | Blocked |
| T3.5 | Implementar endpoint `POST /api/cr/curriculo/{id}/review/` | Blocked |

---

## 📂 Estrutura de Ficheiros

```
newservice/
└── service/
    ├── models.py          ← ✏️ EDITAR (adicionar constantes)
    └── tests/
        └── test_models.py ← 🆕 CRIAR ou EDITAR
```

---

## 🔧 Implementação - Pseudo-código

```python
# service/models.py

from django.db import models

class Curriculo(models.Model):
    """Modelo para currículos de estudantes."""
  
    # ===== CONSTANTES DE ESTADO =====
    CV_STATUS_PENDING = 0
    CV_STATUS_APPROVED = 1
    CV_STATUS_REJECTED = 2
  
    CV_STATUS_CHOICES = [
        (CV_STATUS_PENDING, 'Pendente'),
        (CV_STATUS_APPROVED, 'Aprovado'),
        (CV_STATUS_REJECTED, 'Rejeitado'),
    ]
  
    # ===== CAMPOS =====
    id = models.AutoField(primary_key=True)
    file = models.BinaryField(null=True, blank=True)  # Deprecado - usar storage_path
    storage_path = models.CharField(max_length=500, null=True, blank=True)
    status = models.IntegerField(
        choices=CV_STATUS_CHOICES,
        default=CV_STATUS_PENDING,
        help_text="Estado de validação do CV"
    )
    descricao = models.TextField(null=True, blank=True)
    validated_date = models.DateField(null=True, blank=True)
    estudante = models.OneToOneField(
        'Estudante',
        on_delete=models.CASCADE,
        db_column='estudante_utilizador_auth_user_supabase__id'
    )
  
    class Meta:
        db_table = 'curriculo'
  
    # ===== MÉTODOS HELPER =====
    def is_pending(self) -> bool:
        """Verifica se CV está pendente de validação."""
        return self.status == self.CV_STATUS_PENDING
  
    def is_approved(self) -> bool:
        """Verifica se CV foi aprovado."""
        return self.status == self.CV_STATUS_APPROVED
  
    def is_rejected(self) -> bool:
        """Verifica se CV foi rejeitado."""
        return self.status == self.CV_STATUS_REJECTED
  
    def __str__(self):
        return f"CV {self.id} - {self.get_status_display()}"
```

---

## 🧪 Testes Esperados

```python
# service/tests/test_models.py

import pytest
from django.core.exceptions import ValidationError
from service.models import Curriculo, Estudante

class TestCurriculoStatusConstants:
    """Testes das constantes de estado do modelo Curriculo."""
  
    def test_status_constants_values(self):
        """Verifica valores das constantes."""
        assert Curriculo.CV_STATUS_PENDING == 0
        assert Curriculo.CV_STATUS_APPROVED == 1
        assert Curriculo.CV_STATUS_REJECTED == 2
  
    def test_status_choices_structure(self):
        """Verifica estrutura de CV_STATUS_CHOICES."""
        choices = Curriculo.CV_STATUS_CHOICES
        assert len(choices) == 3
        assert (0, 'Pendente') in choices
        assert (1, 'Aprovado') in choices
        assert (2, 'Rejeitado') in choices
  
    @pytest.mark.django_db
    def test_default_status_is_pending(self, estudante_factory):
        """Verifica que status default é Pendente."""
        estudante = estudante_factory()
        cv = Curriculo.objects.create(
            estudante=estudante,
            descricao="CV de teste"
        )
        assert cv.status == Curriculo.CV_STATUS_PENDING
        assert cv.is_pending()
  
    @pytest.mark.django_db
    def test_is_pending_helper(self, curriculo_factory):
        """Testa método is_pending()."""
        cv = curriculo_factory(status=Curriculo.CV_STATUS_PENDING)
        assert cv.is_pending() is True
        assert cv.is_approved() is False
        assert cv.is_rejected() is False
  
    @pytest.mark.django_db
    def test_is_approved_helper(self, curriculo_factory):
        """Testa método is_approved()."""
        cv = curriculo_factory(status=Curriculo.CV_STATUS_APPROVED)
        assert cv.is_pending() is False
        assert cv.is_approved() is True
        assert cv.is_rejected() is False
  
    @pytest.mark.django_db
    def test_is_rejected_helper(self, curriculo_factory):
        """Testa método is_rejected()."""
        cv = curriculo_factory(status=Curriculo.CV_STATUS_REJECTED)
        assert cv.is_pending() is False
        assert cv.is_approved() is False
        assert cv.is_rejected() is True
  
    @pytest.mark.django_db
    def test_get_status_display(self, curriculo_factory):
        """Testa método get_status_display() do Django."""
        cv_pending = curriculo_factory(status=Curriculo.CV_STATUS_PENDING)
        cv_approved = curriculo_factory(status=Curriculo.CV_STATUS_APPROVED)
        cv_rejected = curriculo_factory(status=Curriculo.CV_STATUS_REJECTED)
      
        assert cv_pending.get_status_display() == 'Pendente'
        assert cv_approved.get_status_display() == 'Aprovado'
        assert cv_rejected.get_status_display() == 'Rejeitado'
  
    @pytest.mark.django_db
    def test_invalid_status_raises_error(self, curriculo_factory):
        """Testa que status inválido não é aceite."""
        with pytest.raises(ValidationError):
            cv = curriculo_factory(status=999)
            cv.full_clean()  # Valida o modelo
  
    @pytest.mark.django_db
    def test_str_method_includes_status(self, curriculo_factory):
        """Testa método __str__ inclui status."""
        cv = curriculo_factory(status=Curriculo.CV_STATUS_APPROVED)
        str_repr = str(cv)
        assert 'Aprovado' in str_repr
        assert str(cv.id) in str_repr
```

---

## 📋 Checklist de Implementação

- [ ] Constantes `CV_STATUS_PENDING`, `CV_STATUS_APPROVED`, `CV_STATUS_REJECTED` adicionadas ao modelo
- [ ] Constante `CV_STATUS_CHOICES` criada com labels em português
- [ ] Campo `status` atualizado com `choices=CV_STATUS_CHOICES` e `default=CV_STATUS_PENDING`
- [ ] Método `is_pending()` implementado
- [ ] Método `is_approved()` implementado
- [ ] Método `is_rejected()` implementado
- [ ] Método `__str__()` atualizado para usar `get_status_display()`
- [ ] Docstrings adicionadas a todos os métodos
- [ ] Ficheiro `service/tests/test_models.py` criado ou atualizado
- [ ] Testes unitários passando (mínimo 8 testes)
- [ ] Migração Django criada (se necessário)
- [ ] Code review realizado
- [ ] CI/CD pipeline verde

---

## 🔗 Referências

- [Django Model Field Choices](https://docs.djangoproject.com/en/stable/ref/models/fields/#choices)
- [Django get_FOO_display()](https://docs.djangoproject.com/en/stable/ref/models/instances/#django.db.models.Model.get_FOO_display)
- [Python Constants Best Practices](https://peps.python.org/pep-0008/#constants)
- [pytest-django Documentation](https://pytest-django.readthedocs.io/)

---

## 📌 Notas Importantes

1. **Naming Convention**: Usar `UPPER_CASE_WITH_UNDERSCORES` para constantes (PEP 8)
2. **Type Safety**: Métodos helper retornam `bool` explicitamente
3. **Backwards Compatibility**: Manter valores numéricos (0, 1, 2) para compatibilidade com BD existente
4. **Enum Alternativo**: Considerar usar `IntegerChoices` do Django 3.0+ para maior type safety:
   ```python
   from django.db import models

   class CVStatus(models.IntegerChoices):
       PENDING = 0, 'Pendente'
       APPROVED = 1, 'Aprovado'
       REJECTED = 2, 'Rejeitado'
   ```
5. **Indexação**: Considerar adicionar índice ao campo `status` para queries de filtro eficientes:
   ```python
   status = models.IntegerField(
       choices=CV_STATUS_CHOICES,
       default=CV_STATUS_PENDING,
       db_index=True  # ← Adicionar índice
   )
   ```

---

## 🚀 Próximos Passos (Após Completar)

1. **T3.3**: Atualizar tabela `cr_curriculo` para usar constantes nos filtros
2. **T3.4**: Criar `CRReviewSerializer` usando `CV_STATUS_CHOICES` no campo de validação
3. **T3.5**: Implementar endpoint de review usando métodos helper (`is_pending()`, etc.)
4. **Refactor Global**: Substituir todos os valores mágicos (0, 1, 2) por constantes em:
   - Views
   - Serializers
   - Filtros
   - Templates (se houver)

---

**Criado em**: 3 Fevereiro 2026
**Versão**: 1.0
**Status**: 📋 Ready for Development
