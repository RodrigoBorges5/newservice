from django.http import HttpResponse


def idex(request):
    return HttpResponse("You're at the service indexs.")