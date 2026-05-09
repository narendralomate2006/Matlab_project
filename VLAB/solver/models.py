from django.db import models
from django.conf import settings

class QueryLog(models.Model):
    PROBLEM_CHOICES = (
        ('integral', 'Integral'),
        ('beta', 'Beta Function'),
    )
    
    CATEGORY_CHOICES = (
        ('Single Integral', 'Single Integral'),
        ('Double Integral', 'Double Integral'),
        ('Beta Function', 'Beta Function'),
    )
    
    DIFFICULTY_CHOICES = (
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    problem_type = models.CharField(max_length=20, choices=PROBLEM_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Single Integral')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Easy')
    expression = models.CharField(max_length=255)
    result = models.TextField()
    is_correct = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.category} ({self.difficulty}): {self.expression}"
