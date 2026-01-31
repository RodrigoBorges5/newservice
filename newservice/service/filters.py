import django_filters
from django.db.models import Q
from .models import Estudante, AreaEstudante, Area, Curriculo
class EstudanteFilterSet(django_filters.FilterSet):
    
    
    # Filtro para grau - case-insensitive exato
    grau = django_filters.CharFilter(
        field_name='grau',
        lookup_expr='iexact',
        label='Grau (case-insensitive)'
    )
    
    # Filtro para múltiplos graus - via método customizado
    grau_in = django_filters.BaseInFilter(
        field_name='grau',
        lookup_expr='iexact',
        label='Graus (múltiplos valores)'
    )
    
    # Filtros para range de ano de faculdade
    ano_min = django_filters.NumberFilter(
        field_name='ano',
        lookup_expr='gte',
        label='Ano de faculdade mínimo (>=)'
    )
    
    ano_max = django_filters.NumberFilter(
        field_name='ano',
        lookup_expr='lte',
        label='Ano de faculdade máximo (<=)'
    )
    
    # Filtro para disponibilidade - aceita várias variações
    disponibilidade = django_filters.CharFilter(
        method='filter_disponibilidade',
        label='Disponibilidade (estágio, emprego, projeto)'
    )
    
    # Filtro para múltiplas disponibilidades
    disponibilidade_in = django_filters.BaseInFilter(
        field_name='disponibilidade',
        lookup_expr='iexact',
        label='Disponibilidades (múltiplos valores)'
    )
    
    # Filtro para área por ID
    area = django_filters.NumberFilter(
        method='filter_by_area_id',
        label='ID da Área'
    )
    
    # Filtro para área por nome - case-insensitive
    area_nome = django_filters.CharFilter(
        method='filter_by_area_name',
        label='Nome da Área (case-insensitive)'
    )
    
    class Meta:
        model = Estudante
        fields = []  # Não usamos os fields padrão, apenas os customizados
    
    def filter_disponibilidade(self, queryset, name, value):
        """
        Filtra por disponibilidade baseado em DISPONIBILIDADE_CHOICES.
        Valores válidos: 'estagio', 'emprego', 'projeto'
        
        Aceita variações:
        - exato: ?disponibilidade=estagio
        - case-insensitive: ?disponibilidade=ESTAGIO
        """
        if not value:
            return queryset
        
        value_lower = value.lower()
        
        # Validar contra as escolhas definidas no modelo
        valid_choices = [choice[0] for choice in Estudante.DISPONIBILIDADE_CHOICES]
        
        if value_lower in valid_choices:
            return queryset.filter(disponibilidade=value_lower)
        else:
            # Busca case-insensitive se não for correspondência exata
            return queryset.filter(disponibilidade__iexact=value)
    
    def filter_by_area_id(self, queryset, name, value):
        """
        Filtra estudantes que têm a área com o ID específico.
        """
        if value:
            return queryset.filter(
                areaestudante__area_id=value
            ).distinct()
        return queryset
    
    def filter_by_area_name(self, queryset, name, value):
        """
        Filtra estudantes que têm áreas com nome contendo value (case-insensitive).
        Suporta múltiplas áreas via repetição de parâmetro (e.g., ?area_nome=Info&area_nome=Dev).
        """
        if value:
            return queryset.filter(
                areaestudante__area__nome__icontains=value
            ).distinct()
        return queryset


class CurriculoFilterSet(django_filters.FilterSet):
    """
    FilterSet para Curriculo permitindo filtros avançados.
    
    Query params suportados:
    - status: Status do CV (0=pendente, 1=aprovado, 2=rejeitado)
    - status_in: Múltiplos status (e.g., ?status_in=0&status_in=1)
    - validated_date_after: CVs validados após data (YYYY-MM-DD)
    - validated_date_before: CVs validados antes data (YYYY-MM-DD)
    - estudante_grau: Grau do estudante (case-insensitive)
    - estudante_grau_in: Múltiplos graus (e.g., ?estudante_grau_in=Licenciatura&estudante_grau_in=Mestrado)
    - estudante_ano_min: Ano de faculdade mínimo (>=)
    - estudante_ano_max: Ano de faculdade máximo (<=)
    - estudante_area: ID da área do estudante
    - estudante_area_nome: Nome da área do estudante (case-insensitive, contém)
    """
    
    # Filtro para status - exact
    status = django_filters.NumberFilter(
        field_name='status',
        lookup_expr='exact',
        label='Status do CV (0=pendente, 1=aprovado, 2=rejeitado)'
    )
    
    # Filtro para múltiplos status
    status_in = django_filters.BaseInFilter(
        field_name='status',
        lookup_expr='exact',
        label='Múltiplos status'
    )
    
    # Filtros para range de validated_date
    validated_date_after = django_filters.DateFilter(
        field_name='validated_date',
        lookup_expr='gte',
        label='CV validado após data (YYYY-MM-DD)'
    )
    
    validated_date_before = django_filters.DateFilter(
        field_name='validated_date',
        lookup_expr='lte',
        label='CV validado antes de data (YYYY-MM-DD)'
    )
    
    # Filtros encadeados do Estudante - grau
    estudante_grau = django_filters.CharFilter(
        field_name='estudante_utilizador_auth_user_supabase_field__grau',
        lookup_expr='iexact',
        label='Grau do estudante (case-insensitive)'
    )
    
    estudante_grau_in = django_filters.BaseInFilter(
        field_name='estudante_utilizador_auth_user_supabase_field__grau',
        lookup_expr='iexact',
        label='Múltiplos graus do estudante'
    )
    
    # Filtros encadeados do Estudante - ano de faculdade
    estudante_ano_min = django_filters.NumberFilter(
        field_name='estudante_utilizador_auth_user_supabase_field__ano',
        lookup_expr='gte',
        label='Ano de faculdade mínimo (>=)'
    )
    
    estudante_ano_max = django_filters.NumberFilter(
        field_name='estudante_utilizador_auth_user_supabase_field__ano',
        lookup_expr='lte',
        label='Ano de faculdade máximo (<=)'
    )
    
    # Filtros encadeados do Estudante - área
    estudante_area = django_filters.NumberFilter(
        method='filter_by_estudante_area_id',
        label='ID da área do estudante'
    )
    
    estudante_area_nome = django_filters.CharFilter(
        method='filter_by_estudante_area_name',
        label='Nome da área do estudante (case-insensitive, contém)'
    )
    
    class Meta:
        model = Curriculo
        fields = []  # Não usamos os fields padrão, apenas os customizados
    
    def filter_by_estudante_area_id(self, queryset, name, value):
        """
        Filtra currículos de estudantes que têm a área com ID específico.
        """
        if value:
            return queryset.filter(
                estudante_utilizador_auth_user_supabase_field__areaestudante__area_id=value
            ).distinct()
        return queryset
    
    def filter_by_estudante_area_name(self, queryset, name, value):
        """
        Filtra currículos de estudantes que têm áreas com nome contendo value (case-insensitive).
        """
        if value:
            return queryset.filter(
                estudante_utilizador_auth_user_supabase_field__areaestudante__area__nome__icontains=value
            ).distinct()
        return queryset
