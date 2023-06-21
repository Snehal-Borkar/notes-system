from rest_framework import serializers
from .models import Text, Video


# class TextSerializer(serializers.Serializer):
#     text = serializers.CharField(max_length=1000)
#     image = serializers.ImageField()
#     video = serializers.FileField()


class TextSerializer(serializers.ModelSerializer):
    # class Meta:
    #     model = Text
    #     fields = ('text_id', 'title', 'text', 'created_by', 'updated_by')

    permission = serializers.SerializerMethodField()

    class Meta:
        model = Text
        fields = ['text_id', 'title', 'text', 'created_by', 'updated_by', 'permission']

    def get_permission(self, obj):
        user = self.context['request'].user
        if user in obj.read_access_to.all():
            permission =  'read'
        if user in obj.write_access_to.all() or user == obj.created_by :
            permission =  'write'
        else:
            permission = None
        return permission

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = ('video_id', 'title', 'text', 'created_by', 'updated_by')