from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import QueryLog
from .math_engine import solve_math_problem
import json

@login_required
def solver_view(request):
    result_data = None
    if request.method == 'POST':
        expression = request.POST.get('expression', '')
        problem_type = request.POST.get('problem_type', 'integral')
        
        result_data = solve_math_problem(expression, problem_type)
        
        # Categorization based on input structure
        category = 'Single Integral'
        if problem_type == 'beta':
            category = 'Beta Function'
        else:
            parts = [p.strip() for p in expression.split(',')]
            # "Two tuples" usually means two variables specified (e.g. x*y, x, y)
            if len(parts) >= 3:
                category = 'Double Integral'
            elif len(parts) == 1:
                # Check for automatic double integral from engine result or expression
                # We can also check if the engine solved it as a double
                category = 'Single Integral'
        
        # Heuristic Difficulty Detection
        difficulty = 'Easy'
        if len(expression) > 25 or 'sin' in expression or 'exp' in expression or category == 'Double Integral':
            difficulty = 'Hard'
        elif len(expression) > 12 or category == 'Beta Function':
            difficulty = 'Medium'
            
        # Save to QueryLog
        QueryLog.objects.create(
            user=request.user,
            problem_type=problem_type,
            category=category,
            difficulty=difficulty,
            expression=expression,
            result=result_data.get('result', result_data.get('error', '')),
            is_correct=result_data.get('success', False)
        )
            
    return render(request, 'solver/solver.html', {'result_data': result_data})

@login_required
def dashboard_view(request):
    queries = QueryLog.objects.filter(user=request.user).order_by('-created_at')
    
    total_solved = queries.filter(is_correct=True).count()
    total_attempts = queries.count()
    mastery_rate = round((total_solved / total_attempts * 100), 1) if total_attempts > 0 else 0
    
    # 7-Day Growth Data
    today = timezone.now().date()
    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    chart_labels = [d.strftime('%b %d') for d in dates]
    chart_data = [queries.filter(created_at__date=d, is_correct=True).count() for d in dates]
    
    # Topic Mastery: Percentage of Success vs Error for each category
    categories_to_check = ['Single Integral', 'Double Integral', 'Beta Function']
    mastery = []
    for cat in categories_to_check:
        qs = queries.filter(category=cat)
        total = qs.count()
        correct = qs.filter(is_correct=True).count()
        # Mastery is success rate
        percentage = round((correct / total * 100), 1) if total > 0 else 0
        mastery.append({'category': cat, 'percentage': percentage})

    context = {
        'queries': queries[:10],
        'total_solved': total_solved,
        'mastery_rate': mastery_rate,
        'mastery': mastery,
        'chart_labels_json': json.dumps(chart_labels),
        'chart_data_json': json.dumps(chart_data)
    }
    return render(request, 'solver/dashboard.html', context)

@login_required
def student_analytics_view(request):
    today = timezone.now().date()
    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    chart_labels = [d.strftime('%b %d') for d in dates]
    chart_data = [QueryLog.objects.filter(user=request.user, created_at__date=d, is_correct=True).count() for d in dates]
    
    categories = ['Single Integral', 'Double Integral', 'Beta Function']
    mastery = []
    for cat in categories:
        qs = QueryLog.objects.filter(user=request.user, category=cat)
        total = qs.count()
        correct = qs.filter(is_correct=True).count()
        percentage = (correct / total * 100) if total > 0 else 0
        mastery.append({'category': cat, 'percentage': round(percentage, 1), 'total': total, 'correct': correct})
        
    return render(request, 'solver/analytics.html', {'chart_labels': chart_labels, 'chart_data': chart_data, 'mastery': mastery})

@user_passes_test(lambda u: u.is_admin)
def admin_dashboard(request):
    today = timezone.now().date()
    total_queries_today = QueryLog.objects.filter(created_at__date=today).count()
    total_queries_all_time = QueryLog.objects.all().count()
    frequent_problems = QueryLog.objects.values('expression', 'category').annotate(count=Count('expression')).order_by('-count')[:5]
    active_students = QueryLog.objects.values('user__username').annotate(query_count=Count('id')).order_by('-query_count')[:5]
    recent_queries = QueryLog.objects.all().order_by('-created_at')[:10]
    
    return render(request, 'solver/admin/analytics.html', locals())
