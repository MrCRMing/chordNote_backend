import datetime

from rest_framework import serializers

from ChordNote import settings


class UserInformationSerializers(serializers.Serializer):
    email = serializers.CharField()
    nickname = serializers.CharField()
    gender = serializers.IntegerField()
    birth_date = serializers.CharField()
    description = serializers.CharField()
    # For Image
    image = serializers.SerializerMethodField()

    def get_image(self, row):
        return row.photo_url


class BookSerializers(serializers.Serializer):
    id_book = serializers.IntegerField(source='id')
    book_name = serializers.CharField(source='name')
    # version = serializers.CharField()
    # description = serializers.CharField()
    # chapter_id_list = serializers.SerializerMethodField()
    # chapter_name_list = serializers.SerializerMethodField()
    profile_photo_url = serializers.SerializerMethodField()

    def get_chapter_id_list(self, row):
        res = []
        chapter_list = row.chapter_set.all()
        for item in chapter_list:
            res.append(item.id)
        return res

    def get_chapter_name_list(self, row):
        res = []
        chapter_list = row.chapter_set.all()
        for item in chapter_list:
            res.append(item.name)
        return res

    def get_profile_photo_url(self, row):
        return "http://" + settings.HOST + ":" + settings.PORT + "/media/" + str(row.profile_photo)


class ChapterSerializers(serializers.Serializer):
    id_chapter = serializers.IntegerField(source="id")
    title = serializers.CharField(source="name")
    period_title_list = serializers.SerializerMethodField()
    period_id_list = serializers.SerializerMethodField()

    # version = serializers.CharField()
    # description = serializers.CharField()
    # file_list = serializers.SerializerMethodField()

    def get_period_title_list(self, row):
        res = []
        period_list = row.period_set.all()
        for item in period_list:
            res.append(item.name)
        return res

    def get_period_id_list(self, row):
        res = []
        period_list = row.period_set.all()
        for item in period_list:
            res.append(item.id)
        return res
    # def get_file_list(self, row):
    #     file_list = dict()
    #     file_list['file_main'] = "http://" + settings.HOST + ":" + settings.PORT + "/media/" + str(row.file_main)
    #     file_list['file_exercises'] = "http://" + settings.HOST + ":" + settings.PORT + "/media/" + str(
    #         row.file_exercises)
    #     file_list['file_answer'] = "http://" + settings.HOST + ":" + settings.PORT + "/media/" + str(row.file_answer)
    #     return file_list


class MomentSerializers(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField()
    like_num = serializers.IntegerField()
    publish_time = serializers.SerializerMethodField()
    email = serializers.CharField(source='user.email')
    nickname = serializers.CharField(source='user.nickname')
    image_url = serializers.CharField(source='user.photo_url')
    music_url = serializers.SerializerMethodField()
    image_urls = serializers.SerializerMethodField()

    @staticmethod
    def get_music_url(row):
        if str(row.music_file) != '':
            url = "http://" + settings.HOST + ":" + settings.PORT + "/media/" + str(row.music_file)
            return url
        else:
            return ''

    @staticmethod
    def get_image_urls(row):
        image_list = row.image_set.all()
        ret = [image.url for image in image_list]
        return ret

    @staticmethod
    def get_publish_time(row):
        publish_time = row.publish_time
        local_datetime = publish_time
        Local_datetime = datetime.datetime.strftime(local_datetime, '%Y-%m-%d %H:%M:%S')
        return Local_datetime


class CommentSerializers(serializers.Serializer):
    id = serializers.IntegerField()
    content = serializers.CharField()
    like_num = serializers.IntegerField()
    publish_time = serializers.SerializerMethodField()
    email = serializers.CharField(source='user.email')
    nickname = serializers.CharField(source='user.nickname')
    image_url = serializers.CharField(source='user.photo_url')

    @staticmethod
    def get_publish_time(row):
        publish_time = row.publish_time
        local_datetime = publish_time
        Local_datetime = datetime.datetime.strftime(local_datetime, '%Y-%m-%d %H:%M:%S')
        return Local_datetime


class PeriodSerializers(serializers.Serializer):
    id_period = serializers.IntegerField(source="id")
    title = serializers.CharField(source="name")
    # 估计也是手动填url的了，默认认为里面的内容就是完整的URL
    content = serializers.CharField(source="content_file")


class OptionSerializers(serializers.Serializer):
    content = serializers.CharField()
    is_right = serializers.BooleanField()


class QuestionSerializers(serializers.Serializer):
    id_question = serializers.IntegerField(source="id")
    stem = serializers.CharField()
    image_url = serializers.SerializerMethodField()
    option_list = serializers.SerializerMethodField()

    def get_image_url(self, row):
        image = row.image_set.first()
        if not image:
            return None
        else:
            return image.url

    def get_option_list(self, row):
        options = row.option_set.all()
        ser = OptionSerializers(instance=options, many=True)
        return ser.data


class CommentSerializers2(serializers.Serializer):
    id_comment = serializers.IntegerField(source="id")
    num_of_good = serializers.IntegerField(source="like_num")
    content = serializers.CharField()
    email = serializers.CharField(source='user.email')
    nickname = serializers.CharField(source='user.nickname')
    image_url = serializers.CharField(source='user.photo_url')
    publish_time = serializers.SerializerMethodField()

    def get_publish_time(self, row):
        publish_time = row.publish_time
        print(publish_time)
        local_datetime = publish_time
        Local_datetime = datetime.datetime.strftime(local_datetime, '%Y-%m-%d %H:%M:%S')
        return Local_datetime
