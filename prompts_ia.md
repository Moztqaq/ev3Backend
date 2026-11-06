# Registro de prompts de IA — PetCare

## Herramienta utilizada

- **GitHub Copilot / VS Code Agent**, asistente de programación integrado en VS Code.

## Registro cronológico de prompts

### 1. Configuración de aplicaciones

> Modifica mi archivo `petcare_core/settings.py`. En la lista `INSTALLED_APPS`, agrega `'rest_framework'` y `'gestion_clinica'` respetando las aplicaciones que ya vienen por defecto.

### 2. Modelado de datos y lógica de citas

> Actúa como desarrollador backend en Django. En el archivo `gestion_clinica/models.py`, crea los modelos para el proyecto **PetCare: Sistema de Gestión de Citas y Fichas Médicas para Veterinaria**:
>
> 1. **Tutor**: nombre, apellido, rut (único), teléfono, correo, dirección y fecha de registro.
> 2. **Mascota**: foreign key a Tutor con CASCADE, nombre, especie (choices: canino, felino, exótico, otro), raza, sexo (choices: macho, hembra), fecha de nacimiento y peso en kg.
> 3. **Veterinario**: OneToOne con User de Django (opcional), nombre, apellido, rut (único), licencia médica (única) y especialidad.
> 4. **Cita**: foreign keys a Mascota y Veterinario, fecha, hora de inicio, hora de fin, motivo y estado (Pendiente, Realizada, Cancelada). **Implementa en el método clean() una validación de negocio para evitar el solapamiento de horas en un mismo veterinario y fecha**.
> 5. **FichaMedica**: foreign key a Mascota y Veterinario, OneToOne opcional a Cita, fecha de atención, motivo de consulta, diagnóstico, tratamiento, receta médica y exámenes clínicos.
> 6. **VacunaControl**: foreign key a Mascota, tipo (Vacuna, Desparasitación, Control), nombre del procedimiento, fecha de aplicación, fecha de próximo control y observaciones.
>
> Incluye métodos `__str__` y las importaciones necesarias (`ValidationError`, `timezone`, etc.).

### 3. Administración de modelos

> Actúa como desarrollador backend en Django. En `gestion_clinica/admin.py`, registra todos los modelos creados de PetCare usando decoradores `@admin.register`. Personaliza cada modelo para cumplir con la rúbrica de evaluación: incluye `list_display`, filtros con `list_filter`, campos de búsqueda con `search_fields` y añade inlines (`TabularInline`) para ver las mascotas asociadas dentro de cada Tutor y las vacunas dentro de cada Mascota.

### 4. API REST con Django REST Framework

> Actúa como desarrollador backend en Django. Necesito implementar la API REST completa con Django REST Framework para el proyecto PetCare, cubriendo los requerimientos de la evaluación:
>
> 1. **Serializers (`gestion_clinica/serializers.py`):**
>    - Crea `ModelSerializer` para cada modelo: `TutorSerializer`, `MascotaSerializer`, `VeterinarioSerializer`, `CitaSerializer`, `FichaMedicaSerializer` y `VacunaControlSerializer`.
>    - En `CitaSerializer`, valida que la hora de término sea mayor a la de inicio y reutiliza la validación para evitar solapamiento de horarios en un mismo veterinario y fecha.
> 2. **ViewSets (`gestion_clinica/views.py`):**
>    - Crea `viewsets.ModelViewSet` para cada una de las entidades con operaciones CRUD completas.
>    - Añade permisos para permitir lectura y restringir escrituras si es necesario (`permissions.IsAuthenticatedOrReadOnly`).
>    - En `VacunaControlViewSet`, agrega un método `@action(detail=False, methods=['get'])` llamado `alertas_pendientes` que filtre y retorne las vacunas o controles cuya fecha de vencimiento sea hoy o dentro de los próximos 7 días, cumpliendo con la regla de negocio de recordatorios preventivos.
> 3. **Rutas de la API (`gestion_clinica/urls.py`):** configura un `DefaultRouter` para tutores, mascotas, veterinarios, citas, fichas y vacunas.
> 4. **URLs principales (`petcare_core/urls.py`):** incluye `gestion_clinica.urls` bajo `api/` y la ruta para el login de DRF bajo `api-auth/`.

### 5. Interfaz web con Django Templates y Bootstrap

> Actúa como desarrollador frontend y backend en Django. Necesito crear la interfaz visual para PetCare con Django Templates y Bootstrap 5 (CDN):
>
> 1. Configura la carpeta `templates/` y `static/` si es necesario.
> 2. Crea `templates/base.html` con un navbar responsivo y enlaces a Inicio/Dashboard, Tutores, Mascotas, Citas, Fichas Médicas y Recordatorios.
> 3. Crea `templates/dashboard.html` como vista principal (`/`), con una tabla de citas del día y badges de estado, además de alertas preventivas para vacunas o controles próximos a vencer o vencidos.
> 4. Crea ModelForms para Tutor, Mascota, Cita y FichaMedica.
> 5. Agrega vistas para renderizar el dashboard y registrar una cita médica y una mascota.
> 6. Vincula las rutas y asegúrate de que la raíz cargue `dashboard.html`.

### 6. Documentación del historial de prompts

> Genera un archivo en la raíz del proyecto llamado `prompts_ia.md`.
>
> Debe tener una estructura limpia en Markdown detallando:
>
> 1. Herramienta utilizada (GitHub Copilot / VS Code Agent).
> 2. Registro cronológico de prompts utilizados para modelado, lógica de citas, Django Admin, API DRF e interfaz web.
> 3. Sección de validación humana: explicación técnica de cómo se auditaron y ejecutaron las migraciones y pruebas en el navegador.

## Validación humana y técnica

### Migraciones

- Se generó la migración inicial de `gestion_clinica` con `manage.py makemigrations gestion_clinica`.
- Se inspeccionó `gestion_clinica/migrations/0001_initial.py` para confirmar que incluyera los seis modelos y sus relaciones.
- Se ejecutó `manage.py makemigrations --check --dry-run`; Django respondió **“No changes detected”**, lo cual confirma que los modelos y la migración están sincronizados.
- No se ejecutó `manage.py migrate` durante esta sesión; por tanto, no se afirma aquí que la migración se haya aplicado a la base de datos local.

### Pruebas y comprobaciones

- `manage.py check` terminó sin errores.
- `manage.py test gestion_clinica` ejecutó **7 pruebas**, todas aprobadas. Cubren la validación de horarios de citas y sus solapamientos, las alertas preventivas y las vistas web para dashboard, registros y listados.
- Se intentó ejecutar `manage.py show_urls` para inspeccionar las rutas, pero el comando no está instalado en el proyecto. El sistema de comprobaciones de Django pasó correctamente.

### Revisión en navegador

- No se realizó una prueba visual automatizada ni se confirmó una sesión de navegador compartida durante esta validación.
- Para completar la revisión manual, iniciar el servidor con `manage.py runserver` y comprobar `/`, `/tutores/`, `/mascotas/`, `/citas/`, `/fichas/` y `/recordatorios/`. También conviene probar los formularios de alta, verificar los badges de estado y confirmar que las alertas distingan controles vencidos de los próximos a vencer.
