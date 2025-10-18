from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CommunityPost, Like
from .serializers import CommunityPostSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly
from django.shortcuts import render

from rest_framework.pagination import PageNumberPagination

class CommunityPostPagination(PageNumberPagination):
    page_size = 20

class CommunityPostViewSet(viewsets.ModelViewSet):
    queryset = (
        CommunityPost.objects
        .select_related('author', 'shared_goal', 'shared_transaction')
        .prefetch_related('comments', 'likes')
        .order_by('-created_at')
    )
    serializer_class = CommunityPostSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    pagination_class = CommunityPostPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            return Response({"message": "Unliked"}, status=status.HTTP_200_OK)
        return Response({"message": "Liked"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticated])
    def comments(self, request, pk=None):
        post = self.get_object()

        if request.method == 'GET':
            comments = post.comments.select_related('author').all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=request.user, post=post)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def liked(self, request):
        """Return all posts liked by the current user."""
        liked_posts = CommunityPost.objects.filter(likes__user=request.user).order_by('-created_at')
        serializer = self.get_serializer(liked_posts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        """Return all posts created by the current user."""
        user_posts = CommunityPost.objects.filter(author=request.user).order_by('-created_at')
        serializer = self.get_serializer(user_posts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    
def community_page(request):
    return render(request, "community/communities.html")
