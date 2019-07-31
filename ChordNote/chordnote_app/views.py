from django.shortcuts import render
from rest_framework.views import APIView
from . import models
from rest_framework.response import Response
from rest_framework import status
from ChordNote import settings
from rest_framework.response import Response
from django.core.mail import send_mail
from django.http import HttpResponse
from rest_framework.decorators import api_view
# Create your views here.

def md5(user_num):
    import hashlib
    import time
    ctime = str(time.time())
    m = hashlib.md5(bytes(user_num, encoding="utf-8"))
    m.update(bytes(ctime, encoding="utf-8"))
    return m.hexdigest()

class AuthView(APIView):
    """"
    用于用户认证登录
    """
    # authentication_classes = []
    #先不考虑全局认证
    def post(self, request, *args, **kwargs):

        ret = {"code": 1000, "msg": None}

        try:
            email = request._request.POST.get("email", None)
            user_password = request._request.POST.get("user_pwd", None)
            obj = models.Users.objects.filter(email=email, password=user_password).first()
            if not obj:
                ret["code"] = 1001
                ret["msg"] = "用户名或密码错误"
                return Response(ret, status.HTTP_200_OK)
            else:

                # 为用户登录创建token
                # token = md5(user_num)
                # 存在就更新，不存在就创建
                # models.UserToken.objects.update_or_create(user=obj, defaults={"token": token})
                # ret["token"] = token
                ret["msg"] = "成功登录"
                ret["email"] = obj.email
                ret["user_pwd"] = obj.password
                ret["user_name"] = obj.name
                return Response(ret, status.HTTP_200_OK)
        except Exception as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegisterView(APIView):
    """"
    用于用户注册
    """
    # authentication_classes = []
    def get(self, request, *args, **kwargs):#发送邮箱验证码
        try:
            ret=dict()
            email=request._request.GET.get("email",None)
            # 为用户登录创建验证码
            checkcode = md5(email)[:5]
            #将验证码保存在session中
            request._request.session["checkcode"]=checkcode
            request._request.session.set_expiry(300)
            #发送邮件
            title = "乐学课程表注册"
            msg = "您好！感谢您注册乐学课程表，这是您本次注册使用的验证码 "+checkcode+" ,该验证码将在5分钟后过期，如过期请重新点击发送，获得新的验证码"
            email_from = settings.DEFAULT_FROM_EMAIL
            reciever = [
                email,
            ]
            # 发送邮件
            send_mail(title, msg, email_from, reciever)
            ret["code"] = 1000
            ret["msg"] = "成功发送验证码"

            return Response(ret, status.HTTP_200_OK)
        except Exception as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request, *args, **kwargs):#注册

        ret = {"code": 1000, "msg": None}
        # try:
        email = request._request.POST.get("email", None)
        user_password = request._request.POST.get("user_pwd", None)
        checkcode = request._request.POST.get("checkcode", None)
        name= request._request.POST.get("name", None)
        if checkcode!=request._request.session["checkcode"]:
            ret["code"]=1002
            ret["msg"] = "验证码错误"
            return Response(ret, status.HTTP_200_OK)
        else:
            db_search = models.Users.objects.filter(email=email).first()
            if db_search==None:
                temp = models.Users()
                temp.email = email
                temp.password = user_password
                temp.name=name
                temp.save()
                ret["code"] = 1000
                ret["msg"] = "成功注册"
                ret["email"] = temp.email
                ret["user_pwd"] = temp.password
                ret["user_name"] = temp.name
                return Response(ret, status.HTTP_200_OK)
            else:
                ret["code"] = 1001
                ret["msg"] = "用户已存在"
                return Response(ret, status.HTTP_200_OK)
        # except:
        #     return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)









