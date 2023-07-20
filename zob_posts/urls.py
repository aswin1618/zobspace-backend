from django.urls import path

from .views import PostUploadView, LikePostAPIView, CreateCommentAPIView, list_all_posts, my_posts, \
    posts_of_followed_users, caption_update_view, post_delete, post_collab, notifications, unread_notification_count,\
    mark_notification_as_read,posts_list_admin

urlpatterns = [

    path('explore/', list_all_posts, name='list_all_posts'),
    path('my_posts/', my_posts, name='my_posts'),
    path('home_posts/', posts_of_followed_users, name='home_posts'),
    path('upload_post/', PostUploadView.as_view(), name='post_upload'),
    path('posts/like/', LikePostAPIView.as_view(), name='like-post'),
    path('posts/comment/', CreateCommentAPIView.as_view(), name='create-comment'),
    path('posts/update_caption/', caption_update_view, name='caption_update_view'),
    path('posts/delete/', post_delete, name='post_delete'),
    path('collab_post/', post_collab, name='collab_post'),
    path('notifications/', notifications, name='notifications'),
    path('notification_count/', unread_notification_count, name='notification_count'),
    path('mark_notif/', mark_notification_as_read, name='mark_notif'),
    path('posts_list_admin/', posts_list_admin, name='posts_list_admin'),
]
