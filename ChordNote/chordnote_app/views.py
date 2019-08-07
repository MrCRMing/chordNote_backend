import datetime

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
    # 先不考虑全局认证
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
    def get(self, request, *args, **kwargs):  # 发送邮箱验证码
        try:
            ret = dict()
            email = request._request.GET.get("email", None)
            # 为用户登录创建验证码
            checkcode = md5(email)[:5]
            # 将验证码保存在数据库中(这里原本是保存在session中，但因为前端一直调用失败，暂时改为保存在数据库表中）
            checkcode_obj = models.checkcode.objects.filter(email=email).first()
            # 若未有相关记录则创建，若已有相关记录则更新
            if not checkcode_obj:
                new_checkcode = models.checkcode()
                new_checkcode.email = email
                new_checkcode.code = checkcode
                new_checkcode.save()
            else:
                checkcode_obj.code = checkcode
                checkcode_obj.save()
            # 发送邮件
            title = "乐学课程表APP注册"
            msg = "您好！感谢您注册乐学课程表APP，这是您本次注册使用的验证码 " + checkcode + " ,该验证码将在5分钟后过期，如过期请重新点击发送，获得新的验证码"
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

    def post(self, request, *args, **kwargs):  # 注册

        ret = {"code": 1000, "msg": None}
        try:
            email = request._request.POST.get("email", None)
            user_password = request._request.POST.get("user_pwd", None)
            checkcode = request._request.POST.get("checkcode", None)
            name = request._request.POST.get("name", None)
            time_now=datetime.datetime.now()
            interval=datetime.timedelta(hours=8,minutes=5)#时间格式问题 UTC比当地时间少8个小时，minutes是设置验证码时效为5分钟
            time_early=time_now-interval
            time_now=time_now-datetime.timedelta(hours=8)

            checkcode_obj=models.checkcode.objects.filter(email=email).first()
            if not checkcode_obj:
                ret["code"] = 1003
                ret["msg"] = "该邮箱未申请过验证码"
                return Response(ret, status.HTTP_200_OK)
            else:
                new_checkcode_obj=models.checkcode.objects.filter(email=email,update_time__range=(time_early,time_now)).first()

                if not new_checkcode_obj:
                    ret["code"] = 1004
                    ret["msg"] = "验证码已过期，请重新获取"
                    return Response(ret, status.HTTP_200_OK)
                else:
                    correct_checkcode=new_checkcode_obj.code
                    if correct_checkcode==checkcode:
                        db_search = models.Users.objects.filter(email=email).first()
                        if db_search == None:
                            temp = models.Users()
                            temp.email = email
                            temp.password = user_password
                            temp.name = name
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
                    else:
                        ret["code"] = 1002
                        ret["msg"] = "验证码错误"
                        return Response(ret, status.HTTP_200_OK)

        except:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)
