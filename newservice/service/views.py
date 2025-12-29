from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .middleware import IsCompany,IsCR,IsStudent

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
    