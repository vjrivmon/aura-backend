from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, EmergencyContactViewSet, KnownPersonViewSet

# Creamos un router para los ViewSets
router = DefaultRouter()
router.register(r'emergency-contacts', EmergencyContactViewSet, basename='emergencycontact') # Para T002
router.register(r'known-persons', KnownPersonViewSet, basename='knownperson') # Para T007
# Aquí se registrarán más ViewSets a medida que los implementemos

app_name = 'core'

urlpatterns = [
    # Rutas de Autenticación
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    # Aquí podrías añadir en el futuro las URLs para password reset si las implementas manualmente
    # path('auth/password/reset/', PasswordResetView.as_view(), name='password_reset'),
    # path('auth/password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Rutas para los ViewSets registrados en el router
    path('', include(router.urls)),
    # Ejemplo: /api/emergency-contacts/
    # Ejemplo: /api/known-persons/
] 