from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection

@api_view(['POST'])
def fetchAllTransferHistory(request):
    vid = request.data.get('vid')
    print(f"Received transfer query request for vehicle: {vid}")
    try:
        with connection.cursor as cursor:
            cursor.execute(
                "SELECT fromDepot, toDepot, date, note FROM myapp_transfer WHERE vid=%s",
                [vid]
            )
            rows = cursor.fetchAll()
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
        with connection.cursor as cursor:
            cursor.execute(
                "SELECT vid, lp, vtype, req FROM myapp_vehicle WHERE depotID=%s",
                [depotID]
            )
            rows = cursor.fetchAll()
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
def addVehicle(request):
    vid = request.data.get("vid")
    lp = request.data.get("lp")
    vtype = request.data.get("vtype")
    req = request.data.get("req")
    depotID = request.data.get("depotID")
    print(f"Received vehicle add request. VID: {vid}, LP: {lp}, VType: {vtype}, Req: {req}, DepotID: {depotID}")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO myapp_vehicle (vid, lp, vtype, req, depotID) VALUES (%s, %s, %s, %s, %s)",
                [vid, lp, vtype, req, depotID]
            )
            if cursor.rowcount == 1:
                return Response({"success": True}, status=200)
            else:
                return Response({"success": False, "message": "添加失败"}, status=400)
    except Exception as e:
        return Response({"success": False, "message": "服务器错误"}, status=500)


@api_view(['POST'])
def removeVehicle(request):
    


@api_view(['POST'])
def transferVehicle(request):
    