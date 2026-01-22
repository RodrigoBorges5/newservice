from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from .middleware import IsCompany, IsCR, IsStudent, IsCompanyOrReadOnly
from .models import Curriculo, Estudante, Vaga
from .serializers import CurriculoSerializer, VagaSerializer



def idex(request):
    return HttpResponse("You're at the service indexs.")

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
    
    Permissões: 
    - Student (role=2): Pode visualizar, criar, atualizar e deletar seu próprio CV
    """
    serializer_class = CurriculoSerializer
    
    queryset = Curriculo.objects.all()
    
    def get_permissions(self):
        """
        permissões baseadas na ação e role do usuário.

        
        IsStudent: Pode gerir o seu próprio CV. (GET, POST, DELETE em /curriculo/me/)
        

        """
        if self.action == 'get_my_cv':
            # Estudante acede ao seu próprio CV
            permission_classes = [IsStudent]
        else:
            # Bloquear acesso aos endpoints padrão do viewset
            permission_classes = []
               
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
            # Verificar UNIQUE constraint (T1.17) - estudante só pode ter 1 CV
            if Curriculo.objects.filter(
                estudante_utilizador_auth_user_supabase_field=estudante
            ).exists():
                return Response(
                    {
                        "detail": "Já existe um currículo associado a este estudante."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Adicionar estudante aos dados antes da serialização
            data = request.data.copy()
            data['estudante_utilizador_auth_user_supabase_field'] = estudante.utilizador_auth_user_supabase_field
            
            serializer = self.get_serializer(data=data)
            
            # Validação US-2.2 acontece no serializer
            try:
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                
                return Response(
                    {
                        "message": "Currículo submetido com sucesso! Aguarde validação da equipa CR.",
                        "data": serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {"detail": "Erro ao submeter currículo: deves aceitar."},
                    status=status.HTTP_400_BAD_REQUEST
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
            self.perform_destroy(curriculo)
            return Response(
                {"message": "Currículo eliminado com sucesso. Crie novo CV se desejar."},
                status=status.HTTP_204_NO_CONTENT
            )
        
        # GET - Retornar CV
        serializer = self.get_serializer(curriculo)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class VagaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de vagas.
    
    permissões:
    - Empresas (role=1): Podem criar, editar, apagar e listar vagas
    - CR (role=0) e Estudantes (role=2): Apenas podem listar vagas
    
    endpoints:
    - GET /vagas/ - Lista todas as vagas
    - GET /vagas/?mine=true - Lista apenas vagas da empresa logada
    - POST /vagas/ - Cria nova vaga (apenas empresas)
    - GET /vagas/{id}/ - Detalhes de uma vaga
    - PUT/PATCH /vagas/{id}/ - Atualiza vaga (apenas empresas)
    - DELETE /vagas/{id}/ - Remove vaga (apenas empresas)
    """
    queryset = Vaga.objects.all()
    serializer_class = VagaSerializer
    permission_classes = [IsCompanyOrReadOnly]
    
    def get_queryset(self):
        """
        Filtra vagas baseado em query params.
        
        Query params:
        - mine=true: Retorna apenas vagas da empresa logada
        """
        queryset = Vaga.objects.all()
        
        # Filtro "minhas vagas"
        mine = self.request.query_params.get('mine', None)
        if mine == 'true':
            # Filtra vagas pela empresa do user_id no header
            queryset = queryset.filter(
                empresa_utilizador_auth_user_supabase_field=self.request.user_id
            )
        
        return queryset
    