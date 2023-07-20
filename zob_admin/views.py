from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from zob_posts.models import Post


@api_view(['GET'])
def monthly_post_count(request):
    # Query the database to get the monthly post count
    if request.user.is_superuser:
        monthly_count = Post.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(
            count=Count('id')).order_by('month')

        # Prepare the data for the bar graph
        labels = [item['month'].strftime('%B %Y') for item in monthly_count]
        data = [item['count'] for item in monthly_count]

        # Return the data as JSON response
        return Response({'labels': labels, 'data': data})
    return Response({'error': 'Artist not found.'}, status=HTTP_400_BAD_REQUEST)
