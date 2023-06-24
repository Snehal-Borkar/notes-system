from drf_yasg import openapi

permission_param = openapi.Parameter(
    "permission",
    openapi.IN_QUERY,
    description="Access to permission",
    type=openapi.TYPE_STRING,
    enum=["admin", "read_only", "editor"],
    required=True,
)

note_type_param = openapi.Parameter(
    "note_type",
    openapi.IN_QUERY,
    description="Type of note",
    type=openapi.TYPE_STRING,
    enum=["text", "video"],
    required=True,
)

text_properties = {
    "text_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Id of the text"),
    "title": openapi.Schema(type=openapi.TYPE_STRING),
    "text": openapi.Schema(type=openapi.TYPE_STRING),
    "created_by": openapi.Schema(type=openapi.TYPE_INTEGER),
    "updated_by": openapi.Schema(type=openapi.TYPE_INTEGER),
    "permission": openapi.Schema(type=openapi.TYPE_STRING),
}
video_properties = {
    "video_id": openapi.Schema(
        type=openapi.TYPE_INTEGER, description="Id of the video"
    ),
    "title": openapi.Schema(type=openapi.TYPE_STRING),
    "description": openapi.Schema(type=openapi.TYPE_STRING),
    "video": openapi.Schema(type=openapi.TYPE_STRING),
    "created_by": openapi.Schema(type=openapi.TYPE_INTEGER),
    "updated_by": openapi.Schema(type=openapi.TYPE_INTEGER),
    "permission": openapi.Schema(type=openapi.TYPE_STRING),
}

get_all_notes_responses = {
    200: openapi.Response(
        description="Successful response for note_type *text* ",
        schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=text_properties,
            ),
        ),
    ),
    "200 CASE 2 ": openapi.Response(
        description="Successful response for note_type *video* ",
        schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=video_properties,
            ),
        ),
    ),
}

get_user_note_response = {
    200: openapi.Response(
        description="Successful response for note_type *text* ",
        schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=text_properties,
            ),
        ),
    ),
    "200 CASE 2 ": openapi.Response(
        description="Successful response for note_type *video* ",
        schema=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=video_properties,
            ),
        ),
    ),
}

share_note_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "note_type": openapi.Schema(type=openapi.TYPE_STRING, enum=["text", "video"]),
        "share_with": openapi.Schema(
            type=openapi.TYPE_STRING, description="username of note receiver"
        ),
        "permission": openapi.Schema(
            type=openapi.TYPE_STRING, enum=["read_only", "editor"]
        ),
    },
    required=["note_type", "share_with", "permission"],
)

update_note_request_body = ""
# update_note_request_body = openapi.Schema(
#     type=openapi.TYPE_OBJECT,
#     properties={
#         "title": openapi.Schema(type=openapi.TYPE_STRING),
#         "text": openapi.Schema(type=openapi.TYPE_STRING ),
#         "description": openapi.Schema(type=openapi.TYPE_STRING), 
#         # 'video': openapi.Schema(type=openapi.TYPE_FILE),
#     },
# )

video_param = openapi.Parameter(
    "video",
    openapi.IN_FORM,
    description="Type of note",
    type=openapi.TYPE_FILE,  
)

openapi.Parameter(
            name='video',
            in_=openapi.IN_FORM,
            type=openapi.TYPE_FILE,
        ),

