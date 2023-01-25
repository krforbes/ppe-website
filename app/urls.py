from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('schedule/', views.schedule, name = 'schedule'),
    path('schedule/md/', views.schedule_md, name = 'schedule_md'),
    path('save_schedule/', views.save_schedule, name = 'save_schedule'),
    path('schedule/md/new/', views.schedule_new, name = 'schedule_new'),
    path('schedule_generate/', views.schedule_generate, name = 'schedule_generate'),
    path('preferences/', views.preferences, name = 'preferences'),
    path('save_preferences/', views.save_preferences, name = 'save_preferences'),
    path('preferences/md/', views.preferences_md, name = 'preferences_md'),
    path('preferences_generate/', views.preferences_generate, name = 'preferences_generate'),
    path('availability/', views.availability, name = 'availability'),
    path('availability/md/', views.availability_md, name = 'availability_md'),
    path('availability/<str:name>/', views.availability_view, name = 'availability_view'),
    path('save_availability/', views.save_availability, name = 'save_availability'),
    path('save_mcalpin/', views.save_mcalpin, name = 'save_mcalpin'),
    path('library/', views.library, name = 'library'),
    path('login/', views.login_page, name= 'login_page'),
    path('login_action/', views.login_action, name = 'login_action'),
    path('logout/', views.logout_action, name = 'logout_action'),
    path('change-password/', views.change_password_setup, name = 'change_password_setup'),
    path('no/', views.not_md, name = "not_md"),
    path('congrats-you-solved-the-riddles-on-the-page-that-you-weren\'t-really-supposed-to-be-on-in-the-first-place/', views.riddle_success, name = 'riddle_success'),
    path('admin-redirect/', views.go_to_admin_site, name = 'go_to_admin_site'),
    
]
