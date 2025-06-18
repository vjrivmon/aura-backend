from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import EmergencyContact, KnownPerson, UserProfile # Asegúrate que UserProfile esté importado
from .serializers import (
    RegisterSerializer, 
    UserSerializer, 
    EmergencyContactSerializer, 
    KnownPersonSerializer
)

class RegisterView(generics.CreateAPIView):
    """
    Vista para registrar nuevos usuarios.
    Utiliza el RegisterSerializer para la validación y creación.
    Permite el acceso a cualquier usuario (autenticado o no) para registrarse.
    Devuelve los datos del usuario creado y los tokens de acceso y refresco.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data # Usamos UserSerializer para la respuesta

        return Response({
            "user": user_data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

# Más adelante, para T002: EmergencyContactViewSet
class EmergencyContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los Contactos de Emergencia.
    Permite operaciones CRUD (Crear, Leer, Actualizar, Eliminar).
    Los permisos aseguran que cada usuario solo pueda gestionar sus propios contactos.
    """
    serializer_class = EmergencyContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Este viewset solo debe devolver los contactos del usuario autenticado.
        """
        return EmergencyContact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Asigna automáticamente el usuario autenticado al crear un nuevo contacto.
        """
        serializer.save(user=self.request.user)

# Más adelante, para T007: KnownPersonViewSet
class KnownPersonViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las Personas Conocidas.
    Permite operaciones CRUD.
    Los permisos aseguran que cada usuario solo pueda gestionar sus propias personas conocidas.
    La lógica de codificación facial se manejará aquí en las acciones 'create' y 'update'.
    """
    serializer_class = KnownPersonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Este viewset solo debe devolver las personas conocidas por el usuario autenticado.
        """
        return KnownPerson.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Asigna automáticamente el usuario autenticado al crear una nueva persona conocida.
        Aquí se añadiría la lógica para procesar la imagen y generar el face_encoding.
        """
        # TODO: Implementar la lógica de procesamiento de imagen y obtención de face_encoding
        # Por ejemplo: image = self.request.data.get('face_image')
        # face_encoding_vector = process_image_to_get_encoding(image)
        # serializer.save(user=self.request.user, face_encoding=face_encoding_vector)
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Permite actualizar una persona conocida.
        Aquí se podría añadir lógica para re-procesar la imagen si se envía una nueva.
        """
        # TODO: Implementar lógica de actualización de face_encoding si se envía nueva imagen
        serializer.save()

# Los endpoints de reseteo de contraseña usualmente se manejan con librerías como
# django-rest-passwordreset o se implementan con vistas que envían emails.
# Por ahora, nos enfocamos en el registro y login.
