from django.urls import path
from . import views

app_name = 'checkin'

urlpatterns = [
    path('', views.CheckinHomeView.as_view(), name='checkin_home'),
    path('<int:pk>/scanner/', views.QRScannerView.as_view(), name='qr_scanner'),
    path('<int:pk>/participants/', views.ParticipantListView.as_view(), name='participants'),
    path('api/scan/', views.ScanQRCodeAPIView.as_view(), name='scan_qr_api'),
    path('api/checkin/', views.CheckinAPIView.as_view(), name='checkin_api'),
]
