from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
]
