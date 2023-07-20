from django.urls import path
from .views import monthly_post_count

urlpatterns = [
        path('monthly_post_count/', monthly_post_count, name='monthly_post_count'),

]
