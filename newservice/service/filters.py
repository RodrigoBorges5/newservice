import django_filters
from django.db.models import Q
from .models import Estudante, AreaEstudante, Area


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
