from rest_framework import serializers
from .models import CommunityPost, Comment, Like
from core.serializers import FinancialGoalSerializer, TransactionSerializer
from core.models import FinancialGoal, Transaction
from users.utils.user_utils import calculate_user_savings


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at"]

    def get_author(self, obj):
        return {"id": obj.author.id, "username": obj.author.username}


class CommunityPostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    goal = FinancialGoalSerializer(source="shared_goal", read_only=True)
    transaction = TransactionSerializer(source="shared_transaction", read_only=True)
    shared_goal = serializers.PrimaryKeyRelatedField(
        queryset=FinancialGoal.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    shared_transaction = serializers.PrimaryKeyRelatedField(
        queryset=Transaction.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = CommunityPost
        fields = [
            "id",
            "author",
            "content",
            "goal",
            "transaction",
            "shared_goal",
            "shared_transaction",
            "likes_count",
            "comments_count",
            "comments",
            "created_at",
        ]

    def get_author(self, obj):
        user = obj.author
        total_savings = calculate_user_savings(user)

        if total_savings >= 60:
            rating = "Expert Saver"
        elif total_savings >= 30:
            rating = "Pro Saver"
        elif total_savings >= 15:
            rating = "Growing Saver"
        elif total_savings > 0:
            rating = "New Saver"
        else:
            rating = "Getting Started"

        return {
            "id": user.id,
            "username": user.username,
            "savings_rating": rating,
        }

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

