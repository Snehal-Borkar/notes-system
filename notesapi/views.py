from django.shortcuts import render
import io
from rest_framework.parsers import JSONParser
from .models import Text, Video
from .serializers import TextSerializer, VideoSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .custom_swagger import note_type_param, permission_param, get_all_notes_responses


@swagger_auto_schema(
    method="get",
    manual_parameters=[permission_param, note_type_param],
    responses=get_all_notes_responses,
)
@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_all_user_notes(request):
    """**Description**
    Api is used to get all the users notes based on request permission :
    1. If permission request is *admin* api will return all notes created by user.
    2. If permission request is *read_only* api will return all notes where user can only read the notes.
    3. If permission request is *read_write* api will return all notes where other user share the note with him with read_write access.
    """
    user = User.objects.get(username=request.user)
    note_type = request.query_params.get("note_type")
    permission = request.query_params.get("permission")

    if not note_type:
        return Response({"message": "missing mandatory param 'note_type'"})
    if note_type not in ["text", "video"]:
        return Response({"message": "Invalid 'note_type'"})
    if not permission:
        return Response({"message": "missing mandatory param 'permission'"})
    if permission not in ["admin", "read_only", "read_write"]:
        return Response({"message": "Invalid 'permission'"})

    if note_type == "text":
        Media = Text
        Serializer = TextSerializer
    elif note_type == "video":
        Media = Video
        Serializer = VideoSerializer

    if permission == "read_only":
        notes = Media.objects.filter(read_access_to=user)
    elif permission == "read_write":
        notes = Media.objects.filter(write_access_to=user)
    elif permission == "admin":
        notes = Media.objects.filter(created_by=user)

    serializer = Serializer(notes, context={"request": request}, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method="get",
    manual_parameters=[note_type_param],
    responses=get_all_notes_responses,
)
@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def user_notes(request, note_id): 
    user = User.objects.get(username=request.user)
    note_type = request.query_params.get("note_type")
    if not note_type:
        return Response({"message": "missing mandetory param 'note_type'"})
    if note_type not in ["text", "video"]:
        return Response({"message": "Invalid note_type"}) 
    try:
        if note_type == "text": 
            note = Text.objects.filter(
                Q(text_id=note_id)
                & (
                    Q(created_by=user)
                    | Q(read_access_to=user)
                    | Q(write_access_to=user)
                )
            ).distinct() 
            serializer = TextSerializer(
                note, context={"request": request}, many=True
            )

        if note_type == "video":
            note = Video.objects.filter(
                Q(video_id=note_id)
                & (
                    Q(created_by=user)
                    | Q(read_access_to=user)
                    | Q(write_access_to=user)
                )
            ).distinct()
            serializer = VideoSerializer(
                note, context={"request": request}, many=True
            )

    except ObjectDoesNotExist:
        return Response({"error": "User is not allowed to access the resource"})
    return Response(serializer.data)


@api_view(["PUT"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def share_notes(request, note_id):
    if request.method == "PUT":
        user = User.objects.get(username=request.user)
        note_type = request.data.get("note_type")
        permission = request.data.get("permission")
        share_with = request.data.get("share_with")
        mandetory_fields = ["note_type", "permission", "share_with"]
        if not note_type:
            return Response({"message": "missing mandetory param 'note_type'"})
        if note_type not in ["text", "video"]:
            return Response({"message": "Invalid note_type"})
        if note_type == "text":
            try:
                #     # Retrieve the Text object you want to share
                text = Text.objects.get(text_id=note_id)
            except ObjectDoesNotExist:
                return Response({"error": "resource does not exists"})

            try:
                #     # # Retrieve the User object you want to share with
                user_to_share = User.objects.get(username=share_with)
            except ObjectDoesNotExist:
                return Response({"error": f"user '{share_with}' does not exists"})
            user_id = user.id
            print("user_id: ", user_id)
            # text = Text.objects.get(text_id=note_id)
            print(
                "//////////////////////////////",
                text.read_access_to.values_list("id", flat=True),
            )
            if text.created_by == user_id:
                has_permission_to = "write"
            elif user_id in text.write_access_to.values_list("id", flat=True):
                has_permission_to = "write"
            elif user_id in text.read_access_to.values_list("id", flat=True):
                has_permission_to = "read"
            else:
                return Response({"error": "User is not allowed to access the resource"})

            if permission == "read" and (
                has_permission_to == "read" or has_permission_to == "write"
            ):
                # Add the user to the read_access_to or write_access_to relationship
                text.read_access_to.add(user_to_share)
            elif permission == "write" and has_permission_to == "write":
                text.write_access_to.add(user_to_share)
            else:
                return Response(
                    {
                        "error": "User is not allowed to share resource with write permission"
                    }
                )

            # Save the changes
            text.save()
        return Response({"message": "successfully shared the resource"})


@api_view(["PUT"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def update_notes(request, note_id):
    if request.method == "PUT":
        user = User.objects.get(username=request.user)

        note_type = request.data.get("note_type")
        if not note_type:
            return Response({"message": "missing mandetory param 'note_type'"})
        if note_type not in ["text", "video"]:
            return Response({"message": "Invalid note_type"})
        if note_type == "text":
            try:
                text = Text.objects.get(text_id=note_id)
                if (
                    text.created_by != user.id
                    and user.id not in text.write_access_to.values_list("id", flat=True)
                ):
                    return Response(
                        {"error": "User is not allowed to access the resource"}
                    )

                title_value = request.data.get("title")
                text_value = request.data.get("text")
                if title_value:
                    text.title = title_value
                if text_value:
                    text.text = text_value
                text.save()

            except ObjectDoesNotExist:
                return Response({"error": "resource does not exists"})
        return Response({"message": "Updated Successfully"})


@api_view(["POST"])
def create_new_user(request):
    body = request.data
    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        return Response({"message": "username or password is missing"})
    User.objects.create_user(username=username, password=password)
    return Response({"message": "successfully created user"})
