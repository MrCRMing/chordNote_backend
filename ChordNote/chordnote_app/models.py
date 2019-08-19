from django.db import models
import datetime, os


def get_image_path(instance, filename):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    year, month, day = date.split("-")
    return os.path.join("user_image", instance.email, filename)


def get_file_main_path(instance, filename):
    return os.path.join("book", str(instance.book.name),str(instance.book.version),instance.name, 'main',filename)


def get_file_exercises_path(instance, filename):
    return os.path.join("book", str(instance.book.name), str(instance.book.version), instance.name, 'exercises', filename)


def get_file_answer_path(instance, filename):
    return os.path.join("book", str(instance.book.name), str(instance.book.version), instance.name, 'answer', filename)


def get_profile_photo_path(instance, filename):
    return os.path.join("book", str(instance.name),str(instance.version), filename)


class Users(models.Model):
    class Meta:
        db_table = "users"

    email = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)

    # 指定外键

    def __str__(self):
        return "%s-%s-%s" % (self.email, self.name, self.password)


class checkcode(models.Model):
    class Meta:
        db_table = "checkcode"

    email = models.CharField(max_length=30, primary_key=True)
    code = models.CharField(max_length=10)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    update_time = models.DateTimeField(auto_now=True, null=True)


class Users(models.Model):
    class Meta:
        db_table = "users"

    email = models.CharField(max_length=32, primary_key=True)
    nickname = models.CharField(max_length=32, null=True)
    password = models.CharField(max_length=32, null=False)
    sex = models.IntegerField(null=True)
    birth_date = models.CharField(max_length=16, null=True)
    description = models.CharField(max_length=64,null=True)
    # For Image
    image = models.ImageField(upload_to=get_image_path, null=True)

    def __str__(self):
        return "%s-%s-%s-%s-%s-%s" % (self.email, self.name, self.password, self.university, self.major, self.grade)


class Book(models.Model):
    class Meta:
        db_table = "book"
        unique_together = ("name", "version")  # 这是重点

    name = models.CharField(max_length=128,null=False)
    version = models.IntegerField(null=False)
    description = models.CharField(max_length=128,null=True)
    profile_photo = models.ImageField(upload_to=get_profile_photo_path, null=True)



class Chapter(models.Model):
    class Meta:
        db_table = "chapter"
        unique_together = ("name","book")  # 这是重点

    name = models.CharField(max_length=128,null=False)
    #version = models.IntegerField(null=False)
    description = models.CharField(max_length=128,null=True)

    file_main = models.FileField(upload_to=get_file_main_path,null=True)
    file_exercises = models.FileField(upload_to=get_file_exercises_path,null=True)
    file_answer = models.FileField(upload_to=get_file_answer_path,null=True)
    book = models.ForeignKey("Book", on_delete=models.CASCADE,null=True)

