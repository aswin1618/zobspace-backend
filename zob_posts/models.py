from django.db import models
from zob_artists.models import User
import os
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

from zob_artists.models import Follow


def generate_unique_filename(instance, filename):
    # Generate a unique filename using UUID
    unique_filename = f'{uuid.uuid4().hex}{os.path.splitext(filename)[1]}'
    # Return the unique filename
    return os.path.join('audio/', unique_filename)


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username')
    audio_file = models.FileField(upload_to=generate_unique_filename)
    caption = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    collaboration = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def display_name(self):
        return str(self)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"Post #{self.id} by {self.author.username}"

    def get_original_post_author(self):
        original_post = self
        while original_post.collaboration:
            original_post = original_post.collaboration
        return original_post.author

    def get_authors_along_collaboration_chain(self):
        authors = []
        current_post = self.collaboration
        while current_post:
            if current_post.author != self.author:
                authors.append(current_post.author)
            current_post = current_post.collaboration

        return authors

    def author_profile_pic(self):
        return self.author.artistprofile.profile_picture.url


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment #{self.id} by {self.author.username} on Post #{self.post.id}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=255)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    is_read = models.BooleanField(default=False)
    username = models.CharField(max_length=255)


@receiver(post_save, sender=Follow)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.following.user,
            notification_type='follow',
            username=instance.follower.username
        )
