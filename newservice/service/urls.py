from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Router para ViewSets
routercv = DefaultRouter()
routervaga = DefaultRouter()
routernotification = DefaultRouter()
routercv.register(r'curriculo', views.CurriculoViewSet, basename='curriculo')
routervaga.register(r'vagas', views.VagaViewSet, basename='vaga')
routernotification.register(r'curriculo/notifications', views.NotificationViewSet, basename='notification')
urlpatterns = [
    path("", views.idex, name="idex"),
    path("teste/", views.teste.as_view(), name="test"),
    
    # Incluir rotas do router
   ]



urlpatterns += routernotification.urls
urlpatterns += routercv.urls
urlpatterns += routervaga.urls