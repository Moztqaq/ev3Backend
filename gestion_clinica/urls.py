from rest_framework.routers import DefaultRouter

from .views import (
    CitaViewSet,
    FichaMedicaViewSet,
    MascotaViewSet,
    TutorViewSet,
    VacunaControlViewSet,
    VeterinarioViewSet,
)

router = DefaultRouter()
router.register(r'tutores', TutorViewSet)
router.register(r'mascotas', MascotaViewSet)
router.register(r'veterinarios', VeterinarioViewSet)
router.register(r'citas', CitaViewSet)
router.register(r'fichas', FichaMedicaViewSet)
router.register(r'vacunas', VacunaControlViewSet)

urlpatterns = router.urls
