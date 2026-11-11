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
from django.contrib.auth import views as auth_views
from django.urls import include, path

from gestion_clinica import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/iniciar-sesion/', views.PetCareLoginView.as_view(), name='login'),
    path('cuentas/cerrar-sesion/', auth_views.LogoutView.as_view(), name='logout'),
    path('cuentas/sin-acceso/', views.acceso_no_disponible, name='acceso_no_disponible'),
    path('', views.dashboard, name='dashboard'),
    path('api/', include('gestion_clinica.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('tutores/', views.registros, {'entidad': 'tutores'}, name='tutores'),
    path('veterinarios/', views.registros, {'entidad': 'veterinarios'}, name='veterinarios'),
    path('mascotas/', views.registros, {'entidad': 'mascotas'}, name='mascotas'),
    path('citas/', views.registros, {'entidad': 'citas'}, name='citas'),
    path('fichas/', views.registros, {'entidad': 'fichas'}, name='fichas'),
    path('recordatorios/', views.registros, {'entidad': 'recordatorios'}, name='recordatorios'),
    path('registros/<str:entidad>/nuevo/', views.editar_registro, name='registro_nuevo'),
    path('registros/<str:entidad>/<int:pk>/editar/', views.editar_registro, name='registro_editar'),
    path('calendario/', views.calendario, name='calendario'),
    path('mascotas/<int:pk>/', views.detalle_mascota, name='detalle_mascota'),
    path('mascotas/<int:pk>/imprimir/', views.imprimir_historial, name='imprimir_historial'),
    path('mi-cuenta/', views.portal_tutor, name='portal_tutor'),
    path('recordatorios/<int:pk>/enviar-correo/', views.enviar_recordatorio, name='enviar_recordatorio'),
    path('mascotas/nueva/', views.editar_registro, {'entidad': 'mascotas'}, name='nueva_mascota'),
    path('citas/nueva/', views.editar_registro, {'entidad': 'citas'}, name='nueva_cita'),
]
