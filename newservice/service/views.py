from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, AllowAny
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .middleware import IsCompany, IsCR, IsStudent, VagaPermission, IsAll, IsCROrIsCompany, IsStudentOrCR
from .models import Curriculo, Estudante, Vaga, CVAccessLog, CV_STATUS_LABELS, Notification
from .serializers import CurriculoSerializer, VagaSerializer, CVSignedUrlSerializer, CVAccessLogSerializer, NotificationSerializer, NotificationReadSerializer
from .filters import CurriculoFilterSet
from service.services.storage_service import SupabaseStorageService
from service.services.cv_service import CVService
from service.services.exceptions import StorageUploadException, StorageSignedUrlException
from django.conf import settings
from django.db import transaction
from .filters import VagaFilterSet, NotificationFilterSet



def idex(request):
    return HttpResponse("You're at the service indexs.")


class AccessHistoryPagination(PageNumberPagination):
    """Paginação customizada para histórico de acessos - 50 registos por página."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class teste(APIView):
    permission_classes = [IsStudent]  # só students podem usar
    #permission_classes = [IsCompany] #só companies podem usar
    #permission_classes = [IsCR] #só CRs podem usar
    def get(self, request):
        return Response({
            "status": "ok",
            "user_id": request.user_id,
            "user_role": request.role
        })


class CurriculoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestão de currículos dos estudantes.
    
    Endpoints:
    - GET curriculo/me/ - Retorna o CV do estudante autenticado
    - POST curriculo/me/ - Cria um novo CV para o estudante autenticado
    - DELETE curriculo/me/ - Remove o CV do estudante autenticado
    - GET /curriculo/{id}/view/ - Visualiza CV com signed URL
    - GET /curriculo/{id}/access-history/ - Histórico de acessos (CR only)
    
    Filtros disponíveis (query params):
    - status: Status do CV (0=pendente, 1=aprovado, 2=rejeitado)
    - status_in: Múltiplos status (e.g., ?status_in=0&status_in=1)
    - validated_date_after: CVs validados após data (YYYY-MM-DD)
    - validated_date_before: CVs validados antes data (YYYY-MM-DD)
    - estudante_grau: Grau do estudante (case-insensitive)
    - estudante_grau_in: Múltiplos graus
    - estudante_ano_min: Ano de faculdade mínimo
    - estudante_ano_max: Ano de faculdade máximo
    - estudante_area: ID da área do estudante
    - estudante_area_nome: Nome da área do estudante (case-insensitive)
    
    Permissões: 
    - Student (role=2): Pode visualizar, criar, atualizar e deletar seu próprio CV
    - CR (role=0): Pode visualizar histórico de acessos
    """
    serializer_class = CurriculoSerializer
    queryset = Curriculo.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = CurriculoFilterSet
    
    def get_queryset(self):
        """
        Filtra queryset baseado no role do utilizador.
        
        - CR (role=0): Pode ver todos os CVs (status 0, 1, 2)
        - Empresa (role=1): Pode ver apenas CVs com status=1 (aprovados)
        - Estudante (role=2): Vê seu próprio CV via /me/
        """
        queryset = Curriculo.objects.all()
        user_role = getattr(self.request, 'role', None)
        
        # Empresa (1) só vê CVs aprovados
        if user_role == 1:
            queryset = queryset.filter(status=1)
        # CR (0) vê todos os CVs
        # Estudante (2) não deve chegar aqui (usa /me/)
        
        return queryset
    
    def get_permissions(self):
        """
        permissões baseadas na ação e role do usuário.

        
        IsStudent: Pode gerir o seu próprio CV. (GET, POST, DELETE em /curriculo/me/)
        IsAll: Qualquer utilizador pode fazer GET para ver vários CVs com filtros
        IsCR: Apenas CR pode ver histórico de acessos
        

        """
        if self.action == 'get_my_cv':
            # Estudante acede ao seu próprio CV
            permission_classes = [IsStudent]
        elif self.action == 'access_history':
            permission_classes = [IsCR]
        elif self.action in ['view_cv']:
            permission_classes = [IsAll]
        else:
            # GET para listar vários CVs com filtros
            permission_classes = [IsCROrIsCompany]
               
        return [permission() for permission in permission_classes]
       
        
    @action(detail=False, methods=['get', 'post', 'delete'], url_path='me')
    def get_my_cv(self, request):
        
        user_id = request.user_id
        
        # Verificar se estudante existe
        try:
            estudante = Estudante.objects.get(
                utilizador_auth_user_supabase_field=user_id
            )
        except Estudante.DoesNotExist:
            return Response(
                {"detail": "Perfil de estudante não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # POST - Criar novo CV
        if request.method == 'POST':

            file = request.FILES.get("cv")

            # validação do ficheiro
            if not file:
                return Response(
                    {"detail": "Ficheiro de currículo é obrigatório."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if file.content_type != settings.ALLOWED_MIME:
                return Response(
                    {"detail": "Apenas ficheiros PDF são permitidos."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
 
            # validação de tamanho
            if file.size > settings.MAX_FILE_SIZE:
                return Response(
                    {"detail": "O ficheiro excede o tamanho máximo de 5MB."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # upload para Supabase
            storage_service = SupabaseStorageService()
            bucket_name = "cvs"
            file_path = f"estudante_{user_id}/cv.pdf"

            try:
                storage_service.upload_file(
                    file=file,
                    bucket_name=bucket_name,
                    file_path=file_path,
                )
            except StorageUploadException:
                return Response(
                    {"detail": "Erro ao guardar o currículo."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            # criar/atualizar Curriculo
            try:
                with transaction.atomic():
                    # transação atómica
                    curriculo, _ = Curriculo.objects.update_or_create(
                        estudante_utilizador_auth_user_supabase_field=estudante,
                        defaults={
                            "file": file_path,
                            "status": 0,  # Pendente de validação
                        },
                    )
            except Exception:
                # rollback do storage
                storage_service.delete_file(
                    bucket_name=bucket_name,
                    file_path=file_path,
                )
                return Response(
                    {"detail": "Erro ao registar CV"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            
            return Response(
                {
                    "id": curriculo.id,
                    "file": file_path,
                    "status": curriculo.status,
                },
                status=status.HTTP_201_CREATED,
            )
        # GET e DELETE - Buscar CV existente
        try:
            curriculo = Curriculo.objects.get(
                estudante_utilizador_auth_user_supabase_field=estudante
            )
        except Curriculo.DoesNotExist:
            return Response(
                {"detail": "Currículo não encontrado. Por favor, submeta o seu CV."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # DELETE - Remover CV
        if request.method == 'DELETE':
            storage_service = SupabaseStorageService()
            bucket_name = "cvs"
            file_path = curriculo.file

            # tentar remover do storage (se existir)
            try:
                if file_path:
                    storage_service.delete_file(
                        bucket_name=bucket_name,
                        file_path=file_path,
                    )
            except Exception:
                return Response(
                    {"detail": "Erro ao remover o currículo do storage."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            # remover registo do BD
            self.perform_destroy(curriculo)
            return Response(
                {"message": "Currículo eliminado com sucesso. Crie novo CV se desejar."},
                status=status.HTTP_204_NO_CONTENT
            )
        
        # GET - Retornar CV (com signed_url se aprovado)
        serializer = self.get_serializer(curriculo)
        response_data = serializer.data
        
        # Adicionar mensagem baseada no status
        if curriculo.status == 0:
            response_data['message'] = "O seu currículo está pendente de validação."
        elif curriculo.status == 2:
            response_data['message'] = "O seu currículo foi rejeitado. Por favor, submeta um novo CV."
        elif curriculo.status == 1:
            # CV aprovado - adicionar signed_url
            cv_service = CVService()
            response_data['signed_url'] = cv_service.get_signed_url_for_curriculo(curriculo, user_id, request.role)
            response_data['expires_in_seconds'] = 900
            response_data['message'] = "O seu currículo está aprovado."
        
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='view')
    def view_cv(self, request, pk=None):
        """
        Endpoint para visualização segura de CVs com URL assinada.
        
        GET /curriculo/{id}/view/
        
        Permissões:
        - Empresa: pode visualizar CVs, status = 1
        - CR: pode visualizar todos os CVs
        - Estudante: deve usar /curriculo/me em vez disto
        
        Retorna:
        - JSON com signed_url + metadata do CV
        - URL válida por 15 minutos (900 segundos)
        
        """
        try:
            curriculo = self.get_object()
        except Curriculo.DoesNotExist:
            return Response(
                {"detail": "Não há currículo encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar permissões
        user_id = request.user_id
        user_role = request.role
        
        # Validar permissões baseado na role
        if user_role == 2:  # Estudante
            # Estudante deve usar /me/ para seu CV
            return Response(
                {"detail": "Estudantes devem usar /curriculo/me/ para visualizar seu CV."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        elif user_role == 1:  # Empresa
            # Empresa só pode ver CVs aprovados
            if curriculo.status != 1:
                return Response(
                    {"detail": "Apenas currículos aprovados podem ser visualizados. Este currículo está em estado: {status_label}.".format(
                        status_label=CV_STATUS_LABELS.get(curriculo.status, 'desconhecido')
                    )},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        elif user_role == 0:  # CR
            # CR pode ver todos
            pass
        
        else:
            return Response(
                {"detail": "Role não reconhecido."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Gerar response com signed URL via service
        cv_service = CVService()
        return cv_service.generate_signed_url_response(curriculo, user_id, user_role)

    @action(detail=True, methods=['get'], url_path='access-history')
    def access_history(self, request, pk=None):
        """
        Endpoint para visualizar histórico de acessos a um CV.
        
        GET /curriculo/{id}/access-history/
        
        Permissões:
        - CR (role=0): Pode visualizar histórico de qualquer CV
        
        Query params:
        - page: Número da página (padrão: 1)
        - page_size: Número de registos por página (padrão: 50, máximo: 100)
        
        Retorna:
        - JSON com lista paginada de acessos ao CV
        - Ordenado por accessed_at DESC (mais recentes primeiro)
        """
        # Verificar permissão - apenas CR pode acessar histórico
        if request.role != 0:  # 0 = CR
            return Response(
                {"detail": "CR visualiza o histórico de acessos."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verificar se CV existe
        try:
            curriculo = self.get_object()
        except Curriculo.DoesNotExist:
            return Response(
                {"detail": "Não há ´currículo encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obter logs ordenados por accessed_at DESC
        access_logs = CVAccessLog.objects.filter(
            curriculo=curriculo
        ).order_by('-accessed_at')
        
        # Aplicar paginação
        paginator = AccessHistoryPagination()
        paginated_logs = paginator.paginate_queryset(access_logs, request)
        
        if paginated_logs is not None:
            serializer = CVAccessLogSerializer(paginated_logs, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        # Fallback se a paginação falhar
        serializer = CVAccessLogSerializer(access_logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class VagaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de vagas.
    
    Permissões:
    - CR (role=0): CRUD completo (admin) - pode criar, editar, apagar e listar todas as vagas
    - Empresas (role=1): CRUD próprio - pode criar, editar, apagar apenas suas vagas
    - Estudantes (role=2): Apenas leitura - pode listar e ver detalhes das vagas
    
    Endpoints:
    - GET /vagas/ - Lista todas as vagas (paginado, ordenado por id)
    - GET /vagas/?mine=true - Lista apenas vagas da empresa logada
    - POST /vagas/ - Cria nova vaga (CR e Empresas)
    - GET /vagas/{id}/ - Detalhes de uma vaga
    - PUT/PATCH /vagas/{id}/ - Atualiza vaga (CR e Empresas, com verificação de propriedade)
    - DELETE /vagas/{id}/ - Remove vaga (CR e Empresas, com verificação de propriedade)
    
    Filtros (via query params):
    - oportunidade: tipo de oportunidade (case-insensitive) - estagio, emprego, projeto
    - area: nome(s) de área (case-insensitive) - ?area=Informatica&area=Marketing
    - area_match: modo de combinação de áreas - 'or' (default) ou 'and'
    - visualizacoes_min: mínimo de visualizações
    - visualizacoes_max: máximo de visualizações
    
    Paginação:
    - page: número da página (default: 1)
    - page_size: itens por página (default: 20)
    
    Ordenação:
    - Ordenado por id ascendente por padrão
    - Pode usar ?ordering=campo para alterar (ex: ?ordering=-id para descendente)
    """
    queryset = Vaga.objects.all().order_by('id')
    serializer_class = VagaSerializer
    permission_classes = [VagaPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = VagaFilterSet
    ordering_fields = ['id', 'nome', 'visualizacoes', 'candidaturas']
    ordering = ['id']  # Ordenação padrão
    
    def get_queryset(self):
        """
        Filtra vagas baseado em query params.
        
        Query params:
        - mine=true: Retorna apenas vagas da empresa logada
        
        Ordenação padrão: id ascendente
        """
        queryset = Vaga.objects.all().order_by('id')
        
        # Filtro "minhas vagas"
        mine = self.request.query_params.get('mine', None)
        if mine == 'true':
            # Filtra vagas pela empresa do user_id no header
            queryset = queryset.filter(
                empresa_utilizador_auth_user_supabase_field=self.request.user_id
            )
        
        return queryset


class NotificationPagination(PageNumberPagination):
    """Paginação para listagem de notificações - 20 por página."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para consulta e gestão de notificações do utilizador.

    Endpoints:
        GET  /curriculo/notifications/          - Lista notificações
        PATCH /curriculo/notifications/{id}/     - Marca notificação como lida

    Permissões:
        - Estudante (role=2): vê apenas as suas notificações.
        - CR (role=0): vê todas; pode filtrar por ``?student=<uuid>``.
        - Empresa (role=1): 403 Forbidden.

    Filtros (query params):
        - type: cv_status_change | cv_feedback
        - status: sent | failed
        - date_from: YYYY-MM-DD (data inicial)
        - date_to: YYYY-MM-DD (data final)
        - student: UUID do estudante (apenas CR)

    Ordenação:
        - Campos: created_at, updated_at, type, status
        - Padrão: -created_at (mais recentes primeiro)

    Paginação:
        - page: número da página (default: 1)
        - page_size: registos por página (default: 20, máximo: 100)
    """

    permission_classes = [IsStudentOrCR]
    pagination_class = NotificationPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = NotificationFilterSet
    ordering_fields = ['created_at', 'updated_at', 'type', 'status']
    ordering = ['-created_at']
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return NotificationReadSerializer
        return NotificationSerializer

    def get_queryset(self):
        """
        Filtra notificações com base no role do utilizador.

        - Estudante: ``recipient_user_id == request.user_id``
        - CR: todas; opcionalmente filtrado por ``?student=<uuid>``
        """
        role = getattr(self.request, 'role', None)
        user_id = getattr(self.request, 'user_id', None)

        if role == 2:
            # Estudante vê apenas as suas notificações
            return Notification.objects.filter(recipient_user_id=user_id)

        # CR (role=0) vê todas
        return Notification.objects.all()

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /curriculo/notifications/{id}/

        Apenas o campo ``read`` pode ser alterado. O estudante só pode
        atualizar as suas próprias notificações; CR pode atualizar qualquer uma.
        """
        instance = self.get_object()
        role = getattr(request, 'role', None)
        user_id = getattr(request, 'user_id', None)

        # Estudante só pode alterar as suas notificações
        if role == 2 and str(instance.recipient_user_id) != str(user_id):
            return Response(
                {"detail": "Não pode alterar notificações de outro utilizador."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)