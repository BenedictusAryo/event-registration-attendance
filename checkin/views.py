from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
import json
import uuid

from events.models import Event, Registration

class CheckinHomeView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'checkin/checkin_home.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user, is_published=True)

class QRScannerView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'checkin/qr_scanner.html'
    context_object_name = 'event'

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)

class ScanQRCodeAPIView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            qr_code = data.get('qr_code')
            
            if not qr_code:
                return JsonResponse({'error': 'QR code is required'}, status=400)
            
            # Try to parse the QR code as UUID
            try:
                unique_id = uuid.UUID(qr_code)
            except ValueError:
                return JsonResponse({'error': 'Invalid QR code format'}, status=400)
            
            # Find registration
            try:
                registration = Registration.objects.get(unique_id=unique_id)
            except Registration.DoesNotExist:
                return JsonResponse({'error': 'Registration not found'}, status=404)
            
            # Check if user is organizer
            if registration.event.organizer != request.user:
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            return JsonResponse({
                'registration_id': registration.id,
                'participant_name': registration.participant_name,
                'participant_email': registration.participant_email,
                'event_name': registration.event.name,
                'status': registration.status,
                'registered_at': registration.registered_at.isoformat(),
                'attended_at': registration.attended_at.isoformat() if registration.attended_at else None,
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class CheckinAPIView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            registration_id = data.get('registration_id')
            
            if not registration_id:
                return JsonResponse({'error': 'Registration ID is required'}, status=400)
            
            # Find registration
            try:
                registration = Registration.objects.get(id=registration_id)
            except Registration.DoesNotExist:
                return JsonResponse({'error': 'Registration not found'}, status=404)
            
            # Check if user is organizer
            if registration.event.organizer != request.user:
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            # Update status
            if registration.status == 'attended':
                return JsonResponse({'error': 'Already checked in'}, status=400)
            
            registration.status = 'attended'
            registration.attended_at = timezone.now()
            registration.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{registration.participant_name} checked in successfully',
                'attended_at': registration.attended_at.isoformat(),
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ParticipantListView(LoginRequiredMixin, ListView):
    model = Registration
    template_name = 'checkin/participants.html'
    context_object_name = 'registrations'
    paginate_by = 25

    def get_queryset(self):
        event = Event.objects.get(pk=self.kwargs['pk'], organizer=self.request.user)
        queryset = Registration.objects.filter(event=event)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(participant_name__icontains=search) |
                Q(participant_email__icontains=search) |
                Q(participant_phone__icontains=search)
            )
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Sorting
        sort = self.request.GET.get('sort', '-registered_at')
        if sort in ['-registered_at', 'registered_at', 'participant_name', '-participant_name', '-attended_at']:
            queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = Event.objects.get(pk=self.kwargs['pk'], organizer=self.request.user)
        return context
