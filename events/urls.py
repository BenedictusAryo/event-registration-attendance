from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Event management URLs
    path('', views.EventListView.as_view(), name='event_list'),
    path('create/', views.EventCreateView.as_view(), name='event_create'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('<int:pk>/delete/', views.EventDeleteView.as_view(), name='event_delete'),
    path('<int:pk>/publish/', views.PublishEventView.as_view(), name='publish_event'),
    path('<int:pk>/qr-code/', views.EventQRCodeView.as_view(), name='event_qr_code'),
    
    # Form builder URLs
    path('<slug:slug>/form-builder/', views.EventFormBuilderView.as_view(), name='form_builder'),
    path('<slug:slug>/add-field/', views.AddEventFieldView.as_view(), name='add_field'),
    path('<slug:slug>/edit-field/<int:field_id>/', views.EditEventFieldView.as_view(), name='edit_field'),
    path('<slug:slug>/delete-field/<int:field_id>/', views.DeleteEventFieldView.as_view(), name='delete_field'),
    
    # Public registration URLs
    path('<slug:slug>/register/', views.EventRegistrationView.as_view(), name='event_register'),
    path('registration/<uuid:unique_id>/success/', views.RegistrationSuccessView.as_view(), name='registration_success'),
    path('registration/<uuid:unique_id>/qr/', views.QRCodeView.as_view(), name='qr_code'),
      # Participant management
    path('<int:pk>/participants/', views.ParticipantListView.as_view(), name='participant_list'),
    path('<int:pk>/participants/export/', views.ExportParticipantsView.as_view(), name='export_participants'),
    path('registration/<int:pk>/detail/', views.RegistrationDetailView.as_view(), name='registration_detail'),
    path('registration/<int:pk>/qr/', views.RegistrationQRCodeView.as_view(), name='registration_qr'),
]
