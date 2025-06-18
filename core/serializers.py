from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from .models import UserProfile, EmergencyContact, KnownPerson # Asegúrate de importar todos los modelos que necesites serializar

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo UserProfile.
    Permite la visualización y edición del perfil de usuario.
    """
    class Meta:
        model = UserProfile
        fields = ('is_visually_impaired', 'created_at', 'updated_at') # Campos del perfil
        read_only_fields = ('created_at', 'updated_at')

class UserSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo User.
    Incluye el perfil del usuario de forma anidada.
    """
    profile = UserProfileSerializer(required=False) # El perfil es opcional al inicio, se puede crear/actualizar después

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile')
        read_only_fields = ('id',)

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializador para el registro de nuevos usuarios.
    Maneja la creación del User y su UserProfile asociado.
    Valida la contraseña y asegura que el email (si se provee) no esté ya en uso.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")
    is_visually_impaired = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 'is_visually_impaired')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': True} # Hacemos el email obligatorio para el registro
        }

    def validate(self, attrs):
        """
        Valida que las contraseñas coincidan.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def validate_email(self, value):
        """
        Valida que el email no esté ya en uso por otro usuario.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un usuario con este email ya existe.")
        return value
    
    def validate_username(self, value):
        """
        Valida que el nombre de usuario no esté ya en uso.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value

    @transaction.atomic # Asegura que la creación del usuario y el perfil sea atómica
    def create(self, validated_data):
        """
        Crea un nuevo objeto User y su UserProfile asociado.
        """
        is_visually_impaired = validated_data.pop('is_visually_impaired', False)
        validated_data.pop('password2') # No necesitamos guardar password2 en la BD
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        # Crea el perfil asociado
        UserProfile.objects.create(user=user, is_visually_impaired=is_visually_impaired)
        return user

# Serializador para EmergencyContact (T002)
class EmergencyContactSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo EmergencyContact.
    Permite crear, leer, actualizar y eliminar contactos de emergencia.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True) # El usuario se asigna automáticamente

    class Meta:
        model = EmergencyContact
        fields = ('id', 'user', 'name', 'phone_number', 'email', 'relationship', 'is_primary', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

# Serializador para KnownPerson (T007)
class KnownPersonSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo KnownPerson.
    Permite gestionar la información de personas conocidas.
    La codificación facial se manejará en la vista, aquí solo se expone el campo.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = KnownPerson
        fields = ('id', 'user', 'name', 'face_encoding', 'relationship', 'notes', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at') 