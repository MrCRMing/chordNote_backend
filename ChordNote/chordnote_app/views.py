import datetime
import hashlib
from collections import OrderedDict

from django.shortcuts import render
from django.utils.datetime_safe import time
from rest_framework.views import APIView

from chordnote_app import serializers
from . import models
from rest_framework.response import Response
from rest_framework import status
from ChordNote import settings
from rest_framework.response import Response
from django.core.mail import send_mail
import time


# Create your views here.

def md5(user_num):
    import hashlib
    import time
    ctime = str(time.time())
    m = hashlib.md5(bytes(user_num, encoding="utf-8"))
    m.update(bytes(ctime, encoding="utf-8"))
    return m.hexdigest()


def rename(origin_name):
    locations = str(origin_name).find(".")
    extension = origin_name[locations:]
    name = origin_name[:locations]
    namestring = name + str(time.time())
    md5 = hashlib.md5(namestring.encode('utf-8')).hexdigest()
    return md5[:10] + extension


class AuthView(APIView):
    """"
    用于用户认证登录
    """

    # authentication_classes = []
    # 先不考虑全局认证
    def post(self, request, *args, **kwargs):

        ret = {"code": 1000, "msg": None}

        # try:
        email = request._request.POST.get("email", None)
        user_password = request._request.POST.get("user_pwd", None)
        obj = models.User.objects.filter(email=email, password=user_password).first()
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
            return Response(ret, status.HTTP_200_OK)
        # except Exception as e:
        #     return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            checkcode_obj = models.Checkcode.objects.filter(email=email).first()
            # 若未有相关记录则创建，若已有相关记录则更新
            if not checkcode_obj:
                new_checkcode = models.Checkcode()
                new_checkcode.email = email
                new_checkcode.code = checkcode
                new_checkcode.save()
            else:
                checkcode_obj.code = checkcode
                checkcode_obj.save()
            # 发送邮件
            title = "晓声APP注册"
            msg = "您好！感谢您注册晓声APP，这是您本次注册使用的验证码 " + checkcode + " ,该验证码将在5分钟后过期，如过期请重新点击发送，获得新的验证码"
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
        # try:
        ret = {"code": 1000, "msg": None}
        email = request._request.POST.get("email", None)
        user_password = request._request.POST.get("user_pwd", None)
        checkcode = request._request.POST.get("checkcode", None)
        nickname = request._request.POST.get("nickname", None)

        gender = request._request.POST.get("gender", None)
        birth_date = request._request.POST.get("birth_date", None)
        description = request._request.POST.get("description", None)
        try:
            # 从上传的文件中读取头像
            photo = request.FILES['image']
        except:
            # 使用默认用户图片作为默认头像
            photo = None

        # 计算时间 用于判断验证码是否超时
        time_now = datetime.datetime.now()
        interval = datetime.timedelta(hours=8, minutes=15)  # 时间格式问题 UTC比当地时间少8个小时，minutes是设置验证码时效为5分钟
        time_early = time_now - interval
        time_now = time_now - datetime.timedelta(hours=8)

        checkcode_obj = models.Checkcode.objects.filter(email=email).first()
        if not checkcode_obj:
            ret["code"] = 1003
            ret["msg"] = "该邮箱未申请过验证码"
            return Response(ret, status.HTTP_200_OK)
        else:
            new_checkcode_obj = models.Checkcode.objects.filter(email=email,
                                                                update_time__range=(time_early, time_now)).first()
            if not new_checkcode_obj:
                ret["code"] = 1004
                ret["msg"] = "验证码已过期，请重新获取"
                return Response(ret, status.HTTP_200_OK)
            else:
                correct_checkcode = new_checkcode_obj.code
                if correct_checkcode == checkcode:
                    db_search = models.User.objects.filter(email=email).first()
                    if db_search == None:
                        # 创建新的用户
                        temp = models.User()
                        temp.email = email
                        temp.password = user_password
                        temp.nickname = nickname
                        temp.gender = gender
                        temp.description = description
                        temp.birth_date = birth_date
                        # 保存用户头像，若没上传，则直接使用默认头像
                        if photo != None:
                            # 先创建头像
                            photo_obj = models.Image(image=photo)
                            imageName = str(photo_obj.image.name)
                            locations = str(imageName).find(".")
                            extension = imageName[locations:]
                            name = imageName[:locations]
                            namestring = name + str(time.time())
                            md5 = hashlib.md5(namestring.encode('utf-8')).hexdigest()
                            photo_obj.image.name = md5[:10] + extension
                            date = datetime.date.today().strftime("%Y/%m/%d/")
                            photo_obj.url = "http://" + settings.HOST + ":" + settings.PORT + "/media/image/" + date + photo_obj.image.name
                            photo_obj.save()

                            temp.photo_url = photo_obj.url
                            temp.save()
                        else:
                            temp.photo_url = settings.DEFAULT_PHOTO_URL
                            temp.save()
                        ret["code"] = 1000
                        ret["msg"] = "成功注册"
                        return Response(ret, status.HTTP_200_OK)
                    else:
                        ret["code"] = 1001
                        ret["msg"] = "用户已存在"
                        return Response(ret, status.HTTP_200_OK)
                else:
                    ret["code"] = 1002
                    ret["msg"] = "验证码错误"
                    return Response(ret, status.HTTP_200_OK)
        # except:
        #     return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserInformationView(APIView):
    # 修改用户信息
    def put(self, request, *args, **kwargs):
        email = request.data.get("email", None)
        obj = models.User.objects.filter(email=email).first()
        if not obj:
            ret = {
                'code': 1001,
                'msg': '用户不存在'
            }
            return Response(ret, status.HTTP_200_OK)
        else:
            obj.nickname = request.data.get("nickname", obj.nickname)
            obj.gender = request.data.get("gender", obj.gender)
            obj.birth_date = request.data.get("birth_date", obj.birth_date)
            obj.description = request.data.get("description", obj.description)
            try:
                photo = request.FILES['image']
            except:
                photo = None

            if photo != None:
                # 先创建头像
                photo_obj = models.Image(image=photo)
                imageName = str(photo_obj.image.name)
                locations = str(imageName).find(".")
                extension = imageName[locations:]
                name = imageName[:locations]
                namestring = name + str(time.time())
                md5 = hashlib.md5(namestring.encode('utf-8')).hexdigest()
                photo_obj.image.name = md5[:10] + extension
                date = datetime.date.today().strftime("%Y/%m/%d/")
                photo_obj.url = "http://" + settings.HOST + ":" + settings.PORT + "/media/image/" + date + photo_obj.image.name
                photo_obj.save()
                obj.photo_url = photo_obj.url
                obj.save()
            else:
                obj.save()
            ret = {
                "code": 1000,
                "msg": "修改用户信息成功"
            }
            return Response(ret, status.HTTP_200_OK)

    # 获得用户信息
    def get(self, request, *args, **kwargs):
        email = request.GET.get("email", None)
        obj = models.User.objects.filter(email=email).first()
        if not obj:
            ret = {
                'code': 1001,
                'msg': '用户不存在'
            }
            return Response(ret, status.HTTP_200_OK)
        else:
            ser = serializers.UserInformationSerializers(instance=obj, many=False)
            ret = {
                "code": 1000,
                "msg": "获取成功",
                "user_information": ser.data
            }
            return Response(ret, status.HTTP_200_OK)


