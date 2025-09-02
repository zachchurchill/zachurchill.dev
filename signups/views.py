from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import VolunteerForm, VolunteerSlot, VolunteerSignup
from .forms import VolunteerSignupForm
import json

def home(request):
    """Display the home page for the signups app"""
    return render(request, 'signups/home.html')

def volunteer_form_view(request, unique_url):
    """Display a volunteer form for public signup"""
    form = get_object_or_404(VolunteerForm, unique_url=unique_url, is_active=True)
    # Force ordering by date, then by title for slots with same date
    slots = form.slots.all().order_by('date', 'title')
    
    # Calculate total credit hours for the form
    total_credit_hours = form.get_total_credit_hours()
    
    context = {
        'form': form,
        'slots': slots,
        'total_credit_hours': total_credit_hours,
    }
    return render(request, 'signups/volunteer_form.html', context)

def volunteer_slot_detail(request, unique_url, slot_id):
    """Display details for a specific volunteer slot"""
    form = get_object_or_404(VolunteerForm, unique_url=unique_url, is_active=True)
    slot = get_object_or_404(VolunteerSlot, id=slot_id, form=form)
    
    if request.method == 'POST':
        signup_form = VolunteerSignupForm(request.POST)
        if signup_form.is_valid():
            # Check if slot is full
            if slot.is_full():
                messages.error(request, 'Sorry, this slot is already full.')
            else:
                # Create the signup
                signup = signup_form.save(commit=False)
                signup.slot = slot
                signup.save()
                messages.success(request, f'Successfully signed up for {slot.title}!')
                return redirect('signups:volunteer_form_view', unique_url=unique_url)
    else:
        signup_form = VolunteerSignupForm()
    
    # Calculate credit hours for this slot
    slot_credit_hours = slot.get_total_credit_hours()
    individual_credit_hours = slot.volunteer_type.credit_hours if slot.volunteer_type else 0
    
    context = {
        'form': form,
        'slot': slot,
        'signup_form': signup_form,
        'signups': slot.signups.all(),
        'slot_credit_hours': slot_credit_hours,
        'individual_credit_hours': individual_credit_hours,
    }
    return render(request, 'signups/slot_detail.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def ajax_signup(request, unique_url, slot_id):
    """Handle AJAX signup requests"""
    try:
        form = get_object_or_404(VolunteerForm, unique_url=unique_url, is_active=True)
        slot = get_object_or_404(VolunteerSlot, id=slot_id, form=form)
        
        data = json.loads(request.body)
        signup_form = VolunteerSignupForm(data)
        
        if signup_form.is_valid():
            if slot.is_full():
                return JsonResponse({
                    'success': False,
                    'message': 'Sorry, this slot is already full.'
                })
            
            signup = signup_form.save(commit=False)
            signup.slot = slot
            signup.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully signed up for {slot.title}!',
                'available_spots': slot.available_spots(),
                'current_signups': slot.current_signups
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors below.',
                'errors': signup_form.errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        })

def form_summary(request, unique_url):
    """Display a summary of all signups for a form (admin view)"""
    form = get_object_or_404(VolunteerForm, unique_url=unique_url)
    slots = form.slots.all().order_by('date')
    
    # Calculate total credit hours for the form
    total_credit_hours = form.get_total_credit_hours()
    
    context = {
        'form': form,
        'slots': slots,
        'total_credit_hours': total_credit_hours,
    }
    return render(request, 'signups/form_summary.html', context)
