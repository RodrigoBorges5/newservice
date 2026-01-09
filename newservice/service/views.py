from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from .middleware import IsCompany, IsCR, IsStudent
from .models import Curriculo, Estudante
from .serializers import CurriculoSerializer

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
    - GET /api/curriculo/me/ - Retorna o CV do estudante autenticado
    - POST /api/curriculo/ - Cria um novo CV (apenas se share_aceites = TRUE)
    - GET /api/curriculo/{id}/ - Detalhes de um CV específico
    - PUT/PATCH /api/curriculo/{id}/ - Atualiza CV
    - DELETE /api/curriculo/{id}/ - Remove CV
    
    Permissões: Apenas estudantes (IsStudent)
    """
    serializer_class = CurriculoSerializer
    permission_classes = [IsStudent]
    queryset = Curriculo.objects.all()
    
    def get_queryset(self):
        """
        Filtra queryset para retornar apenas o CV do estudante autenticado.
        Estudantes só podem ver o seu próprio CV.
        """
        user_id = self.request.user_id
        
        try:
            estudante = Estudante.objects.get(
                utilizador_auth_user_supabase_field=user_id
            )
            return Curriculo.objects.filter(
                estudante_utilizador_auth_user_supabase_field=estudante
            )
        except Estudante.DoesNotExist:
            return Curriculo.objects.none()
    
    def get_serializer_context(self):
        """
        Adiciona request ao contexto do serializer para validação US-2.2.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get'], url_path='me')
    def get_my_cv(self, request):
        """
        GET /api/curriculo/me/
        
        Retorna o CV do estudante autenticado.
        Se não existir CV, retorna 404.
        """
        user_id = request.user_id
        
        try:
            estudante = Estudante.objects.get(
                utilizador_auth_user_supabase_field=user_id
            )
        except Estudante.DoesNotExist:
            return Response(
                {"detail": "Perfil de estudante não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            curriculo = Curriculo.objects.get(
                estudante_utilizador_auth_user_supabase_field=estudante
            )
            serializer = self.get_serializer(curriculo)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Curriculo.DoesNotExist:
            return Response(
                {"detail": "Currículo não encontrado. Por favor, submeta o seu CV."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def create(self, request, *args, **kwargs):
        """
        POST /api/curriculo/
        
        Cria um novo currículo para o estudante autenticado.
        
        Validações críticas (US-2.2):
        - Verificar se estudante.share_aceites = TRUE
        - Verificar UNIQUE constraint (apenas 1 CV por estudante)
        
        Returns:
            201 Created - CV criado com sucesso
            400 Bad Request - Validação falhou ou CV duplicado
            403 Forbidden - share_aceites = FALSE
        """
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
        
        # Verificar UNIQUE constraint (T1.17) - estudante só pode ter 1 CV
        if Curriculo.objects.filter(
            estudante_utilizador_auth_user_supabase_field=estudante
        ).exists():
            return Response(
                {
                    "detail": "Já existe um currículo associado a este estudante. "
                             "Use PUT/PATCH para atualizar o CV existente."
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
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    "message": "Currículo submetido com sucesso! Aguarde validação da equipa CR.",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        PUT/PATCH /api/curriculo/{id}/
        
        Atualiza o CV do estudante. Apenas o próprio estudante pode atualizar.
        """
        instance = self.get_object()
        
        # Verificar se o CV pertence ao estudante autenticado
        user_id = request.user_id
        try:
            estudante = Estudante.objects.get(
                utilizador_auth_user_supabase_field=user_id
            )
            
            if instance.estudante_utilizador_auth_user_supabase_field != estudante:
                return Response(
                    {"detail": "Não tem permissão para editar este currículo."},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Estudante.DoesNotExist:
            return Response(
                {"detail": "Perfil de estudante não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            "message": "Currículo atualizado com sucesso!",
            "data": serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/curriculo/{id}/
        
        Remove o CV do estudante.
        """
        instance = self.get_object()
        
        # Verificar se o CV pertence ao estudante autenticado
        user_id = request.user_id
        try:
            estudante = Estudante.objects.get(
                utilizador_auth_user_supabase_field=user_id
            )
            
            if instance.estudante_utilizador_auth_user_supabase_field != estudante:
                return Response(
                    {"detail": "Não tem permissão para eliminar este currículo."},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Estudante.DoesNotExist:
            return Response(
                {"detail": "Perfil de estudante não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        self.perform_destroy(instance)
        return Response(
            {"message": "Currículo eliminado com sucesso."},
            status=status.HTTP_204_NO_CONTENT
        )
    