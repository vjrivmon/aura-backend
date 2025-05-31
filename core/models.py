from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class EmergencyContact(models.Model):
    """
    Modelo para almacenar contactos de emergencia para un usuario.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="emergency_contacts",
        verbose_name="Usuario"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Nombre del Contacto"
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name="Número de Teléfono",
        help_text="Número de teléfono del contacto de emergencia."
    )
    email = models.EmailField(
        max_length=255,
        blank=True, 
        null=True,
        verbose_name="Correo Electrónico"
    )
    relationship = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Relación",
        help_text="Ej: Hijo, Amigo, Familiar."
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name="Contacto Principal",
        help_text="Marcar si este es el contacto principal para notificaciones SOS."
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Contacto de Emergencia"
        verbose_name_plural = "Contactos de Emergencia"
        ordering = ["user", "-is_primary", "name"] # Ordena por usuario, luego primario, luego nombre

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class KnownPerson(models.Model):
    """
    Modelo para almacenar información sobre personas conocidas por el usuario,
    incluyendo su codificación facial para reconocimiento.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="known_persons",
        verbose_name="Usuario"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Nombre de la Persona"
    )
    face_encoding = models.TextField(
        blank=True, 
        verbose_name="Codificación Facial",
        help_text="Representación vectorial de la cara para reconocimiento."
    )
    relationship = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Relación",
        help_text="Ej: Familiar, Amigo, Colega."
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notas Adicionales"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Persona Conocida"
        verbose_name_plural = "Personas Conocidas"
        ordering = ["user", "name"]

    def __str__(self):
        return f"{self.name} (Conocido de {self.user.username})"

# Test comment to trigger change detection
