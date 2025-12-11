from rest_framework import status, views
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token # We might need to install djangorestframework-authtoken or use simple JWT if preferred, but for now assuming Basic is implicit or just returning user data. Actually, let's just return a dummy token or user ID for this simple flow since user said "login with phone number". 
# Better: Create/Get user and return it.
from .serializers import UserSerializer, LoginSerializer

User = get_user_model()

class LoginView(views.APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            # Simplified login: if user exists return user, else create.
            # In production, this needs SMS verification.
            user, created = User.objects.get_or_create(phone_number=phone_number, defaults={'full_name': 'New User'})
            
            # Use DRF Token if installed or just return User ID for simplicity as requested?
            # Let's keep it very simple: return User ID.
            
            return Response({
                'message': 'Login Successful',
                'user': UserSerializer(user).data,
                'created': created
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
