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
                "SELECT fromDepot, toDepot, date, note FROM myapp_transfer WHERE vid=%d",
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


@api_view(['POST'])
def addVehicle(request):

@api_view(['POST'])
def removeVehicle(request):

@api_view(['POST'])
def transferVehicle(request):
    