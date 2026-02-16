import django_filters
from django.db.models import Q
from .models import Estudante, AreaEstudante, Area, Curriculo, Notification


class NotificationFilterSet(django_filters.FilterSet):
    """
    Filtros para o endpoint de notificações.

    Parâmetros de query suportados:
        - type: Tipo de notificação (cv_status_change, cv_feedback)
        - status: Estado de envio (sent, failed)
        - date_from: Data inicial (YYYY-MM-DD)
        - date_to: Data final (YYYY-MM-DD)
        - student: UUID do estudante (apenas para CR/Admin)
    """

    type = django_filters.CharFilter(
        field_name='type',
        lookup_expr='iexact',
        label='Tipo de notificação',
    )

    status = django_filters.CharFilter(
        field_name='status',
        lookup_expr='iexact',
        label='Estado de envio',
    )

    date_from = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__gte',
        label='Data inicial (YYYY-MM-DD)',
    )

    date_to = django_filters.DateFilter(
        field_name='created_at',
        lookup_expr='date__lte',
        label='Data final (YYYY-MM-DD)',
    )

    student = django_filters.UUIDFilter(
        field_name='recipient_user_id',
        label='UUID do estudante (apenas CR)',
    )

    class Meta:
        model = Notification
        fields = ['type', 'status', 'date_from', 'date_to', 'student']


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
