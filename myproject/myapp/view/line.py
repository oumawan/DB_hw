from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection, transaction

@api_view(['POST'])
@transaction.atomic
def addLine(request):
    lineName = request.data.get("lineName")
    lineFrom = request.data.get("lineFrom")
    lineTo = request.data.get("lineTo")
    depotID = request.data.get("depotID")
    vtype = request.data.get("vtype")
    run_duration = request.data.get("run_duration")
    print(f"Received line add request " + lineName + ", " + lineFrom + ", " + lineTo + ", " + depotID + ", " + vtype + ", " + str(run_duration))
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO myapp_line (lineName, lineFrom, lineTo, depotID, vtype, run_duration) VALUES (%s, %s, %s, %s, %s, %s)",
                [lineName, lineFrom, lineTo, depotID, vtype, run_duration]
            )
            if cursor.rowcount == 1:
                return Response({"success": True}, status=200)
            else:
                return Response({"success": False, "message": "添加失败"}, status=400)
    except Exception as e:
        return Response({"success": False, "message": "服务器错误"}, status=500)

@api_view(['POST'])
def fetchAllLines(request):
    depotID = request.data.get("depotID")
    print(f"Received line fetch request for depotID: {depotID}")
    try:
        with connection.cursor()as cursor:
            cursor.execute(
                "SELECT lineNo, lineName, lineFrom, lineTo, vtype, run_duration \
                    FROM myapp_line WHERE depotID=%s",
                [depotID]
            )
            rows = cursor.fetchall()
            lines = []
            for row in rows:
                lineNo, lineName, lineFrom, lineTo, vtype, run_duration = row
                lines.append({
                    "lineNo": lineNo, 
                    "lineName": lineName, 
                    "lineFrom": lineFrom,
                    "lineTo": lineTo,
                    "vtype": vtype, 
                    "run_duration": run_duration,
                })
            return Response({"success": True, "lines": lines}, status=200)
    except Exception as e:
        return Response({"success": False, "message": "服务器错误"}, status=500)

@api_view(['POST'])
@transaction.atomic
def removeLine(request):
    # 移除线路后，同时也应移除与之关联的班次
    lineNo = request.data.get("lineNo")
    print(f"Received line remove request. lineNo: {lineNo}")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM myapp_line WHERE lineNo=%s",
                [lineNo]
            )
            if cursor.rowcount < 0:
                return Response({"success": False, "message": "删除失败"}, status=400)
        return Response({"success": True}, status=200)
    except Exception as e:
        return Response({"success": False, "message": "服务器错误"}, status=500)
