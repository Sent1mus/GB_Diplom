from django.urls import path
from .views.auth import signup, user_login, user_logout
from .views.profile import user_profile, edit_profile, change_password, deactivate_profile
from .views.booking import user_booking_list, user_booking_update, user_booking_delete
from .views.service import *
from .views import *


urlpatterns = [
    path('', main_page, name='main'),
    path('about-us/', about_us, name='about_us'),
    path('services/', services, name='services'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),


    path('services/book/<int:service_id>/', book_service, name='book_service'),
    path('services/select-provider/<int:service_id>/', select_provider, name='select_provider'),
    path('services/booking-confirm/<int:service_id>/<int:provider_id>/', booking_confirm, name='booking_confirm'),

    path('user_profile/', user_profile, name='user_profile'),
    path('user_profile/edit/', edit_profile, name='edit_profile'),
    path('user_profile/change_password/', change_password, name='change_password'),
    path('user_profile/deactivate/', deactivate_profile, name='deactivate_profile'),
    path('user_profile/bookings_list/', user_booking_list, name='user_booking_list'),
    path('user_profile/bookings/update/<int:pk>/', user_booking_update, name='user_booking_update'),
    path('user_profile/bookings/delete/<int:pk>/', user_booking_delete, name='user_booking_delete'),
    path('list/', list_all_db, name='list'),
]

