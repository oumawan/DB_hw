from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection, transaction

@api_view(['POST'])
def fetchAllTransferHistory(request):
    vid = request.data.get('vid')
    print(f"Received transfer query request for vehicle: {vid}")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT fromDepot, toDepot, date, note FROM myapp_transfer WHERE vid_id=%s",
                [vid]
            )
            rows = cursor.fetchall()
            transfers = []
            for row in rows:
                fromDepot, toDepot, date, note = row
                transfers.append({
                    "fromDepot": fromDepot, 
                    "toDepot": toDepot, 
                    "date": date, 
                    "note": note
                })
            return Response({"success": True, "transfers": transfers}, status=200)
    except Exception as e:
        return Response({"success": False, "message": "服务器错误"}, status=500)
    
@api_view(['POST'])
def fetchAllVehicles(request):
    depotID = request.data.get("depotID")
    print(f"Received vehicle fetch request for depotID: {depotID}")
    try:
        with connection.cursor()as cursor:
            cursor.execute(
                "SELECT vid, lp, vtype, req FROM myapp_vehicle WHERE depotID=%s",
                [depotID]
            )
            rows = cursor.fetchall()
            vehicles = []
            for row in rows:
                vid, lp, vtype, req = row
                vehicles.append({
                    "vid": vid, 
                    "lp": lp, 
                    "vtype": vtype, 
                    "req": req
                })
            return Response({"success": True, "vehicles": vehicles}, status=200)
    except Exception as e:
        return Response({"success": False, "message": "服务器错误"}, status=500)
        

@api_view(['POST'])
@transaction.atomic
def addVehicle(request):
    lp = request.data.get("lp")
    vtype = request.data.get("vtype")
    req = request.data.get("req")
    depotID = request.data.get("depotID")
    print(f"Received vehicle add request. LP: {lp}, VType: {vtype}, Req: {req}, DepotID: {depotID}")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO myapp_vehicle (lp, vtype, req, depotID) VALUES (%s, %s, %s, %s)",
                [lp, vtype, req, depotID]
            )
            if cursor.rowcount == 1:
                return Response({"success": True}, status=200)
            else:
                return Response({"success": False, "message": "添加失败"}, status=400)
    except Exception as e:
        return Response({"success": False, "message": "服务器错误"}, status=500)


@api_view(['POST'])
@transaction.atomic
def removeVehicle(request):
    # 移除车辆后，同时也应移除历史记录，以及与之关联的班次
    vid = request.data.get("vid")
    print(f"Received vehicle remove request. VID: {vid}")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM myapp_vehicle WHERE vid=%s",
                [vid]
            )
            if cursor.rowcount < 0:
                return Response({"success": False, "message": "删除失败"}, status=400)
        return Response({"success": True}, status=200)
    except Exception as e:
        return Response({"success": False, "message": "服务器错误"}, status=500)

@api_view(['POST'])
@transaction.atomic
def transferVehicle(request):
    vid = request.data.get('vid')
    fromDepot = request.data.get('fromDepot')
    toDepot = request.data.get('toDepot')
    date = request.data.get('date')
    note = request.data.get('note')
    print(f"Received transfer query request: {request.data}")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO myapp_transfer (vid_id, fromDepot, toDepot, date, note) VALUES (%s, %s, %s, %s, %s)",
                [vid, fromDepot, toDepot, date, note]
            )
            if cursor.rowcount != 1:
                return Response({"success": False, "message": "失败"}, status=400)
        return Response({"success": True}, status=200)  
    except Exception as e:
        return Response({"success": False, "message": "服务器错误"}, status=500)