from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from .middleware import IsCompany, IsCR, IsStudent, IsCompanyOrReadOnly
from .models import Vaga
from .serializers import VagaSerializer

def idex(request):
    return HttpResponse("You're at the service indexs.")

class teste(APIView):
    permission_classes = [IsStudent] #só students podem usar
    #permission_classes = [IsCompany] #só companies podem usar
    #permission_classes = [IsCR] #só CRs podem usar
    def get(self, request):
        return Response({
            "status": "ok",
            "user_id": request.user_id,
            "user_role": request.role
        })


class VagaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de vagas.
    
    permissões:
    - Empresas (role=1): Podem criar, editar, apagar e listar vagas
    - CR (role=0) e Estudantes (role=2): Apenas podem listar vagas
    
    endpoints:
    - GET /vagas/ - Lista todas as vagas
    - POST /vagas/ - Cria nova vaga (apenas empresas)
    - GET /vagas/{id}/ - Detalhes de uma vaga
    - PUT/PATCH /vagas/{id}/ - Atualiza vaga (apenas empresas)
    - DELETE /vagas/{id}/ - Remove vaga (apenas empresas)
    """
    queryset = Vaga.objects.all()
    serializer_class = VagaSerializer
    permission_classes = [IsCompanyOrReadOnly]
    