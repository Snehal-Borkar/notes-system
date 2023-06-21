from django.contrib import admin
from .models import Text, Video
# Register your models here.
 
@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ['text_id','title','text', 'created_by', 'updated_by']

@admin.register(Video)
class TextAdmin(admin.ModelAdmin):
    list_display = ['video_id','title','description', 'created_by', 'updated_by']