from rest_framework import serializers

from ChordNote import settings

class UserInformationSerializers(serializers.Serializer):
    email = serializers.CharField()
    nickname = serializers.CharField()
    sex = serializers.IntegerField()
    birth_date = serializers.CharField()
    description = serializers.CharField()
    # For Image
    image = serializers.SerializerMethodField()
    def get_image(self,row):
        return "http://" + settings.HOST + ":" + settings.PORT + "/media/" + str(row.image)


class BookSerializers(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    version = serializers.CharField()
    description = serializers.CharField()
    chapter_id_list = serializers.SerializerMethodField()
    chapter_name_list = serializers.SerializerMethodField()
    profile_photo_url = serializers.SerializerMethodField()
    def get_chapter_id_list(self, row):
        res = []
        chapter_list = row.chapter_set.all()
        for item in chapter_list:
            res.append(item.id)
        return res

    def get_chapter_name_list(self,row):
        res = []
        chapter_list = row.chapter_set.all()
        for item in chapter_list:
            res.append(item.name)
        return res

    def get_profile_photo_url(self,row):
        return "http://" + settings.HOST + ":" + settings.PORT + "/media/" + str(row.profile_photo)


class ChapterSerializers(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    #version = serializers.CharField()
    description = serializers.CharField()
    file_list = serializers.SerializerMethodField()

    def get_file_list(self, row):
        file_list = dict()
        file_list['file_main'] = "http://" + settings.HOST + ":" + settings.PORT + "/media/" + str(row.file_main)
        file_list['file_exercises'] = "http://" + settings.HOST + ":" + settings.PORT + "/media/" + str(row.file_exercises)
        file_list['file_answer'] = "http://" + settings.HOST + ":" + settings.PORT + "/media/" + str(row.file_answer)
        return file_list