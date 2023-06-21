# Generated by Django 4.1.2 on 2023-06-18 15:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="NoteBook",
            fields=[
                ("book_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=150, unique=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Video",
            fields=[
                ("video_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "title",
                    models.CharField(default="title", max_length=150, unique=True),
                ),
                (
                    "description",
                    models.TextField(blank=True, default="text", null=True),
                ),
                ("video", models.FileField(upload_to="videos/")),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "notebook",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="notesapi.notebook",
                    ),
                ),
                (
                    "read_access_to",
                    models.ManyToManyField(
                        blank=True,
                        related_name="read_video_access",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="updated_videos",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "write_access_to",
                    models.ManyToManyField(
                        blank=True,
                        related_name="write_video_access",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Text",
            fields=[
                ("text_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "title",
                    models.CharField(default="title", max_length=150, unique=True),
                ),
                ("text", models.TextField(default="text")),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "notebook",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="notesapi.notebook",
                    ),
                ),
                (
                    "read_access_to",
                    models.ManyToManyField(
                        blank=True,
                        related_name="read_access",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="updated_texts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "write_access_to",
                    models.ManyToManyField(
                        blank=True,
                        related_name="write_access",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
