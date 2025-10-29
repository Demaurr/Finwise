from django.shortcuts import render, get_object_or_404, redirect
import json
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from users.models import UserProfile
from community.models import CommunityPost as Post
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncDay, TruncHour
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages
from collections import OrderedDict


def dashboard(request):
    return render(request, 'core/dashboard.html')


def add_transaction_page(request):
    return render(request, 'core/transactions.html')


def add_goal_page(request):
    return render(request, 'core/goals.html')

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    total_users = UserProfile.objects.count()
    total_posts = Post.objects.count()
    recent_users = UserProfile.objects.order_by('-date_joined')[:10]
    recent_posts = Post.objects.order_by('-created_at')[:10]
    now = timezone.now()

    def generate_trends(model, date_field, trunc_func, since, freq, label_fmt):
        """
        Generate continuous date buckets (zero-filled) for charts.
        freq: 'hour', 'day', or 'month'
        """
        qs = (
            model.objects.filter(**{f"{date_field}__gte": since})
            .annotate(period=trunc_func(date_field))
            .values("period")
            .annotate(count=Count("id"))
            .order_by("period")
        )

        data = {x["period"].strftime(label_fmt): x["count"] for x in qs}

        filled = OrderedDict()
        cursor = since
        while cursor <= now:
            if freq == "hour":
                label = cursor.strftime("%H:%M")
                cursor += timedelta(hours=1)
            elif freq == "day":
                label = cursor.strftime("%b %d")
                cursor += timedelta(days=1)
            elif freq == "month":
                label = cursor.strftime("%b %Y")
                next_month = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
                cursor = next_month
            filled[label] = data.get(label, 0)

        return filled

    user_trends = {
        "1D": generate_trends(UserProfile, "date_joined", TruncHour, now - timedelta(days=1), "hour", "%H:%M"),
        "1W": generate_trends(UserProfile, "date_joined", TruncDay, now - timedelta(weeks=1), "day", "%b %d"),
        "1M": generate_trends(UserProfile, "date_joined", TruncDay, now - timedelta(days=30), "day", "%b %d"),
        "6M": generate_trends(UserProfile, "date_joined", TruncMonth, now - timedelta(days=180), "month", "%b %Y"),
        "1Y": generate_trends(UserProfile, "date_joined", TruncMonth, now - timedelta(days=365), "month", "%b %Y"),
    }

    post_trends = {
        "1D": generate_trends(Post, "created_at", TruncHour, now - timedelta(days=1), "hour", "%H:%M"),
        "1W": generate_trends(Post, "created_at", TruncDay, now - timedelta(weeks=1), "day", "%b %d"),
        "1M": generate_trends(Post, "created_at", TruncDay, now - timedelta(days=30), "day", "%b %d"),
        "6M": generate_trends(Post, "created_at", TruncMonth, now - timedelta(days=180), "month", "%b %Y"),
        "1Y": generate_trends(Post, "created_at", TruncMonth, now - timedelta(days=365), "month", "%b %Y"),
    }

    context = {
        "total_users": total_users,
        "total_posts": total_posts,
        "recent_users": recent_users,
        "recent_posts": recent_posts,
        "user_trends": json.dumps(user_trends, default=str),
        "post_trends": json.dumps(post_trends, default=str),
    }

    return render(request, "admin_panel/admin_dashboard.html", context)

@user_passes_test(lambda u: u.is_superuser)
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect('admin_dashboard')
