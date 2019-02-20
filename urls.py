from django.urls import path
from . import views

# <a href='{% url 'users:index'%}'></a>
app_name = 'users'
urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]