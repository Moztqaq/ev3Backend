"""
URL configuration for petcare_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from gestion_clinica import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('api/', include('gestion_clinica.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('tutores/', views.registros, {'entidad': 'tutores'}, name='tutores'),
    path('mascotas/', views.registros, {'entidad': 'mascotas'}, name='mascotas'),
    path('citas/', views.registros, {'entidad': 'citas'}, name='citas'),
    path('fichas/', views.registros, {'entidad': 'fichas'}, name='fichas'),
    path('recordatorios/', views.registros, {'entidad': 'recordatorios'}, name='recordatorios'),
    path('mascotas/nueva/', views.nueva_mascota, name='nueva_mascota'),
    path('citas/nueva/', views.nueva_cita, name='nueva_cita'),
]
