from django.urls import path
from .views import LatestAppVersionView, UploadAppVersionView, HomeView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('latest/', LatestAppVersionView.as_view(), name='latest-version'),
    path('upload/', UploadAppVersionView.as_view(), name='upload-version'),
]
