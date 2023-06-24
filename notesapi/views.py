from .models import Text, Video
from .serializers import TextSerializer, VideoSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from .custom_swagger import (
    note_type_param,
    permission_param,
    get_all_notes_responses,
    share_note_request_body,
    update_note_request_body,
    video_param,
)
from rest_framework import status
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser


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
    3. If permission request is *editor* api will return all notes where other user share the note with him with editor access.
    """
    user = User.objects.get(username=request.user)
    note_type = request.query_params.get("note_type")
    permission = request.query_params.get("permission")

    if not note_type:
        return Response(
            {"error": "missing mandatory param 'note_type'"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if note_type not in ["text", "video"]:
        return Response(
            {"error": "Invalid 'note_type'"}, status=status.HTTP_400_BAD_REQUEST
        )
    if not permission:
        return Response(
            {"error": "missing mandatory param 'permission'"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if permission not in ["admin", "read_only", "editor"]:
        return Response(
            {"error": "Invalid 'permission'"}, status=status.HTTP_400_BAD_REQUEST
        )

    if note_type == "text":
        Media = Text
        Serializer = TextSerializer
    elif note_type == "video":
        Media = Video
        Serializer = VideoSerializer

    if permission == "read_only":
        notes = Media.objects.filter(read_access_to=user)
    elif permission == "editor":
        notes = Media.objects.filter(write_access_to=user)
    elif permission == "admin":
        notes = Media.objects.filter(created_by=user)

    serializer = Serializer(notes, context={"request": request}, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


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
        return Response(
            {"error": "missing mandatory param 'note_type'"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if note_type not in ["text", "video"]:
        return Response(
            {"error": "Invalid note_type"}, status=status.HTTP_400_BAD_REQUEST
        )
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
            serializer = TextSerializer(note, context={"request": request}, many=True)

        if note_type == "video":
            note = Video.objects.filter(
                Q(video_id=note_id)
                & (
                    Q(created_by=user)
                    | Q(read_access_to=user)
                    | Q(write_access_to=user)
                )
            ).distinct()
            serializer = VideoSerializer(note, context={"request": request}, many=True)

    except ObjectDoesNotExist:
        return Response(
            {"error": "User is not allowed to access the resource"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    return Response(serializer.data)


@swagger_auto_schema(
    method="put",
    request_body=share_note_request_body,
    responses={200: "Success"},
)
@api_view(["PUT"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def share_notes(request, note_id):
    """**Description**
    Api is used to share the notes among other user based on what permission user has.
    - If user has admin access to the resource, he can share note with either read_only or editor permission,
    - If user has only read access, he cannot give write access for the resource,
    - If user has editor access, he can share the resource with, either read_only or editor access to others.
    """
    user = User.objects.get(username=request.user)
    note_type = request.data.get("note_type")
    permission = request.data.get("permission")
    share_with = request.data.get("share_with")
    mandatory_fields = ["note_type", "permission", "share_with"]
    missing_fields = set(mandatory_fields) - set((request.data).keys())
    if missing_fields:
        return Response(
            {"error": f"missing mandatory field {missing_fields}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if note_type not in ["text", "video"]:
        return Response(
            {"error": "Invalid 'note_type'"}, status=status.HTTP_400_BAD_REQUEST
        )
    if permission not in ["read_only", "editor"]:
        return Response(
            {"error": "Invalid 'permission'"}, status=status.HTTP_400_BAD_REQUEST
        )
    if note_type == "text":
        try:
            # Retrieve the Text object you want to share
            note = Text.objects.get(text_id=note_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "resource does not exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    if note_type == "video":
        try:
            # Retrieve the Video object you want to share
            note = Video.objects.get(video_id=note_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": "resource does not exists"},
                status=status.HTTP_404_NOT_FOUND,
            )

    try:
        # Retrieve the User object you want to share with
        user_to_share = User.objects.get(username=share_with)
    except ObjectDoesNotExist:
        return Response(
            {"error": f"user '{share_with}' does not exists"},
            status=status.HTTP_404_NOT_FOUND,
        )
    if note.created_by == user or user.id in note.write_access_to.values_list(
        "id", flat=True
    ):
        user_has_permission = "editor"
    # elif user.id in note.write_access_to.values_list("id", flat=True):
    #     user_has_permission = "editor"
    elif user.id in note.read_access_to.values_list("id", flat=True):
        user_has_permission = "read_only"
    else:
        return Response(
            {"error": "User is not allowed to access the resource"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if permission == "read_only" and (
        user_has_permission == "read_only" or user_has_permission == "editor"
    ):
        # Add the user to the read_access_to or write_access_to relationship
        note.read_access_to.add(user_to_share)
        note.write_access_to.remove(user_to_share)
    elif permission == "editor" and user_has_permission == "editor":
        note.write_access_to.add(user_to_share)
        note.read_access_to.remove(user_to_share)
    else:
        return Response(
            {"error": "User is not allowed to share resource with editor permission"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Save the changes
    note.save()
    return Response(
        {"message": "successfully shared the resource"}, status=status.HTTP_200_OK
    )


from rest_framework import parsers
from drf_yasg import openapi

  
@api_view(["PUT"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def update_notes(request, note_id):
    """**Description**
    Api id used to updated the resource only if user has either created or has editor access
    """
    if request.method == "PUT":
        user = User.objects.get(username=request.user)

        note_type = request.query_params.get("note_type")
        if not note_type:
            return Response(
                {"error": "missing mandatory param 'note_type'"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if note_type not in ["text", "video"]:
            return Response(
                {"error": "Invalid note_type"}, status=status.HTTP_400_BAD_REQUEST
            )
        if note_type == "text":
            try:
                text = Text.objects.get(text_id=note_id)
            except ObjectDoesNotExist:
                return Response(
                    {"error": "resource does not exists"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if (
                text.created_by != user
                and user.id not in text.write_access_to.values_list("id", flat=True)
            ):
                return Response(
                    {"error": "User is not allowed to update the resource"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            title_value = request.data.get("title")
            text_value = request.data.get("text")
            if title_value:
                text.title = title_value
            if text_value:
                text.text = text_value
            text.updated_by = user
            text.save()

        if note_type == "video":
            try:
                video = Video.objects.get(video_id=note_id)
            except ObjectDoesNotExist:
                return Response(
                    {"error": "resource does not exists"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if (
                video.created_by != user
                and user.id not in video.write_access_to.values_list("id", flat=True)
            ):
                return Response(
                    {"error": "User is not allowed to update the resource"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            title_value = request.data.get("title")
            desc_value = request.data.get("description")
            video_value = request.FILES.get("video")
            content_type = video_value.content_type
            if title_value:
                video.title = title_value
            if desc_value:
                video.description = desc_value
            if video_value and "video" in content_type:
                video.video = video_value
            else:
                return Response(
                    {"error": "Invalid file type"}, status=status.HTTP_400_BAD_REQUEST
                )

            video.updated_by = user
            video.save()

        return Response({"message": "Updated Successfully"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def create_new_user(request):
    body = request.data
    username = body.get("username")
    password = body.get("password")
    if not username or not password:
        return Response(
            {"error": "username or password is missing"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    User.objects.create_user(username=username, password=password)
    return Response(
        {"message": "successfully created user"}, status=status.HTTP_201_CREATED
    )
