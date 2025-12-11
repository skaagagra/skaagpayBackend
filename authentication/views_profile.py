from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserSerializer

class UserParamsMixin:
    def get_user(self):
        user_id = self.request.headers.get('X-User-ID')
        if not user_id:
            return None
        return get_object_or_404(User, pk=user_id)

class UserProfileView(generics.RetrieveUpdateAPIView, UserParamsMixin):
    serializer_class = UserSerializer

    def get_object(self):
        user = self.get_user()
        if not user:
             # In a real app this should raise PermissionDenied or similar,
             # but to match our flow logic with 404/401 handling in mixin:
             return None 
        return user
