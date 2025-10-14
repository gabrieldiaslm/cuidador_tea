from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Páginas de autenticação
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.signup, name='signup'),

    # Seleção e gerenciamento de perfis
    path('profiles/', views.profile_select, name='profile_select'),
    path('profiles/select/<int:profile_id>/', views.select_profile_and_redirect, name='select_profile_and_redirect'),
    path('profiles/create/', views.profile_create, name='profile_create'),

    # Página principal
    path('home/', views.home, name='home'),

    # Redirecionamento
    path('', views.index, name='index'),
    
    # Páginas de Avaliações
    path('assessments/', views.assessment_list, name='assessment_list'),
    path('assessments/<int:assessment_id>/take/', views.take_assessment, name='take_assessment'),
    path('history/', views.assessment_history, name='assessment_history'),
]