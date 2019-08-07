from django.db import models


# Create your models here.
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

    email = models.CharField(max_length=30,primary_key=True)
    code = models.CharField(max_length=10)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    update_time = models.DateTimeField(auto_now=True, null=True)
