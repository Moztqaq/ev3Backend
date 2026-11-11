# PetCare

Sistema de gestión para una clínica veterinaria: tutores, mascotas, agenda,
fichas clínicas y controles preventivos.

## Funcionalidades

- Panel de atención con indicadores, citas del día y alertas preventivas.
- Búsqueda, filtros y paginación en las listas; alta y edición de registros.
- Administración de veterinarios desde la sección **Veterinarios**.
- Calendario mensual de citas.
- Historial por mascota y resumen imprimible que se puede guardar como PDF desde
  el navegador.
- Acceso de personal con cuenta de Django y portal de tutor limitado a las
  mascotas vinculadas a esa cuenta.
- API REST protegida para usuarios administradores/personal autorizado.
- Envío manual de recordatorios por correo cuando SMTP esté configurado.

WhatsApp no está conectado: requiere elegir proveedor, aportar credenciales y
configurar consentimiento y plantillas aprobadas. No se simulan envíos.

## Ejecución local

Requiere Python 3.12 o superior. En PowerShell:

```powershell
py -m venv env
.\env\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre <http://127.0.0.1:8000/> e inicia sesión con la cuenta del personal. Para
la configuración local, `.env.example` activa el modo de desarrollo. Revisa y
mantén `.env` fuera del control de versiones; nunca pongas credenciales reales
en `.env.example`.

### Vincular una cuenta del portal

1. Inicia sesión con una cuenta `is_staff` y abre `/admin/`.
2. Crea una cuenta de usuario para el tutor; déjala sin permisos de personal ni
   superusuario.
3. En el registro del tutor, asigna esa cuenta en el campo **Usuario**.
4. Entrega al tutor sus credenciales por un canal seguro.

Las cuentas nuevas no se vinculan automáticamente por correo o RUT. Esto evita
que alguien reclame datos clínicos de otra persona sin verificación por parte
de la clínica.

### Perfiles de veterinarios de demostración

Para poblar una base local con cinco perfiles ficticios (tres hombres y dos
mujeres), ejecuta:

```powershell
python manage.py seed_demo_veterinarios
```

El comando es idempotente y no reemplaza registros existentes. Sus RUT y
licencias llevan el prefijo `DEMO`; no representan profesionales reales y no
deben usarse para operación clínica.

## Configuración

Las opciones se leen desde variables de entorno o `.env`; la base local por
defecto es SQLite.

- `DJANGO_SECRET_KEY`: clave aleatoria privada, obligatoria para cualquier
  despliegue real.
- `DJANGO_DEBUG`: déjalo en `False` en producción.
- `DJANGO_ALLOWED_HOSTS`: nombres de dominio/IP que servirán la aplicación.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: orígenes HTTPS de la aplicación cuando aplique.
- `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` y
  `DB_SSLMODE`: conexión de PostgreSQL para producción.
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`,
  `EMAIL_USE_TLS` y `DEFAULT_FROM_EMAIL`: SMTP. Sin `EMAIL_HOST`, la acción de
  envío se bloquea y muestra que falta configuración.
- `DJANGO_SECURE_SSL_REDIRECT` y `DJANGO_SECURE_COOKIES`: actívalos detrás de
  HTTPS una vez que el proxy/servidor esté correctamente configurado.
- `DJANGO_SECURE_HSTS_SECONDS`: usa un valor de HSTS solo después de comprobar
  que todo el dominio sirve HTTPS correctamente.

El correo se envía manualmente desde la lista de recordatorios; no hay una tarea
programada ni mensajes de WhatsApp. Primero prueba SMTP con un buzón controlado.

## Despliegue

El servidor `runserver` es solo para desarrollo. Antes de publicar:

1. Usa PostgreSQL y un proveedor de despliegue/servidor WSGI apropiado.
2. Configura secretos y contraseñas en el gestor de secretos del proveedor, no
   en el repositorio ni en el navegador.
3. Configura HTTPS, hosts/orígenes, cookies seguras y archivos estáticos.
4. Ejecuta `python manage.py migrate` y `python manage.py collectstatic`.
5. Ejecuta `python manage.py check --deploy` y corrige todos los avisos.
6. Programa y prueba respaldos cifrados de la base de datos, y el procedimiento
   de restauración.
7. Define políticas de conservación, consentimiento y acceso para datos
   personales y médicos según la normativa aplicable.

Esta configuración no publica la aplicación ni reemplaza una revisión de
seguridad y privacidad previa a producción.

## Rutas

| Ruta | Uso |
|---|---|
| `/` | Panel del personal |
| `/cuentas/iniciar-sesion/` | Inicio de sesión |
| `/mi-cuenta/` | Portal de tutores vinculados |
| `/tutores/`, `/veterinarios/`, `/mascotas/`, `/citas/` | Gestión de registros |
| `/calendario/` | Agenda mensual |
| `/fichas/`, `/recordatorios/` | Historiales y controles |
| `/api/` | API REST restringida |
| `/admin/` | Administración de Django |

## Validación

```powershell
python manage.py check
python manage.py test gestion_clinica
python manage.py check --deploy
```
