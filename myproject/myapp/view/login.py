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
                "SELECT uid, email, password, name, depotID FROM myapp_user WHERE email=%s"
                , [email]
            )
            row = cursor.fetchone()
            if row:
                uid, db_email, db_password, name, depotID = row
                print(f"Fetched user from DB: uid={uid}, email={db_email}, name={name}, depotID={depotID}")
                is_admin = False
                if password == db_password:
                    cursor.execute(
                        "SELECT 1 FROM myapp_admin WHERE uid_id=%s", [uid]
                    )
                    if cursor.fetchone():
                        is_admin = True
                        print(f"User {email} is an admin.")
                    else:
                        print(f"User {email} is a driver.")
                    return Response({
                        "success": True,
                        "user" : {
                            "uid": uid,
                            "email": db_email,
                            "name": name,
                            "depotID": depotID,
                            "is_admin": is_admin
                        },
                        "message": "欢迎"
                    }, status=200)
            return Response({"success": False, "message": "邮箱或密码错误"}, status=401)
    except Exception as e:
        print(f"Error during login: {e}")
        return Response({"success": False, "message": "服务器错误"}, status=500)
    