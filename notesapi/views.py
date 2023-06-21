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


@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_all_user_notes(request):
    # content = {
    #     "user": str(request.user),  # `django.contrib.auth.User` instance.
    #     "auth": str(request.auth),  # None
    # }
    # print(content)
    user = User.objects.get(username=request.user)
    note_type = request.query_params.get("note_type")
    access_read_only_shared = request.query_params.get("access_read_only_shared")
    access_read_only_shared = (
        True if access_read_only_shared.lower() == "true" else False
    )

    access_write_shared = request.query_params.get("access_write_shared")
    access_write_shared = True if access_write_shared.lower() == "true" else False

    if not note_type:
        return Response({"message": "missing mandetory param note_type"})
    if note_type not in ["text", "video"]:
        return Response({"message": "Invalid note_type"})

    # if access_read_only_shared and access_write_shared:
    # print("//////////////////user_id", user_id.id)
    # user_id = 5  # Example user ID
    # user = User.objects.get(pk=user_id)
    #     access_read_only_text_notes = Text.objects.filter(write_access_to__in=user)
    #     access_users_write_text_notes = Text.objects.filter(read_access_to=user)
    #     print("///////////////////////////////access_read_only_text_notes :",access_read_only_text_notes)
    #     serializer = TextSerializer(access_read_only_text_notes, many=True)
    #     print("///////////////////////////////",serializer.data)
    if access_read_only_shared:
        access_read_only_text_notes = Text.objects.filter(read_access_to=user)
        serializer = TextSerializer(access_read_only_text_notes, many=True)
    elif access_write_shared:
        access_users_write_text_notes = Text.objects.filter(write_access_to=user)
        serializer = TextSerializer(access_users_write_text_notes, many=True)

    else:
        users_all_text_notes = Text.objects.filter(created_by=user)
        serializer = TextSerializer(users_all_text_notes, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def user_notes(request, note_id):
    if request.method == "GET":
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
                return Response({"error": "User is not allowed to share resource with write permission"})

            # Save the changes
            text.save()
        return Response({"message": "successfully shared the resource"})


@api_view(["POST"])
def create_new_user(request):
    body = request.data
    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        return Response({"message": "username or password is missing"})
    User.objects.create_user(username=username, password=password)
    return Response({"message": "successfully created user"})
