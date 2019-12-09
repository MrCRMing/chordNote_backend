from django.db import models
import datetime, os
from ChordNote import settings

def get_user_image_path(instance, filename):
    return os.path.join("user_image", instance.email, filename)


def get_image_path(instance, filename):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    year, month, day = date.split("-")
    return os.path.join("image", year, month, day, filename)


def get_musci_file_path(instance, filename):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    year, month, day = date.split("-")
    return os.path.join("music", year, month, day, filename)


def get_profile_photo_path(instance, filename):
    return os.path.join("book", str(instance.name), filename)


def get_content_file_path(instance, filename):
    return os.path.join("content_file", str(instance.name), filename)


class Checkcode(models.Model):
    class Meta:
        db_table = "checkcode"

    email = models.CharField(max_length=30, primary_key=True)
    code = models.CharField(max_length=10)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    update_time = models.DateTimeField(auto_now=True, null=True)


class User(models.Model):
    class Meta:
        db_table = "user"

    email = models.CharField(max_length=32, primary_key=True)
    nickname = models.CharField(max_length=32, null=True)
    password = models.CharField(max_length=32, null=False)
    gender = models.IntegerField(null=True)
    birth_date = models.CharField(max_length=16, null=True)
    description = models.CharField(max_length=64, null=True)
    photo_url = models.CharField(max_length=64, null=True)

class Book(models.Model):
    class Meta:
        db_table = "book"

    name = models.CharField(max_length=128, null=False)
    description = models.CharField(max_length=500, null=True)
    profile_photo = models.ImageField(upload_to=get_profile_photo_path, null=True)


class Chapter(models.Model):
    class Meta:
        db_table = "chapter"
        unique_together = ("name", "book")  # 这是重点

    name = models.CharField(max_length=128, null=False)
    description = models.CharField(max_length=128, null=True)

    book = models.ForeignKey("Book", on_delete=models.CASCADE, null=True)


class Period(models.Model):
    class Meta:
        db_table = "period"

    name = models.CharField(max_length=128, null=False)
    content_file = models.FileField(upload_to=get_content_file_path, null=True)

    chapter = models.ForeignKey("Chapter", on_delete=models.CASCADE, null=True)


class Question(models.Model):
    class Meta:
        db_table = "question"

    stem = models.CharField(max_length=500, null=False)  # 题干

    period = models.ForeignKey("Period", on_delete=models.CASCADE, null=True)


class Option(models.Model):
    class Meta:
        db_table = "option"

    content = models.CharField(max_length=200, null=False)  # 题干
    is_right = models.BooleanField(default=False)

    question = models.ForeignKey("Question", on_delete=models.CASCADE, null=True)


class Image(models.Model):
    class Meta:
        db_table = "image"

    url = models.TextField(null=True)
    image = models.ImageField(upload_to=get_image_path)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    update_time = models.DateTimeField(auto_now=True, null=True)

    # 建立外键
    question = models.ForeignKey("Question", on_delete=models.CASCADE, null=True)
    moment = models.ForeignKey("Moment", on_delete=models.CASCADE, null=True)



class Moment(models.Model):
    class Meta:
        db_table = "moment"

    title = models.CharField(max_length=50, null=False)
    content = models.CharField(max_length=500, null=False)
    like_num = models.IntegerField(default=0)
    publish_time = models.DateTimeField(auto_now_add=True, null=False)
    music_file = models.FileField(upload_to=get_musci_file_path, null=True)

    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True)


class Comment(models.Model):
    class Meta:
        db_table = "comment"

    content = models.CharField(max_length=500, null=False)
    like_num = models.IntegerField(default=0)
    publish_time = models.DateTimeField(auto_now_add=True, null=False)

    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True)


class User_collect_Comment(models.Model):
    # 用于记载评论和评论收藏者的关联信息
    class Meta:
        db_table = "user_collect_comment"

    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    comment = models.ForeignKey("Comment", on_delete=models.CASCADE, null=True)

class User_collect_Moment(models.Model):
    # 用于记载评论和评论收藏者的关联信息
    class Meta:
        db_table = "user_collect_moment"

    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    moment = models.ForeignKey("Moment", on_delete=models.CASCADE, null=True)