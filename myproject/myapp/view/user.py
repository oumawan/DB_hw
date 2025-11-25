from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection, transaction

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    print(f"Received login attempt with email: {email} and password: {password}")
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT uid, email, password, name, depotID FROM myapp_user WHERE email = %s LIMIT 1",
                [email]
            )
            row = cursor.fetchone()

            if row:
                uid, db_email, db_password, name, depotID = row
                if password != db_password:
                    return Response({"success": False}, status=200)
                    
                # 用户认证成功，开始鉴权
                
                # depotID为空，则登陆失败
                if depotID is None:
                    return Response({
                            "success": False,
                            "message": "用户未被指定车场，请联系管理员"
                        },status=200)

                # 管理员鉴权
                cursor.execute(
                    "SELECT uid_id FROM myapp_admin WHERE uid_id = %s LIMIT 1", [uid]
                )
                row = cursor.fetchone()
                if row:
                    print(f"Admin login successful for email: {email}")
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

                # 司机鉴权
                cursor.execute(
                    "SELECT uid_id, license FROM myapp_driver WHERE uid_id=%s LIMIT 1", [uid]
                )
                row = cursor.fetchone()
                if row:
                    print(f"Driver login successful for email: {email}")
                    return Response({
                        "success": True,
                        "user": {
                            "uid": uid,
                            "email": db_email,
                            "name": name,
                            "depotID": depotID,
                            "is_admin": False,
                            "license": row[1]
                        }
                    }, status=200)
                print(f"Authentication for user {uid} failed")
                return Response({"success": False, "message":"身份认证失败，请联系管理员"}, status=200)
            else:
                print(f"Login failed: no matching user for email: {email}")
                return Response({"success": False, "message": "邮箱或密码错误"}, status=401)
    except Exception as e:
        print(f"Error during login: {e}")
        return Response({"message": "服务器错误"}, status=500)
    
@api_view(['POST'])
@transaction.atomic
def modifyUserInfo(request):
    print("Received User profile change request with data:", request.data)
    uid = request.data.get('uid')
    name = request.data.get('name')
    email = request.data.get('email')
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE myapp_user SET name=%s, email=%s WHERE uid=%s",
                [name, email, uid]
            )
        return Response({"success": True}, status=200)
    except Exception as e:
        print(f"Error during profile update: {e}")
        return Response({"success": False, "message": "服务器错误"}, status=500)

@api_view(['POST'])
@transaction.atomic
def modifyUserPassword(request):
    print("Received User profile change request with data:", request.data)
    uid = request.data.get('uid')
    password = request.data.get('password')
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE myapp_user SET password=%s WHERE uid=%s",
                [password, uid]
            )
        return Response({"success": True}, status=200)
    except Exception as e:
        print(f"Error during profile update: {e}")
        return Response({"success": False, "message": "服务器错误"}, status=500)