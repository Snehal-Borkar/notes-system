# Generated by Django 4.1.2 on 2023-06-18 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notesapi", "0002_alter_text_title_alter_video_title"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="text",
            name="notebook",
        ),
        migrations.RemoveField(
            model_name="video",
            name="notebook",
        ),
        migrations.DeleteModel(
            name="NoteBook",
        ),
    ]
