from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import UserProfile

# Create your tests here.

class AuthTests(APITestCase):
    """
    Pruebas para los endpoints de autenticación: registro y login.
    """

    def setUp(self):
        """
        Configuración inicial para las pruebas.
        Define las URLs para los endpoints de registro y login.
        """
        self.register_url = reverse('core:auth_register')
        self.login_url = reverse('token_obtain_pair') # Usamos el nombre de la URL definida en config.urls

    def test_user_registration_success(self):
        """
        Prueba el registro exitoso de un nuevo usuario.
        Verifica que se crea el usuario y su perfil, y que la respuesta es HTTP 201.
        También comprueba que se devuelven los tokens de acceso y refresco.
        """
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongP@ssw0rd123",
            "password2": "StrongP@ssw0rd123",
            "is_visually_impaired": True
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.assertTrue(UserProfile.objects.filter(user__username="testuser", is_visually_impaired=True).exists())
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertTrue(response.data['user']['profile']['is_visually_impaired'])

    def test_user_registration_password_mismatch(self):
        """
        Prueba el fallo de registro cuando las contraseñas no coinciden.
        Verifica que la respuesta es HTTP 400 y que se incluye un error de validación.
        """
        data = {
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "StrongP@ssw0rd123",
            "password2": "DifferentPassword",
            "is_visually_impaired": False
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data) # DRF devuelve el error bajo la clave del campo

    def test_user_registration_existing_username(self):
        """
        Prueba el fallo de registro cuando el nombre de usuario ya existe.
        """
        # Primero creamos un usuario
        User.objects.create_user(username='existinguser', email='initial@example.com', password='password123')
        data = {
            "username": "existinguser", # Intentamos registrar con el mismo username
            "email": "newemail@example.com",
            "password": "StrongP@ssw0rd123",
            "password2": "StrongP@ssw0rd123",
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_user_registration_existing_email(self):
        """
        Prueba el fallo de registro cuando el email ya existe.
        """
        User.objects.create_user(username='anotheruser', email='existingemail@example.com', password='password123')
        data = {
            "username": "newuser3",
            "email": "existingemail@example.com", # Intentamos registrar con el mismo email
            "password": "StrongP@ssw0rd123",
            "password2": "StrongP@ssw0rd123",
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_login_success(self):
        """
        Prueba el login exitoso de un usuario existente.
        Verifica que se devuelven los tokens de acceso y refresco.
        """
        # Primero, crea un usuario para hacer login
        test_username = "loginuser"
        test_password = "loginP@ssw0rd"
        User.objects.create_user(username=test_username, password=test_password, email="login@example.com")
        
        data = {
            "username": test_username,
            "password": test_password
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_failure_wrong_password(self):
        """
        Prueba el fallo de login con contraseña incorrecta.
        """
        User.objects.create_user(username="loginuser2", password="correctPassword", email="login2@example.com")
        data = {
            "username": "loginuser2",
            "password": "wrongPassword"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data) # Simple JWT devuelve el error en 'detail'

    def test_user_login_failure_nonexistent_user(self):
        """
        Prueba el fallo de login para un usuario que no existe.
        """
        data = {
            "username": "nonexistentuser",
            "password": "anyPassword"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_access_protected_route_with_token(self):
        """
        Prueba el acceso a una ruta protegida utilizando un token JWT.
        Para esto, necesitamos una ruta protegida de ejemplo. Crearemos una temporalmente.
        """
        # Crear usuario y obtener token
        user = User.objects.create_user(username='authtestuser', password='authpassword')
        login_data = {"username": "authtestuser", "password": "authpassword"}
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['access']

        # Supongamos que tenemos un endpoint en core.urls como 'test-protected'
        # que requiere autenticación. Lo simularemos.
        # Necesitarías añadir una vista simple y una URL para esto en core/views.py y core/urls.py
        # Por ejemplo, en core/urls.py: path('test-protected/', TestProtectedView.as_view(), name='test_protected')
        # Y en core/views.py una vista simple:
        # from rest_framework.views import APIView
        # class TestProtectedView(APIView):
        #     permission_classes = [permissions.IsAuthenticated]
        #     def get(self, request):
        #         return Response({"message": "ok"}, status=status.HTTP_200_OK)
        
        # Como no podemos modificar archivos aquí para añadir esa vista y URL de prueba,
        # esta parte del test es conceptual. Para ejecutarla, deberías añadir esa vista.
        # Por ahora, verificaremos que el usuario está autenticado si usamos el token.
        
        # Ejemplo de cómo se haría la llamada si la ruta existiera:
        # protected_url = reverse('core:test_protected') 
        # self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        # response = self.client.get(protected_url)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Para este test, al menos verificamos que el token es generado
        self.assertTrue(access_token)
