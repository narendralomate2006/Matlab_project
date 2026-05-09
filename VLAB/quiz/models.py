from django.db import models
from django.conf import settings

class Question(models.Model):
    QUESTION_TYPES = (
        ('MCQ', 'Multiple Choice Question'),
        ('INT', 'Integer Answer'),
    )
    SUBJECT_CHOICES = (
        ('Math', 'Mathematics'),
        ('Calculus', 'Calculus'),
    )
    
    text = models.TextField()
    type = models.CharField(max_length=3, choices=QUESTION_TYPES, default='MCQ')
    option_a = models.CharField(max_length=255, blank=True, null=True)
    option_b = models.CharField(max_length=255, blank=True, null=True)
    option_c = models.CharField(max_length=255, blank=True, null=True)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    correct_answer = models.CharField(max_length=255)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='Math')

    def __str__(self):
        return f"[{self.subject}] {self.text[:50]}..."

class Test(models.Model):
    title = models.CharField(max_length=255)
    questions = models.ManyToManyField(Question, related_name='tests')
    duration_minutes = models.PositiveIntegerField(default=60)

    def __str__(self):
        return self.title

class TestAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)
    time_taken_seconds = models.PositiveIntegerField(default=0)
    # Stores which question IDs were correct/incorrect
    # Example: {"correct": [1, 3], "incorrect": [2, 4]}
    answer_report = models.JSONField(default=dict)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.test.title} - Score: {self.score}"
