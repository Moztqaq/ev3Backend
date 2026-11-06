# PetCare - Sistema de Gestión de Citas y Fichas Médicas para Veterinaria

## Descripción

PetCare es una aplicación web para apoyar la gestión diaria de una clínica veterinaria. Centraliza la información de tutores y mascotas, permite registrar citas y fichas médicas, y mantiene controles preventivos de vacunas y desparasitación.

El proyecto incluye:

- Modelos para tutores, mascotas, veterinarios, citas, fichas médicas y vacunas/controles.
- Validación de horarios para impedir el solapamiento de citas de un veterinario.
- Administración de datos mediante Django Admin.
- API REST con Django REST Framework para operaciones CRUD y alertas de controles próximos.
- Interfaz web con Django Templates y Bootstrap 5, con dashboard de citas y alertas.

## Requisitos y stack tecnológico

- Python 3.10 o superior.
- Django 6.1.
- Django REST Framework 3.18.
- PostgreSQL como motor previsto para despliegue.
- AWS EC2 para alojar la aplicación.
- Bootstrap 5 mediante CDN.

> **Configuración local:** actualmente `petcare_core/settings.py` usa SQLite para facilitar el desarrollo local. `psycopg2-binary` está incluido en `requirements.txt` para el uso de PostgreSQL, pero antes de desplegar en EC2 se deben configurar las credenciales y el motor de base de datos de forma segura, preferentemente mediante variables de entorno.

## Instalación y ejecución local

Abre PowerShell en la carpeta donde quieras guardar el proyecto y sigue estos pasos.

### 1. Clonar el repositorio

Reemplaza la URL de ejemplo por la URL real del repositorio:

```powershell
git clone <URL_DEL_REPOSITORIO>
cd ev3Backend
```

### 2. Crear y activar el entorno virtual

```powershell
py -m venv env
.\env\Scripts\Activate.ps1
```

Si PowerShell impide la activación por la política de ejecución, permite scripts para el usuario actual o ejecuta los comandos usando directamente `.\env\Scripts\python.exe`.

### 3. Instalar dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Aplicar migraciones

```powershell
python manage.py migrate
```

### 5. (Opcional) Crear un usuario administrador

```powershell
python manage.py createsuperuser
```

### 6. Iniciar el servidor de desarrollo

```powershell
python manage.py runserver
```

Visita <http://127.0.0.1:8000/> para el dashboard, <http://127.0.0.1:8000/admin/> para Django Admin y <http://127.0.0.1:8000/api/> para la API REST.

## Rutas principales

| Ruta | Descripción |
|---|---|
| `/` | Dashboard con citas del día y alertas preventivas |
| `/tutores/` | Listado de tutores |
| `/mascotas/` | Listado y registro de mascotas |
| `/citas/` | Listado y registro de citas |
| `/fichas/` | Fichas médicas |
| `/recordatorios/` | Vacunas y controles |
| `/api/` | API REST |
| `/api-auth/` | Login/logout navegable de Django REST Framework |
| `/admin/` | Administración de Django |

## Despliegue en AWS EC2

Para publicar el sistema, prepara una instancia EC2, instala una versión compatible de Python y PostgreSQL (local o como servicio administrado), configura las variables sensibles fuera del repositorio, aplica las migraciones y despliega la aplicación usando un servidor WSGI/ASGI y un servidor web apropiados. No utilices `runserver` como servidor de producción.

### IP Pública de AWS EC2

> **IP pública funcional:** `PENDIENTE DE ASIGNAR`
>
> Reemplaza este texto por la IP pública asignada a la instancia EC2 y confirma que la aplicación sea accesible desde ella. No se proporcionó una IP ni se verificó un despliegue en EC2 al preparar este README.

