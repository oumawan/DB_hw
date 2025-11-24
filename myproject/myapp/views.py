from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    print(f"Received login attempt with email: {email} and password: {password}")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT uid, email, password, name, depotID FROM myapp_admin WHERE email = %s LIMIT 1",
                [email]
            )
            row = cursor.fetchone()
            if row:
                uid, db_email, db_password, name, depotID = row
                if password == db_password:
                    print(f"Login successful for email: {email}")
                    return Response({
                        "success": True,
                        "user": {
                            "uid": uid,
                            "email": db_email,
                            "name": name,
                            "depotID": depotID,
                            "is_admin": True
                        }
                    }, status=200)
                else:
                    return Response({"success": False}, status=200)
            cursor.execute(
                "SELECT uid, email, password, name, depotID, license FROM myapp_driver WHERE email=%s LIMIT 1", [email]
            )
            row = cursor.fetchone()
            if row:
                uid, db_email, db_password, name, depotID, license = row
                if password == db_password:
                    print(f"Login successful for email: {email}")
                    return Response({
                        "success": True,
                        "user": {
                            "uid": uid,
                            "email": db_email,
                            "name": name,
                            "depotID": depotID,
                            "license": license,
                            "is_admin": False
                        }
                    }, status=200)
                else:
                    return Response({"success": False}, status=200)
        print(f"Login failed: no matching user for email: {email}")
        return Response({"success": False}, status=200)
    except Exception as e:
        print(f"Error during login: {e}")
        return Response({"message": "服务器错误"}, status=500)
    
@api_view(['POST'])
def driver_change_profile(request):
    print("Received driver profile change request with data:", request.data)
    name = request.data.get('name')
    email = request.data.get('email')
    uid = request.data.get('uid')
    license = request.data.get('license')
    depotID = request.data.get('depotID')
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE myapp_driver SET name=%s, email=%s, license=%s, depotID=%s WHERE uid=%s",
                [name, email, license, depotID, uid]
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
                "SELECT uid, name, email, license FROM myapp_driver WHERE depotID=%s", [depotID]
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
def add_driver(request):
    name = request.data.get('name')
    email = request.data.get('email')
    license = request.data.get('license')
    depotID = request.data.get('depotID')
    print(f"Received add driver request with name: {name}, email: {email}, license: {license}, depotID: {depotID}")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO myapp_driver (name, email, license, depotID) VALUES (%s, %s, %s, %s)",
                [name, email, license, depotID]
            )
            if cursor.rowcount == 1:
                return Response({"success": True}, status=200)
            else:
                return Response({"success": False, "message": "添加失败"}, status=400)
    except Exception as e:
        print(f"Error adding driver: {e}")
        return Response({"success": False, "message": "服务器错误"}, status=500)