from django.urls import path
from .views.auth import signup, user_login, user_logout
from .views.profile import user_profile, update_profile, change_user_password, deactivate_user_profile
from .views.booking import list_booking, user_booking_update, user_booking_delete
from .views.review import add_review, service_reviews
from .views.service import services
from .views import main_page, about_us, temp_list_all_db

urlpatterns = [
    path('', main_page, name='main'),
    path('about-us/', about_us, name='about_us'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('services/', services, name='services'),

    path('profile/', user_profile, name='user_profile'),
    path('profile/update_profile/', update_profile, name='update_profile'),
    path('profile/change_password/', change_user_password, name='change_password'),
    path('profile/deactivate_profile/', deactivate_user_profile, name='deactivate_profile'),

    path('profile/list_booking', list_booking, name='list_booking'),
    path('profile/booking/update/<int:pk>/', user_booking_update, name='user_booking_update'),
    path('profile/booking/delete/<int:pk>/', user_booking_delete, name='user_booking_delete'),

    path('review/add/<int:booking_id>/', add_review, name='add_review'),
    path('reviews/<int:service_id>/', service_reviews, name='service_reviews'),

    path('list/', temp_list_all_db, name='list'),
]

