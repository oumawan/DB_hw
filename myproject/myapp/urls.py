from django.urls import path
from .view import driver, line, schedule, user, vehicle

# TODO: 映射肯定没写完
urlpatterns = [
    path('api/user/login/', user.login),    #已完成
    path('api/user/changeProfile/', user.modifyUserInfo),   #已完成
    path('api/user/changePassword/', user.modifyUserPassword),  #已完成

    path('api/driver/changeInfo/', driver.driver_change_profile),   #已完成
    path('api/admin/drivers/fetchAll/', driver.fetchAllDrivers),    #已完成
    path('api/admin/drivers/add/', driver.add_driver),  #已完成
    path('api/driver/leave/add/', driver.addLeave),     #已完成，但是没有查找功能，也没有和调度相配合，所以目前用不到

    path('api/admin/line/add/', line.addLine),      #已完成
    path('api/admin/line/fetchAll/', line.fetchAllLines),       #已完成
    path('api/admin/line/remove/', line.removeLine),    #已完成
    path('api/line/fetchOneRunDuration/', line.fetchOneLineRunDuration),

    #目前用不到
    path('api/schedules/fetchAll/', schedule.fetchAllSchedules),
    path('api/schedules/byDriver/', schedule.fetchSchedulesByDriver),
    path('api/schedules/byVehicle/', schedule.fetchSchedulesByVehicle),
    path('api/schedules/byLine/', schedule.fetchSchedulesByLine),
    path('api/schedule/autoDispatch/', schedule.auto_dispatch_schedule), # 新增的自动签派接口

    path('api/admin/vehicle/fetchAlltransferHistory/', vehicle.fetchAllTransferHistory),    #已完成
    path('api/admin/vehicle/fetchAll/', vehicle.fetchAllVehicles),      #已完成
    path('api/admin/vehicle/add/', vehicle.addVehicle),     #已完成
    path('api/admin/vehicle/remove/', vehicle.removeVehicle),   #已完成
    path('api/admin/vehicle/transfer/', vehicle.transferVehicle),   #已完成
]