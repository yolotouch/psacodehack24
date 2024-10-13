from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    department = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    years_of_experience = models.FloatField()
    skillset = models.TextField()  # A comma-separated string of skills
    project_success_rate = models.FloatField()

    def __str__(self):
        return self.name


class Question(models.Model):
    mentor_name = models.CharField(max_length=100)
    mentee_name = models.CharField(max_length=100)
    question_text = models.TextField()
    answer_text = models.TextField(blank=True, null=True)  # For mentor's response
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question from {self.mentee_name} to {self.mentor_name}"
