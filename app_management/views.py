from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import AppVersion
from .serializers import AppVersionSerializer
from admin_panel.views import AdminUserMixin

from django.views.generic import TemplateView
from .models import AppVersion

class HomeView(TemplateView):
    template_name = 'app_management/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_version'] = AppVersion.objects.order_by('-version_code').first()
        return context

class LatestAppVersionView(generics.RetrieveAPIView):
    """
    Public endpoint to get the latest app version info.
    """
    serializer_class = AppVersionSerializer
    permission_classes = [] # Public

    def get_object(self):
        return AppVersion.objects.order_by('-version_code').first()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({'message': 'No version available', 'version_code': 0}, status=status.HTTP_200_OK)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class UploadAppVersionView(views.APIView, AdminUserMixin):
    """
    Admin endpoint to upload a new APK and version info.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if not self.get_admin_user():
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = AppVersionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
