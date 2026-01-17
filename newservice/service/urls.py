from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# configurar router para ViewSets (cria as rotas automaticamente)
router = DefaultRouter()
router.register(r'vagas', views.VagaViewSet, basename='vaga')

urlpatterns = [
    path("", views.idex, name="idex"),
    path("teste/", views.teste.as_view(), name="test"),
    path("", include(router.urls)),  # Adiciona rotas do router
]