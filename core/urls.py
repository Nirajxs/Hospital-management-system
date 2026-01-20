from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),
    path('profile/', views.profile, name='profile'),
    path('appointment/book/', views.book_appointment, name='appointment_book'),
    path('appointment/<int:pk>/payment/', views.appointment_payment, name='appointment_payment'),
    path('appointment/<int:pk>/confirm/', views.confirm_payment, name='confirm_payment'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('appointment/<int:pk>/status/', views.update_appointment_status, name='update_appointment_status'),

    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('rate-doctor/<int:doctor_id>/', views.rate_doctor, name="rate_doctor"),

    # urls.py
    # path("logout/", custom_logout, name="logout"),

]
