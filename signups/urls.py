from django.urls import path
from . import views

app_name = 'signups'

urlpatterns = [
    path('', views.home, name='home'),
    path('form/<str:unique_url>/', views.volunteer_form_view, name='volunteer_form_view'),
    path('form/<str:unique_url>/slot/<int:slot_id>/', views.volunteer_slot_detail, name='slot_detail'),
    path('form/<str:unique_url>/slot/<int:slot_id>/signup/', views.ajax_signup, name='ajax_signup'),
    path('form/<str:unique_url>/summary/', views.form_summary, name='form_summary'),
]
