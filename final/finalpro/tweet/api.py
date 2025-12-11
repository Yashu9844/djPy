from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Tweet
from .serializers import TweetSerializer
from .permissions import IsOwnerOrReadOnly


class TweetViewSet(viewsets.ModelViewSet):
    queryset = Tweet.objects.all().order_by('-created_at')
    serializer_class = TweetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['text', 'user__username']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at', '-id']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
