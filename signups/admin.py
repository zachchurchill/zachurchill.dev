from django.contrib import admin
from django.utils.html import format_html
from django.http import JsonResponse
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib import messages
from django.shortcuts import redirect
from .models import VolunteerForm, VolunteerSlot, VolunteerSignup, VolunteerType

class VolunteerSignupInline(admin.TabularInline):
    model = VolunteerSignup
    extra = 0
    readonly_fields = ['signed_up_at']
    fields = ['name', 'email', 'phone', 'notes', 'signed_up_at']

class VolunteerSlotInline(admin.TabularInline):
    model = VolunteerSlot
    extra = 1
    fields = ['volunteer_type', 'title', 'description', 'date', 'max_volunteers', 'current_signups']
    readonly_fields = ['current_signups']

@admin.register(VolunteerForm)
class VolunteerFormAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'is_active', 'form_link', 'total_slots', 'total_signups']
    list_filter = ['is_active', 'created_at', 'created_by']
    search_fields = ['title', 'description']
    readonly_fields = ['unique_url', 'form_link', 'created_at', 'updated_at']
    actions = ['open_form', 'copy_form_url']
    fieldsets = (
        ('Form Information', {
            'fields': ('title', 'description', 'is_active', 'created_by')
        }),
        ('Form Access', {
            'fields': ('unique_url', 'form_link'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [VolunteerSlotInline]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('volunteer-types/', self.admin_site.admin_view(self.get_volunteer_types), name='volunteer-types'),
        ]
        return custom_urls + urls
    
    def get_volunteer_types(self, request):
        volunteer_types = VolunteerType.objects.filter(is_active=True).values('id', 'name', 'description')
        return JsonResponse(list(volunteer_types), safe=False)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['volunteer_types'] = VolunteerType.objects.filter(is_active=True)
        return super().change_view(request, object_id, form_url, extra_context)
    
    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['volunteer_types'] = VolunteerType.objects.filter(is_active=True)
        return super().add_view(request, form_url, extra_context)
    
    def total_slots(self, obj):
        return obj.slots.count()
    total_slots.short_description = 'Total Slots'
    
    def total_signups(self, obj):
        return sum(slot.signups.count() for slot in obj.slots.all())
    total_signups.short_description = 'Total Signups'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

    def form_link(self, obj):
        """Display a clickable link to the volunteer form"""
        if obj.unique_url:
            url = obj.get_form_url()
            return format_html(
                '<a href="{}" target="_blank" style="background: #007cba; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; font-size: 12px;">🔗 Open Form</a><br><small style="color: #666;">{}</small>',
                url, obj.unique_url
            )
        return obj.unique_url
    form_link.short_description = 'Form Link'
    form_link.admin_order_field = 'unique_url'
    
    def open_form(self, request, queryset):
        """Admin action to open the volunteer form in a new tab"""
        if queryset.count() == 1:
            form = queryset.first()
            return redirect(form.get_form_url())
        else:
            messages.warning(request, 'Please select only one form to open.')
    open_form.short_description = "Open selected form"
    
    def copy_form_url(self, request, queryset):
        """Admin action to copy form URL to clipboard (shows message)"""
        if queryset.count() == 1:
            form = queryset.first()
            messages.success(request, f'Form URL copied: {form.get_form_url()}')
        else:
            messages.warning(request, 'Please select only one form to copy URL.')
    copy_form_url.short_description = "Copy form URL"

@admin.register(VolunteerSlot)
class VolunteerSlotAdmin(admin.ModelAdmin):
    list_display = ['title', 'volunteer_type', 'form', 'date', 'current_signups', 'max_volunteers', 'is_full']
    list_filter = ['date', 'form', 'form__is_active', 'volunteer_type']
    search_fields = ['title', 'description', 'form__title', 'volunteer_type__name']
    readonly_fields = ['current_signups']
    inlines = [VolunteerSignupInline]
    

    
    def is_full(self, obj):
        return obj.is_full()
    is_full.boolean = True
    is_full.short_description = 'Full'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('form')

@admin.register(VolunteerSignup)
class VolunteerSignupAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'slot', 'form_title', 'signed_up_at']
    list_filter = ['signed_up_at', 'slot__date', 'slot__form']
    search_fields = ['name', 'email', 'slot__title', 'slot__form__title']
    readonly_fields = ['signed_up_at']
    
    def form_title(self, obj):
        return obj.slot.form.title
    form_title.short_description = 'Form'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('slot', 'slot__form')

@admin.register(VolunteerType)
class VolunteerTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']
