from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection, transaction

DEFAULT_PASSWORD = "7355608"

@api_view(['POST'])
@transaction.atomic
def driver_change_profile(request):
    print("Received driver profile change request with data:", request.data)
    uid = request.data.get('uid')
    license = request.data.get('license')
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE myapp_driver SET license=%s WHERE uid=%s",
                [license, uid]
            )
        return Response({"success": True}, status=200)
    except Exception as e:
        print(f"Error during profile update: {e}")
        return Response({"success": False, "message": "服务器错误"}, status=500)
    
@api_view(['POST'])
def fetchAllDrivers(request):
    depotID = request.data.get('depotID')
    with connection.cursor() as cursor:
        try:
            cursor.execute(
                "SELECT U.uid, U.name, U.email, D.license \
                    FROM myapp_user U, myapp_driver D \
                        WHERE U.depotID=%s AND U.uid=D.uid", [depotID]
            )
            rows = cursor.fetchall()
            drivers = []
            for row in rows:
                uid, name, email, license = row
                drivers.append({
                    "uid": uid,
                    "name": name,
                    "email": email,
                    "license": license
                })
            return Response({"success": True, "drivers": drivers}, status=200)
        except Exception as e:
            return Response({"success": False, "message": "服务器错误"}, status=500)

@api_view(['POST'])
@transaction.atomic
def add_driver(request):
    name = request.data.get('name')
    email = request.data.get('email')
    license = request.data.get('license')
    depotID = request.data.get('depotID')
    print(f"Received add driver request with name: {name}, email: {email}, license: {license}, depotID: {depotID}")
    try:
        new_uid = None
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO myapp_user (name, email, password, depotID) VALUES (%s, %s, %s, %s)",
                [name, email, DEFAULT_PASSWORD, depotID]
            )
            new_uid = cursor.lastrowid
            if new_uid is None:
                return Response({"success": False, "message": "添加失败"}, status=400)
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO myapp_driver (uid, license) VALUES (%s, %s)",
                [new_uid, license]
            )
            if cursor.rowcount == 1:
                return Response({"success": True}, status=200)
            else:
                return Response({"success": False, "message": "添加失败"}, status=400)
    except Exception as e:
        print(f"Error adding driver: {e}")
        return Response({"success": False, "message": "服务器错误"}, status=500)
    
@api_view(['POST'])
@transaction.atomic
def addLeave(request):
    uid = request.data.get('uid')
    tbegin = request.data.get('tbegin')
    tend = request.data.get('tend')
    reason = request.data.get('reason')
    print(f"Received addLeave request. UID {uid}, tbegin {tbegin}, tend {tend}, reason: {reason}")
    try:
        with connection.cursor()as cursor:
            cursor.execute(
                "INSERT INTO myapp_leave (uid, tbegin, tend, reason) VALUES (%s, %s, %s, %s)",
                [uid,tbegin,tend,reason]
            )
            if cursor.rowcount == 1:
                return Response({"success": True}, status=200)
            else:
                return Response({"success": False, "message": "添加失败"}, status=400)
    except Exception as e:
        print(f"Error registering leave: {e}")
        return Response({"success": False, "message": "服务器错误"}, status=500)
    
