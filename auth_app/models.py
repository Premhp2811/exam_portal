from django.db import models

class ExamPaper(models.Model):
    # Branch and academic info
    branch = models.CharField(max_length=10)  # cse, ece, mech, etc.
    year = models.CharField(max_length=10)    # first, second, third
    semester = models.CharField(max_length=2)  # 1, 2, 3, 4, 5, 6
    
    # Paper details
    subject = models.CharField(max_length=200)
    paper_type = models.CharField(max_length=50)  # Mid Term, End Sem, etc.
    year_exam = models.CharField(max_length=10)   # 2024, 2023, etc.
    description = models.TextField(blank=True, null=True)
    
    # File
    file = models.FileField(upload_to='exam_papers/')
    
    # Metadata
    uploaded_by = models.CharField(max_length=100)  # Teacher name
    uploaded_at = models.DateTimeField(auto_now_add=True)
    downloads = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.subject} - {self.paper_type} ({self.year_exam})"
    
    class Meta:
        ordering = ['-uploaded_at']
class Syllabus(models.Model):
    # Branch info
    branch = models.CharField(max_length=10)  # cse, ece, mech, etc.
    
    # Syllabus details
    title = models.CharField(max_length=200)
    academic_year = models.CharField(max_length=20)  # 2024-25, 2023-24, etc.
    description = models.TextField(blank=True, null=True)
    
    # File
    file = models.FileField(upload_to='syllabus/')
    
    # Metadata
    uploaded_by = models.CharField(max_length=100)  # Teacher name
    uploaded_at = models.DateTimeField(auto_now_add=True)
    downloads = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.title} - {self.academic_year}"
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name_plural = "Syllabi"