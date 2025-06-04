from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction

from .models import UserProfile
from .forms import UserProfileForm, UserForm
from events.models import Event, Registration

class UserProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'core/user_profile.html'
    context_object_name = 'profile'

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's events
        user_events = Event.objects.filter(organizer=user).order_by('-created_at')
        
        # Get statistics
        total_events = user_events.count()
        total_participants = Registration.objects.filter(event__organizer=user).count()
        total_attended = Registration.objects.filter(event__organizer=user, status='attended').count()
        
        # Get recent events (last 5)
        recent_events = user_events[:5]
        
        # Mock recent activity (in a real app, you'd have an Activity model)
        recent_activity = []
        
        context.update({
            'total_events': total_events,
            'total_participants': total_participants,
            'total_attended': total_attended,
            'recent_events': recent_events,
            'recent_activity': recent_activity,
        })
        
        return context

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'core/edit_profile.html'
    success_url = reverse_lazy('core:user_profile')

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_form'] = UserForm(self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserForm(instance=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        profile_form = self.get_form()
        user_form = UserForm(request.POST, instance=request.user)

        if profile_form.is_valid() and user_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect(self.success_url)
        else:
            context = self.get_context_data()
            context['user_form'] = user_form
            return self.render_to_response(context)
