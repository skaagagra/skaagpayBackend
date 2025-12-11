from rest_framework import status, views
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token 
from .serializers import UserSerializer, LoginSerializer

User = get_user_model()

class LoginView(views.APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            full_name = serializer.validated_data.get('full_name')
            
            # Simplified login: if user exists return user, else create.
            defaults = {'full_name': full_name} if full_name else {'full_name': 'New User'}
            
            user, created = User.objects.get_or_create(phone_number=phone_number, defaults=defaults)
            
            # If user exists but full_name is provided, update it (if currently default or requested)
            if not created and full_name:
                user.full_name = full_name
                user.save()
            
            return Response({
                'message': 'Login Successful',
                'user': UserSerializer(user).data,
                'created': created
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
