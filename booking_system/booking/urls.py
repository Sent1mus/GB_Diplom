from django.urls import path
from .views import main_page, about_us, services, signup, user_login, user_logout, list_all_db, profile

urlpatterns = [
    path('', main_page, name='main'),
    path('about-us/', about_us, name='about_us'),
    path('services/', services, name='services'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('list/', list_all_db, name='list'),
]
