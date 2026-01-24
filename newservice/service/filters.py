import django_filters
from django.db.models import Q
from .models import Vaga, Area


class VagaFilterSet(django_filters.FilterSet):
    """
    FilterSet para o modelo Vaga.
    
    Filtros disponíveis:
    - oportunidade: filtro case-insensitive (estagio, emprego, projeto)
    - area: filtro por nome de área (case-insensitive, suporta múltiplos: ?area=Informatica&area=Marketing)
    - visualizacoes_min: visualizações >= valor
    - visualizacoes_max: visualizações <= valor
    - area_match: modo de combinação de áreas ('and' ou 'or', default: 'or')
    
    Exemplos:
    - /vagas/?oportunidade=estagio
    - /vagas/?oportunidade=ESTAGIO (case-insensitive)
    - /vagas/?area=Informatica&area=Marketing (vagas com área Informatica OU Marketing)
    - /vagas/?area=Informatica&area=Marketing&area_match=and (vagas com AMBAS as áreas)
    - /vagas/?oportunidade=estagio&area=Informatica (combinação de filtros)
    - /vagas/?visualizacoes_min=100&visualizacoes_max=500
    """
    
    # Filtro de oportunidade (case-insensitive)
    oportunidade = django_filters.CharFilter(
        method='filter_oportunidade_iexact',
        help_text="Tipo de oportunidade (case-insensitive): estagio, emprego, projeto"
    )
    
    # Filtro de área por nome (case-insensitive, múltiplos valores)
    area = django_filters.CharFilter(
        method='filter_by_area_names',
        help_text="Nome(s) de área (case-insensitive). Múltiplos: ?area=Informatica&area=Marketing"
    )
    
    # Filtro de visualizações (intervalo)
    visualizacoes_min = django_filters.NumberFilter(
        field_name='visualizacoes',
        lookup_expr='gte',
        help_text="Visualizações mínimas"
    )
    
    visualizacoes_max = django_filters.NumberFilter(
        field_name='visualizacoes',
        lookup_expr='lte',
        help_text="Visualizações máximas"
    )
    
    # Modo de combinação de áreas (AND/OR)
    area_match = django_filters.ChoiceFilter(
        choices=[('or', 'OR'), ('and', 'AND')],
        method='filter_area_match_mode',
        help_text="Modo de combinação de áreas: 'or' (default) ou 'and'"
    )
    
    class Meta:
        model = Vaga
        fields = ['oportunidade', 'area']
    
    def filter_oportunidade_iexact(self, queryset, name, value):
        """
        Filtra vagas por oportunidade (case-insensitive).
        Aceita: estagio, ESTAGIO, Estagio, etc.
        """
        if not value:
            return queryset
        
        return queryset.filter(oportunidade__iexact=value)
    
    def filter_by_area_names(self, queryset, name, value):
        """
        Filtra vagas por nome(s) de área (case-insensitive).
        Suporta múltiplos valores via ?area=X&area=Y
        O modo (AND/OR) é determinado pelo parâmetro area_match.
        """
        if not value:
            return queryset
        
        # Obtém todos os valores do parâmetro 'area' (múltiplos)
        area_names = self.data.getlist('area') if hasattr(self.data, 'getlist') else [value]
        
        if not area_names:
            return queryset
        
        # Obtém o modo de match (default: OR)
        area_match = self.data.get('area_match', 'or').lower()
        
        if area_match == 'and':
            # AND: vaga deve ter TODAS as áreas especificadas
            for area_name in area_names:
                queryset = queryset.filter(vagaarea__area__nome__iexact=area_name)
            return queryset.distinct()
        else:
            # OR (default): vaga deve ter PELO MENOS UMA das áreas
            q_objects = Q()
            for area_name in area_names:
                q_objects |= Q(vagaarea__area__nome__iexact=area_name)
            return queryset.filter(q_objects).distinct()
    
    def filter_area_match_mode(self, queryset, name, value):
        """
        Este filtro não altera o queryset diretamente.
        O valor é usado em filter_by_area_names para determinar o modo.
        """
        return queryset
