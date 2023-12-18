from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import register, login, update_profile, save_data, get_data_by_id, get_all_data_history, admin_login, delete_user, toggle_user, reset_password, user_list, user_stat

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('update-profile/', update_profile, name='update-profile'),
    path('sensor-data/save/', save_data, name='save-sensor-data'),
    path('sensor-data/<int:id>/', get_data_by_id, name='get-sensor-data-by-id'),
    path('sensor-data/history/', get_all_data_history, name='get-all-sensor-data-history'),

    path('admin/login/', admin_login, name='admin-login'),
    path('admin/users/', user_list, name='user-list'),
    path('admin/stat/', user_stat, name='user-stat'),
    path('admin/logout/', LogoutView.as_view(next_page='admin-login'), name='admin-logout'),

    path('admin/users/delete/<int:user_id>/', delete_user, name='delete-user'),
    path('admin/users/toggle/<int:user_id>/', toggle_user, name='toggle-user'),
    path('admin/users/reset-password/<int:user_id>/', reset_password, name='reset-password'),
]
