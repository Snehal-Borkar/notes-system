from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# class Notes(models.Model):
#     text = models.CharField(max_length=1000)
#     image = models.ImageField(upload_to="images/",null=True)
#     video = models.FileField(upload_to="videos/", null=True)

 

class Text(models.Model):
    text_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150, default="title")
    text = models.TextField(default="text") 
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    updated_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="updated_texts",
    )
    read_access_to = models.ManyToManyField(
        User, blank=True, related_name="read_access"
    )
    write_access_to = models.ManyToManyField(
        User, blank=True, related_name="write_access"
    )


class Video(models.Model):
    video_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=150, default="title")
    description = models.TextField(default="description", null=True, blank=True)
    video = models.FileField(upload_to="videos/") 
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    updated_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="updated_videos",
    )
    read_access_to = models.ManyToManyField(
        User, blank=True, related_name="read_video_access"
    )
    write_access_to = models.ManyToManyField(
        User, blank=True, related_name="write_video_access"
    )
