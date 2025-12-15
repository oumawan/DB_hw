from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
from datetime import datetime
# from myapp.models import Driver, Vehicle, Line, Schedule, Leave, User # 移除 ORM 相关的导入

@api_view(['POST'])
def fetchSchedulesByDriver(request):
    uid = request.data.get('uid')
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT sid, dtime, atime, dlocation, lineNo, vid FROM myapp_schedule WHERE uid=%s",
                [uid]
            )
            rows = cursor.fetchall()
            schedules = []
            for row in rows:
                sid, dtime, atime, dlocation, lineNo, vid = row
                schedules.append({
                    "sid": sid,
                    "dtime": dtime,
                    "atime": atime,
                    "dlocation": dlocation,
                    "lineNo": lineNo,
                    "vid": vid,
                })
            return Response({"success": True, "schedules": schedules}, status=200)
        except Exception as e:
            return Response({"success": False, "message": "服务器错误"}, status=500)


@api_view(['POST'])
def fetchSchedulesByVehicle(request):
    vid = request.data.get('vid')
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT sid, dtime, atime, dlocation, lineNo, uid FROM myapp_schedule WHERE vid=%s",
                [vid]
            )
            rows = cursor.fetchall()
            schedules = []
            for row in rows:
                sid, dtime, atime, dlocation, lineNo, uid = row
                schedules.append({
                    "sid": sid,
                    "dtime": dtime,
                    "atime": atime,
                    "dlocation": dlocation,
                    "lineNo": lineNo,
                    "uid": uid,
                })
            return Response({"success": True, "schedules": schedules}, status=200)
        except Exception as e:
            return Response({"success": False, "message": "服务器错误"}, status=500)

@api_view(['POST'])
def fetchSchedulesByLine(request):
    lineNo = request.data.get('lineNo')
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT sid, dtime, atime, dlocation, vid, uid FROM myapp_schedule WHERE lineNo=%s",
                [lineNo]
            )
            rows = cursor.fetchall()
            schedules = []
            for row in rows:
                sid, dtime, atime, dlocation, vid, uid = row
                schedules.append({
                    "sid": sid,
                    "dtime": dtime,
                    "atime": atime,
                    "dlocation": dlocation,
                    "vid": vid,
                    "uid": uid,
                })
            return Response({"success": True, "schedules": schedules}, status=200)
        except Exception as e:
            return Response({"success": False, "message": "服务器错误"}, status=500)
        
# TODO: 班次分配；
# TODO: 班次这里，前端应该支持按时间过滤，否则这个规模可能过大；又或者，把时间也放进查询条件？

@api_view(['POST'])
def auto_dispatch_schedule(request):
    try:
        lineNo = request.data.get('lineNo')
        dtime_str = request.data.get('dtime')
        atime_str = request.data.get('atime')

        dtime = datetime.fromisoformat(dtime_str)
        atime = datetime.fromisoformat(atime_str)
    except (ValueError, TypeError):
        return Response({"success": False, "message": "无效的时间格式或缺少参数"}, status=400)

    with connection.cursor() as cursor:
        # 1. 获取线路信息
        cursor.execute("SELECT lineNo, vtype, lineFrom FROM myapp_line WHERE lineNo = %s", [lineNo])
        line_info = cursor.fetchone()
        if not line_info:
            return Response({"success": False, "message": "线路不存在"}, status=404)
        
        # 将结果转换为字典以便于访问
        line = {
            "lineNo": line_info[0],
            "vtype": line_info[1],
            "lineFrom": line_info[2]
        }

        # 2. 查找可用司机
        # 查找所有司机，并排除请假和有其他排班的司机
        cursor.execute(
            """
            SELECT U.uid
            FROM myapp_user U
            INNER JOIN myapp_driver D ON U.uid = D.uid
            WHERE NOT EXISTS (
                SELECT 1 FROM myapp_leave L
                WHERE L.uid_id = U.uid
                AND L.tbegin < %s AND L.tend > %s
            )
            AND NOT EXISTS (
                SELECT 1 FROM myapp_schedule S
                WHERE S.uid_id = U.uid
                AND S.dtime < %s AND S.atime > %s
            )
            """,
            [atime, dtime, atime, dtime]
        )
        available_drivers = [row[0] for row in cursor.fetchall()]

        if not available_drivers:
            return Response({"success": False, "message": "没有可用的司机"}, status=404)

        # 3. 查找可用车辆
        # 查找所有车辆中，与线路的 vtype 匹配的车辆，并排除有其他排班和有调动记录的车辆
        cursor.execute(
            """
            SELECT V.vid
            FROM myapp_vehicle V
            WHERE V.vtype = %s
            AND NOT EXISTS (
                SELECT 1 FROM myapp_schedule S
                WHERE S.vid_id = V.vid
                AND S.dtime < %s AND S.atime > %s
            )
            AND NOT EXISTS (
                SELECT 1 FROM myapp_transfer T
                WHERE T.vid_id = V.vid
                AND T.date = %s
            )
            """,
            [line['vtype'], atime, dtime, dtime.date()]
        )
        available_vehicles = [row[0] for row in cursor.fetchall()]

        if not available_vehicles:
            return Response({"success": False, "message": "没有可用的车辆"}, status=404)

        # 4. 创建班次记录 (使用第一个找到的可用司机和车辆)
        assigned_driver_uid = available_drivers[0]
        assigned_vehicle_vid = available_vehicles[0]
        
        try:
            cursor.execute(
                """
                INSERT INTO myapp_schedule (dtime, atime, dlocation, lineNo_id, vid_id, uid_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [dtime, atime, line['lineFrom'], line['lineNo'], assigned_vehicle_vid, assigned_driver_uid]
            )
            # 获取新插入的 schedule 的 sid (如果需要)
            # 对于 SQLite，可以通过 SELECT last_insert_rowid() 获取
            # 对于 PostgreSQL，可以使用 RETURNING sid
            # 这里简化处理，不返回 sid
            return Response({
                "success": True,
                "message": "班次自动签派成功",
                "assigned_driver_id": assigned_driver_uid,
                "assigned_vehicle_id": assigned_vehicle_vid
            }, status=201)
        except Exception as e:
            return Response({"success": False, "message": f"创建班次失败: {str(e)}"}, status=500)