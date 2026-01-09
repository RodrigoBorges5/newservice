from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Router para ViewSets
router = DefaultRouter()
router.register(r'curriculo', views.CurriculoViewSet, basename='curriculo')
urlpatterns = [
    path("", views.idex, name="idex"),
    path("teste/", views.teste.as_view(), name="test"),
    
    # Incluir rotas do router
   ]



urlpatterns += router.urls