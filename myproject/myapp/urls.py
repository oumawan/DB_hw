from django.urls import path
from .view import driver, line, schedule, user, vehicle

# TODO: 映射肯定没写完
urlpatterns = [
    path('api/user/login/', user.login),
    path('api/user/changeProfile/', user.modifyUserInfo),
    path('api/user/changePassword/', user.modifyUserPassword),

    path('api/driver/changeInfo/', driver.driver_change_profile),
    path('api/admin/drivers/fetchAll/', driver.fetchAllDrivers),
    path('api/admin/drivers/add/', driver.add_driver),
    path('api/driver/leave/add/', driver.addLeave),

    path('api/admin/line/add/', line.addLine),
    path('api/admin/line/fetchAll/', line.fetchAllLines),
    path('api/admin/line/remove/', line.removeLine),

    path('api/schedules/byDriver/', schedule.fetchSchedulesByDriver),
    path('api/schedules/byVehicle/', schedule.fetchSchedulesByVehicle),
    path('api/schedules/byLine/', schedule.fetchSchedulesByLine),

    path('api/admin/vehicle/fetchAlltransferHistory/', vehicle.fetchAllTransferHistory),
    path('api/admin/vehicle/fetchAll/', vehicle.fetchAllVehicles),
    path('api/admin/vehicle/add/', vehicle.addVehicle),
    path('api/admin/vehicle/remove/', vehicle.removeVehicle),
    path('api/admin/vehicle/transfer/', vehicle.transferVehicle),
]