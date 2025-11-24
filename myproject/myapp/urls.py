from django.urls import path
from . import views
urlpatterns = [
    path('api/login/', views.login),
    path('api/drivers/changeProfile', views.driver_change_profile),
    path('api/admin/fetchAllDrivers', views.fetchAllDrivers),
    path('api/admin/createDriver', views.add_driver)
]