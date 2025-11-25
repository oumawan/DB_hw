from django.urls import path
import view
from . import views

import myproject.myapp.view.user

# TODO: 映射肯定没写完
urlpatterns = [
    path('api/login/', view.user.login),
    path('api/drivers/changeProfile', views.driver_change_profile),
    path('api/admin/fetchAllDrivers', views.fetchAllDrivers),
    path('api/admin/createDriver', views.add_driver)
]