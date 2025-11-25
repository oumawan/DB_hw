from django.urls import path
from . import views

import myapp.view.login

urlpatterns = [
    path('api/login/', myapp.view.login.login),
    path('api/drivers/changeProfile', views.driver_change_profile),
    path('api/admin/fetchAllDrivers', views.fetchAllDrivers),
    path('api/admin/createDriver', views.add_driver)
]