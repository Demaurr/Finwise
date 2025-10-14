from django.db.models import Sum, Avg, Q
from core.models import Transaction, FinancialGoal
from datetime import timedelta, date


def analyze_user_finances(user):
    transactions = Transaction.objects.filter(user=user)
    goals = FinancialGoal.objects.filter(user=user)

    total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    net_savings = total_income - total_expense
    savings_rate = round((net_savings / total_income) * 100, 2) if total_income > 0 else 0

    category_spending = (
        transactions.filter(type='expense')
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    last_6_months = date.today() - timedelta(days=180)
    monthly_data = (
        transactions.filter(date__gte=last_6_months)
        .values('date__month')
        .annotate(
            income=Sum('amount', filter=Q(type='income')),
            expense=Sum('amount', filter=Q(type='expense')),
        )
        .order_by('date__month')
    )

    goal_progress = [
        {
            'title': g.title,
            'progress': g.progress,
            'target': float(g.target_amount),
            'current': float(g.current_amount)
        }
        for g in goals
    ]

    return {
        'total_income': float(total_income),
        'total_expense': float(total_expense),
        'net_savings': float(net_savings),
        'savings_rate': savings_rate,
        'category_spending': list(category_spending),
        'monthly_trend': list(monthly_data),
        'goal_progress': goal_progress,
    }


def compare_with_region(user):
    user_location = getattr(user, 'location', None)
    if not user_location:
        return None

    from users.models import UserProfile

    region_users = UserProfile.objects.filter(location__city=user_location.get("city", ""))
    region_transactions = Transaction.objects.filter(user__in=region_users)

    user_income = Transaction.objects.filter(user=user, type='income').aggregate(total=Sum('amount'))['total'] or 0
    user_expense = Transaction.objects.filter(user=user, type='expense').aggregate(total=Sum('amount'))['total'] or 0

    region_income = region_transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
    region_expense = region_transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
    region_user_count = region_users.count() or 1

    last_6_months = date.today() - timedelta(days=180)
    region_monthly_avg = (
        region_transactions.filter(date__gte=last_6_months)
        .values('date__month')
        .annotate(
            avg_income=Avg('amount', filter=Q(type='income')),
            avg_expense=Avg('amount', filter=Q(type='expense')),
        )
        .order_by('date__month')
    )

    region_category_avg = (
        region_transactions.filter(type='expense')
        .values('category')
        .annotate(avg_spent=Avg('amount'))
        .order_by('-avg_spent')
    )

    comparison = {
        'user_income': float(user_income),
        'user_expense': float(user_expense),
        'region_avg_income': float(region_income / region_user_count),
        'region_avg_expense': float(region_expense / region_user_count),
        'region_monthly_avg': list(region_monthly_avg),
        'region_category_avg': list(region_category_avg),
        'region': user_location
    }

    return comparison


def generate_insights(personal_data, comparison_data=None):
    insights = []

    if personal_data['savings_rate'] >= 30:
        insights.append("💰 Excellent savings rate — you’re saving over 30% of your income.")
    elif personal_data['savings_rate'] < 10:
        insights.append("⚠️ Your savings rate is low — consider reducing discretionary expenses.")

    if personal_data['category_spending']:
        top_category = max(personal_data['category_spending'], key=lambda x: x['total'])
        insights.append(f"🧾 Your highest spending category is {top_category['category']} (${top_category['total']:.2f}).")

    if comparison_data:
        if personal_data['total_income'] > comparison_data['region_avg_income'] * 1.1:
            insights.append("🌟 Your income is above your city average — strong financial position.")
        elif personal_data['total_income'] < comparison_data['region_avg_income'] * 0.9:
            insights.append("📊 Your income is below your city average — consider ways to grow earnings.")

        if personal_data['total_expense'] > comparison_data['region_avg_expense'] * 1.2:
            insights.append("⚠️ You’re spending more than most in your region — review expense habits.")
        elif personal_data['total_expense'] < comparison_data['region_avg_expense'] * 0.8:
            insights.append("✅ You’re spending less than average — efficient budgeting!")

    for goal in personal_data['goal_progress']:
        if goal['progress'] >= 90:
            insights.append(f"🎯 You’re about to reach your goal: {goal['title']}!")
        elif goal['progress'] < 25:
            insights.append(f"🚀 You’re just starting on {goal['title']} — stay consistent!")

    return insights


def full_user_analytics(user):
    personal = analyze_user_finances(user)
    # print(personal)
    comparison = compare_with_region(user)
    insights = generate_insights(personal, comparison)
    
    return {
        'personal': personal,
        'comparison': comparison,
        'insights': insights
    }
