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
        if user == obj.created_by:
            permission =  'admin'
        if user in obj.write_access_to.all()  :
            permission =  'read_write'
        elif user in obj.read_access_to.all():
            permission =  'only_read' 
        return permission

class VideoSerializer(serializers.ModelSerializer):
    # class Meta:
    #     model = Text
    #     fields = ('video_id', 'title', 'text', 'created_by', 'updated_by')
    
    permission = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['video_id', 'title', 'description','video', 'created_by', 'updated_by', 'permission']

    def get_permission(self, obj):
        user = self.context['request'].user 
        if user == obj.created_by:
            permission =  'admin'
        if user in obj.write_access_to.all()  :
            permission =  'read_write'
        elif user in obj.read_access_to.all():
            permission =  'read_only' 
        return permission