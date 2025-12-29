from django.urls import path

from . import views

urlpatterns = [
    path("", views.idex, name="idex"),
     path("teste/", views.teste.as_view(), name="test"),
]