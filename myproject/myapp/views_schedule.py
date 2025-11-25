from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection

@api_view(['POST'])
def fetchSchedulesByDriver(request):
    uid = request.data.get['uid']
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
                    "linoNo": lineNo,
                    "vid": vid,
                })
            return Response({"success": True, "schedules": schedules}, status=200)
        except Exception as e:
            return Response({"success": False, "message": "服务器错误"}, status=500)


@api_view(['POST'])
def fetchSchedulesByVehicle(request):
    vid = request.data.get['vid']
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
                    "linoNo": lineNo,
                    "uid": uid,
                })
            return Response({"success": True, "schedules": schedules}, status=200)
        except Exception as e:
            return Response({"success": False, "message": "服务器错误"}, status=500)
