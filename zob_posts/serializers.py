from rest_framework import serializers
from .models import Post, Comment,Notification


class PostSerializer(serializers.ModelSerializer):
    total_likes = serializers.SerializerMethodField()
    original_post_author = serializers.SerializerMethodField()
    authors_along_collab = serializers.SerializerMethodField()
    display_name = serializers.ReadOnlyField()
    author_profile_pic = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'audio_file', 'caption', 'created_at', 'likes', 'display_name', 'updated_at',
                  'total_likes',
                  'original_post_author', 'authors_along_collab', 'author_profile_pic']

    def get_total_likes(self, post):
        return post.total_likes()

    def get_original_post_author(self, post):
        return post.get_original_post_author().username

    def get_authors_along_collab(self, post):
        return [author.username for author in post.get_authors_along_collaboration_chain()]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class PostCaptionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['caption']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id','notification_type', 'post', 'is_read', 'username')