class BookView(APIView):
    def post(self, request, *args, **kwargs):  # create,
        # method = request.data.get("method",None)
        # if method == 'create':
        name = request.data.get("name", None)
        version = request.data.get("version", None)
        temp = models.Book.objects.filter(name=name, version=version).first()
        if not temp:
            description = request.data.get("description", None)
            book = models.Book()
            book.name = name
            book.version = version
            book.description = description
            book.profile_photo = request.FILES['profile_photo']
            book.save()
            ret = {
                "code": 1000,
                "msg": "Create successfully",
                "book_id": book.id
            }
            return Response(ret, status.HTTP_200_OK)
        else:
            ret = {
                "code": 1001,
                "msg": "This version of the book already exists.",
                "book_id": temp.id

            }
            return Response(ret, status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        book_id = request.GET.get("book_id", None)
        book = models.Book.objects.filter(pk=book_id).first()
        if not book:
            ret = {
                "code": 1001,
                "msg": "The book does not exist"
            }
            return Response(ret, status.HTTP_200_OK)
        else:
            ser = serializers.BookSerializers(instance=book, many=False)
            ret = {
                "code": 1000,
                "msg": "Successful access",
                "book": ser.data
            }
            return Response(ret, status.HTTP_200_OK)


class ChapterView(APIView):
    def post(self, request, *args, **kwargs):  # create,
        book_id = request.data.get("book_id", None)
        book = models.Book.objects.filter(pk=book_id).first()
        if not book:
            ret = {
                "code": 1001,
                "msg": "The book does not exist",
                "book_id": book_id
            }
            return Response(ret, status.HTTP_200_OK)
        else:
            name = request.data.get("name", None)
            # version = request.data.get("version", None)
            temp = models.Chapter.objects.filter(name=name, book_id=book_id).first()
            if not temp:
                chapter = models.Chapter()
                chapter.name = name
                # chapter.version = version
                chapter.description = request.data.get("description", None)
                chapter.file_exercises = request.FILES['file_exercises']
                chapter.file_answer = request.FILES['file_answer']
                chapter.file_main = request.FILES['file_main']
                chapter.book = book
                chapter.save()
                ret = {
                    "code": 1000,
                    "msg": "Create successfully",
                    "chapter_id": chapter.id
                }
                return Response(ret, status.HTTP_200_OK)
            else:
                ret = {
                    "code": 1001,
                    "msg": "The chapter already exists.",
                    "chapter_id": temp.id

                }
                return Response(ret, status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        chapter_id = request.GET.get("chapter_id", None)
        chapter = models.Chapter.objects.filter(id=chapter_id).first()
        if not chapter:
            ret = {
                "code": 1001,
                "msg": "The chapter does not exist.",
                "chapter_id": chapter_id

            }
            return Response(ret, status.HTTP_200_OK)
        else:
            ser = serializers.ChapterSerializers(instance=chapter, many=False)
            ret = {
                "code": 1000,
                "msg": "Access successfully",
                "chapter": ser.data
            }
            return Response(ret, status.HTTP_200_OK)


from rest_framework.pagination import CursorPagination


# 用于分页操作
class MyCursorPagination(CursorPagination):
    # 设置每页传10条数据，可上下翻页
    cursor_query_param = 'cursor'
    page_size = 10
    ordering = '-id'
    page_size_query_param = None
    max_page_size = None


class MomentView(APIView):
    # 获得全部动态
    def get(self, request, *args, **kwargs):
        try:
            ret = {"code": 1000, "msg": None}
            moment_list = models.Moment.objects.all()
            # 创建分页对象
            pg = MyCursorPagination()
            # 获取分页的数据
            page_data = pg.paginate_queryset(queryset=moment_list, request=request, view=self)
            # 对数据序列化
            ser = serializers.MomentSerializers(instance=page_data, many=True)

            return Response(OrderedDict([
                ('code', 1000),
                ('msg', '获得动态成功'),
                ('next', pg.get_next_link()),
                ('previous', pg.get_previous_link()),
                ('results', ser.data)
            ]))
        except:
            ret = {
                "code": 1001,
                "msg": "获得动态失败",

            }
            return Response(ret, status.HTTP_200_OK)

    # 添加动态
    def post(self, request, *args, **kwargs):
        try:
            ret = {"code": 1000, "msg": None}
            email = request._request.POST.get("email", None)
            title = request._request.POST.get("title", None)
            content = request._request.POST.get("content", None)
            publish_time = datetime.datetime.now()
            try:
                music = request.FILES['music']
            except:
                music = None

            try:
                images = request.FILES.getlist('images')
            except:
                images = None

            moment_obj = models.Moment()
            moment_obj.title = title
            moment_obj.content = content
            moment_obj.publish_time = publish_time

            user_obj = models.User.objects.filter(email=email).first()
            moment_obj.user = user_obj

            # 给动态添加音乐文件
            if music != None:
                moment_obj.music_file = music

            moment_obj.save()
            # 给动态添加图片，通过绑定图片到该动态上
            if images != None:
                for image_item in images:
                    image_obj = models.Image(image=image_item)
                    imageName = str(image_obj.image.name)
                    locations = str(imageName).find(".")
                    extension = imageName[locations:]
                    name = imageName[:locations]
                    namestring = name + str(time.time())
                    md5 = hashlib.md5(namestring.encode('utf-8')).hexdigest()
                    image_obj.image.name = md5[:10] + extension
                    date = datetime.date.today().strftime("%Y/%m/%d/")
                    image_obj.url = "http://" + settings.HOST + ":" + settings.PORT + "/media/image/" + date + image_obj.image.name
                    image_obj.moment = moment_obj
                    image_obj.save()
            ret = {
                "code": 1000,
                "msg": "发表动态成功",
            }
            return Response(ret, status.HTTP_200_OK)
        except:
            ret = {
                "code": 1001,
                "msg": "发表动态失败",

            }
            return Response(ret, status.HTTP_200_OK)

    # 删除动态
    def delete(self, request, *args, **kwargs):
        ret = {
            'code': 1000,
            'msg': ''
        }
        try:
            moment_id = request.data.get("moment_id", None)
            models.Moment.objects.filter(id=moment_id).delete()

            ret['msg'] = '删除动态成功'
            return Response(ret, status.HTTP_200_OK)
        except:
            ret = {
                'code': 1001,
                'msg': '删除动态失败'
            }
            return Response(ret, status.HTTP_200_OK)

    # 修改动态相关信息，包括点赞/取消点赞，收藏/取消收藏动态
    def put(self, request, *args, **kwargs):
        ret = {
            'code': 1000,
            'msg': ''
        }
        try:
            moment_id = request.data.get("moment_id", None)
            method = request.data.get("method", None)
            if method == "add_like_num":
                moment_obj = models.Moment.objects.filter(id=moment_id).first()
                like_num = moment_obj.like_num
                moment_obj.like_num = like_num + 1
                moment_obj.save()
                ret['code'] = 1000
                ret['msg'] = '点赞成功'
                ret['like_num'] = moment_obj.like_num
                return Response(ret, status.HTTP_200_OK)
            elif method == "cancel_add_like_num":
                moment_obj = models.Moment.objects.filter(id=moment_id).first()
                like_num = moment_obj.like_num
                moment_obj.like_num = like_num - 1
                if moment_obj.like_num < 0:
                    moment_obj.like_num = 0
                moment_obj.save()
                ret['code'] = 1000
                ret['msg'] = '取消点赞成功'
                ret['like_num'] = moment_obj.like_num
                return Response(ret, status.HTTP_200_OK)
            elif method == "collect_moment":
                email = request.data.get("email", None)
                moment_obj = models.Moment.objects.filter(id=moment_id).first()
                user_obj = models.User.objects.filter(email=email).first()
                search_obj = models.User_collect_Moment.objects.filter(user=user_obj, moment=moment_obj).first()
                if search_obj != None:
                    ret['code'] = 1003
                    ret['msg'] = '该收藏已存在'
                    return Response(ret, status.HTTP_200_OK)
                else:
                    relationship_obj = models.User_collect_Moment()
                    relationship_obj.user = user_obj
                    relationship_obj.moment = moment_obj
                    relationship_obj.save()
                    ret['code'] = 1000
                    ret['msg'] = '收藏动态成功'
                    return Response(ret, status.HTTP_200_OK)
            elif method == "cancel_collect_moment":
                email = request.data.get("email", None)
                moment_obj = models.Moment.objects.filter(id=moment_id).first()
                user_obj = models.User.objects.filter(email=email).first()
                models.User_collect_Moment.objects.filter(user=user_obj, moment=moment_obj).delete()
                ret['code'] = 1000
                ret['msg'] = '取消收藏成功'
                return Response(ret, status.HTTP_200_OK)
            else:
                ret['code'] = 1001
                ret['msg'] = '传入参数有误，请确保method参数取值只能为add_like_num、cancel_add_like_num、' \
                             'collect_moment、cancel_collect_moment中的一个'
                return Response(ret, status.HTTP_200_OK)
        except:
            ret = {
                'code': 1002,
                'msg': '未知错误，操作失败'
            }
            return Response(ret, status.HTTP_200_OK)


class Moment_DetailView(APIView):
    # 获得某个用户收藏或发表的动态
    def get(self, request, *args, **kwargs):
        ret = {"code": 1000, "msg": None}
        try:
            email = request.GET.get("email", None)
            type=request.GET.get('type',None)
            if type=="collected":
                relationship_list=models.User_collect_Moment.objects.filter(user__email=email)
                moment_list=[]
                for relationship_item in relationship_list:
                    moment_id=relationship_item.moment_id
                    moment_obj=models.Moment.objects.filter(id=moment_id).first()
                    moment_list.append(moment_obj)
                ser=serializers.MomentSerializers(instance=moment_list,many=True)

                ret["code"] = 1000
                ret["msg"] = '获得收藏的动态成功'
                ret["data"]=ser.data

                return Response(ret, status.HTTP_200_OK)
            elif type=='published':
                user_obj=models.User.objects.filter(email=email).first()
                moment_list=user_obj.moment_set.all()
                ser = serializers.MomentSerializers(instance=moment_list, many=True)
                ret["code"] = 1000
                ret["msg"] = '获得发表的动态成功'
                ret["data"] = ser.data

                return Response(ret, status.HTTP_200_OK)
            else:
                ret["code"] = 1002
                ret["msg"] = 'type值错误，只能为collected和published中的一个'
                return Response(ret, status.HTTP_200_OK)
        except:
            ret = {
                "code": 1001,
                "msg": "未知错误，操作失败",

            }
            return Response(ret, status.HTTP_200_OK)

class Comment_DetailView(APIView):
    # 获得某个用户收藏或发表的评论
    def get(self, request, *args, **kwargs):
        ret = {"code": 1000, "msg": None}
        try:
            email = request.GET.get("email", None)
            type = request.GET.get('type', None)
            if type == "collected":
                relationship_list = models.User_collect_Comment.objects.filter(user__email=email)
                comment_list = []
                for relationship_item in relationship_list:
                    comment_id = relationship_item.comment_id
                    comment_obj = models.Comment.objects.filter(id=comment_id).first()
                    comment_list.append(comment_obj)
                ser = serializers.CommentSerializers(instance=comment_list, many=True)

                ret["code"] = 1000
                ret["msg"] = '获得收藏的动态成功'
                ret["data"] = ser.data

                return Response(ret, status.HTTP_200_OK)
            elif type == 'published':
                user_obj = models.User.objects.filter(email=email).first()
                comment_list = user_obj.comment_set.all()
                ser = serializers.CommentSerializers(instance=comment_list, many=True)
                ret["code"] = 1000
                ret["msg"] = '获得发表的评论成功'
                ret["data"] = ser.data

                return Response(ret, status.HTTP_200_OK)
            else:
                ret["code"] = 1002
                ret["msg"] = 'type值错误，只能为collected和published中的一个'
                return Response(ret, status.HTTP_200_OK)
        except:
            ret = {
                "code": 1001,
                "msg": "未知错误，操作失败",

            }
            return Response(ret, status.HTTP_200_OK)