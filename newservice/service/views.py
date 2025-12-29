from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response

def idex(request):
    return HttpResponse("You're at the service indexs.")

class teste(APIView):
    def get(self, request):
        return Response({
            "status": "ok",
            "user_id": request.user_id
        })