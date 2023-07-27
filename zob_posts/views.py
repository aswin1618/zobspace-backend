from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.response import Response
from io import BytesIO
from .models import Post, Comment, Notification
from zob_artists.models import Follow
from .serializers import PostSerializer, CommentSerializer, PostCaptionUpdateSerializer,NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from pydub import AudioSegment
import tempfile
from django.core.files import File
from rest_framework.permissions import IsAdminUser

# Create your views here.


class PostUploadView(APIView):
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)

        if serializer.is_valid():
            # Get the audio file from the request
            audio_file = request.FILES.get('audio_file')
            caption = serializer.validated_data.get('caption')
            # Save the post with the unique filename as the audio_file value
            post = serializer.save(author=request.user, audio_file=audio_file, caption=caption)
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class LikePostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        post_id = request.data.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            serializer = PostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            post.likes.add(request.user)
            serializer = PostSerializer(post)
            if post.author != request.user:
                Notification.objects.create(
                    user=post.author,
                    notification_type='like',
                    post=post,
                    username=request.user.username
                )
            return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def list_all_posts(request):
    posts = Post.objects.exclude(author=request.user)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(['GET'])
def my_posts(request):
    posts = Post.objects.filter(author=request.user)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(['GET'])
def posts_of_followed_users(request):
    # Get the current user
    user = request.user

    # Get the IDs of the followed profiles
    followed_profiles = Follow.objects.filter(follower=user).values_list('following', flat=True)

    # Retrieve posts from the followed profiles
    followed_posts = Post.objects.filter(author__artistprofile__in=followed_profiles).order_by('-created_at')

    serializer = PostSerializer(followed_posts, many=True)
    return Response(serializer.data, status=HTTP_200_OK)

@api_view(['POST'])
def caption_update_view(request):
    post_id = request.data.get('post_id')
    caption = request.data.get('caption')
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({'error': 'post not found'}, status=status.HTTP_404_NOT_FOUND)

    author = post.author
    if request.user == author:
        serializer = PostCaptionUpdateSerializer(instance=post, data={'caption': caption}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    else:
        return Response({'error': 'You are not authorized to update this post.'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
def post_delete(request):
    post_id = request.data.get('post_id')
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    if request.user == author:
        post.delete()
        return Response({'message': 'Post deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    else:
        return Response({'error': 'You are not authorized to delete this post.'}, status=status.HTTP_403_FORBIDDEN)





@api_view(['POST'])
def post_collab(request, format=None):
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        post_id = request.data.get('post_id')
        post = Post.objects.get(id=post_id)
        audio_1 = post.audio_file
        audio_2 = request.FILES.get('audio_file')
        caption = serializer.validated_data.get('caption')

        # Load both audio files using Pydub
        audio_segment_1 = AudioSegment.from_file(BytesIO(audio_1.read()))
        audio_segment_2 = AudioSegment.from_file(BytesIO(audio_2.read()))

        # Overlay the audio files
        output_audio = audio_segment_1.overlay(audio_segment_2)

        # Export the output audio to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            output_audio.export(temp_file.name, format='wav')

            # Create a Django File object from the temporary file
            temp_django_file = File(temp_file)

            # Assign the temporary file to the audio_file field
            serializer.validated_data['audio_file'] = temp_django_file

            # Create the collaboration post
            collaboration_post = serializer.save(author=request.user, caption=caption)

            # Link the collaboration post to the original post
            post.collaboration = collaboration_post
            post.save()

        return Response({'collaboration_post_id': collaboration_post.id})

    return Response(serializer.errors, status=400)


@api_view(['GET'])
def notifications(request):
    notification = Notification.objects.filter(user=request.user)
    serializer = NotificationSerializer(notification, many=True)
    inverted_notifications = serializer.data[::-1]
    return Response(inverted_notifications)


@api_view(['GET'])
def unread_notification_count(request):
    user = request.user
    count = Notification.objects.filter(user=user, is_read=False).count()
    data = {'count': count}
    return Response(data)


@api_view(['POST'])
def mark_notification_as_read(request):
    notification_id = request.data.get('notification_id')
    if notification_id is None:
        return Response({'error': 'Notification ID is required.'}, status=400)

    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found.'}, status=404)

    notification.is_read = True
    notification.save()
    return Response({'message': 'Notification marked as read.'})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def posts_list_admin(request):
    posts = Post.objects.all()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(['GET'])
def get_comments_for_post(request, postid):
    post = get_object_or_404(Post, id=postid)
    comments = Comment.objects.filter(post=post)

    serializer = CommentSerializer(comments, many=True)
    data = serializer.data
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Require authentication for this view
def create_comment(request):
    data = request.data
    # postId= request.data.get('post_id')
    # data['post'] = Post.objects.get(id=postId)
    data['author'] = request.user.id  # Set the author using request.user.id

    serializer = CommentSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)