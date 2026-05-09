from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
import sympy as sp
from .models import Test, Question, TestAttempt
from solver.models import QueryLog
from solver.math_engine import solve_math_problem

def check_answer(user_ans, correct_ans):
    """
    Direct 'Option Match' grading logic.
    Supports string flexibility and integer/float equivalence.
    """
    u = str(user_ans).strip().lower()
    c = str(correct_ans).strip().lower()
    
    if not u: return False
    
    # 1. Direct string match
    if u == c: return True
    
    # 2. Integer/Float match (e.g., 4 matches 4.0)
    try:
        if float(u) == float(c): return True
    except:
        pass
        
    return False

@login_required
def test_window_view(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all()
    return render(request, 'quiz/test_window.html', {
        'test': test,
        'questions': questions,
    })

@login_required
def submit_test_view(request, test_id):
    if request.method == 'POST':
        test = get_object_or_404(Test, id=test_id)
        questions = test.questions.all()
        score = 0
        answer_report = {"correct": [], "incorrect": []}
        
        for question in questions:
            user_answer = request.POST.get(f'q_{question.id}', '')
            is_correct = check_answer(user_answer, question.correct_answer)
            
            if is_correct:
                score += 1
                answer_report["correct"].append(question.id)
            else:
                answer_report["incorrect"].append(question.id)
            
            # SAVE TO QUERYLOG FOR GROWTH GRAPH
            QueryLog.objects.create(
                user=request.user,
                problem_type='test_question',
                category=question.subject,
                expression=question.text,
                result=user_answer,
                is_correct=is_correct
            )
        
        time_taken = request.POST.get('time_taken', 0)
        
        attempt = TestAttempt.objects.create(
            user=request.user,
            test=test,
            score=score,
            time_taken_seconds=int(time_taken),
            answer_report=answer_report
        )
        
        return redirect('test_result', attempt_id=attempt.id)
    return redirect('dashboard')

@login_required
def test_result_view(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, user=request.user)
    test = attempt.test
    total_questions = test.questions.count()
    percentage = (attempt.score / total_questions * 100) if total_questions > 0 else 0
    avg_time = (attempt.time_taken_seconds / total_questions) if total_questions > 0 else 0
    
    # Detailed Question Report (All questions, no derivations)
    report_data = attempt.answer_report # {"correct": [ids...], "incorrect": [ids...]}
    all_questions = test.questions.all()
    question_reports = []
    
    for q in all_questions:
        is_correct = q.id in report_data.get('correct', [])
        # Retrieve the user's raw answer from logs
        try:
            log = QueryLog.objects.filter(user=request.user, expression=q.text).latest('timestamp')
            user_ans = log.result
        except:
            user_ans = "No Answer"
            
        question_reports.append({
            'question': q,
            'user_answer': user_ans,
            'is_correct': is_correct
        })

    # Topic Mastery Analysis
    incorrect_ids = report_data.get('incorrect', [])
    incorrect_questions = Question.objects.filter(id__in=incorrect_ids)
    subjects_to_practice = list(set(q.subject for q in incorrect_questions))

    context = {
        'attempt': attempt,
        'percentage': round(percentage, 1),
        'avg_time': round(avg_time, 1),
        'subjects_to_practice': subjects_to_practice,
        'question_reports': question_reports,
        'total_questions': total_questions,
    }
    return render(request, 'quiz/test_result.html', context)

@login_required
def test_list_view(request):
    tests = Test.objects.all()
    return render(request, 'quiz/index.html', {'tests': tests})
@user_passes_test(lambda u: u.is_admin)
def teacher_dashboard_view(request):
    User = get_user_model()
    students = User.objects.filter(is_student=True)
    all_attempts = TestAttempt.objects.all().order_by('-completed_at')
    
    if request.method == 'POST' and 'create_question' in request.POST:
        text = request.POST.get('text')
        q_type = request.POST.get('type')
        option_a = request.POST.get('option_a')
        option_b = request.POST.get('option_b')
        option_c = request.POST.get('option_c')
        option_d = request.POST.get('option_d')
        correct_answer = request.POST.get('correct_answer')
        subject = request.POST.get('subject')
        
        Question.objects.create(
            text=text,
            type=q_type,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer,
            subject=subject
        )
        return redirect('teacher_dashboard')

    context = {
        'students': students,
        'all_attempts': all_attempts,
    }
    return render(request, 'quiz/teacher_dashboard.html', context)
