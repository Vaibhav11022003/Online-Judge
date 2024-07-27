from django.db import models
from django.contrib.auth.models import User
# Create your models here.

difficulties=[('easy','easy'),
              ('medium' ,'medium'),
              ('hard','hard'),
              ]
topics=[('arrays','arrays'),
        ('strings','strings'),
        ('stack','stack'),
        ('queue','queue'),
        ('priority queue','priority queue'),
        ('DP','DP'),
        ('graphs','graphs'),
        ('maths','maths')]
class Problem(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    difficulty=models.CharField(max_length=100,choices=difficulties)
    topics=models.CharField(max_length=100,choices=topics,default='maths')
    title=models.CharField(max_length=100)
    statement=models.TextField()
    constraints=models.TextField()
    inputs=models.TextField()
    outputs=models.TextField()
    created=models.DateTimeField(auto_now_add=True,null=True)
    
    def __str__(self):
        return self.title

class TestCases(models.Model):
    input_data=models.TextField()
    output_data=models.TextField()
    problem=models.ForeignKey(Problem,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return f"{self.problem}{self.id}"

class DummyTestCases(models.Model):
    input_data=models.TextField()
    output_data=models.TextField()
    body=models.TextField(null=True,blank=True)
    problem=models.ForeignKey(Problem,on_delete=models.CASCADE,null=True)
    def __str__(self):
        return f"{self.problem}{self.id}"

languages=[('py','py'),
           ('cpp','cpp'),
           ]
status_flag=[('passed','passed'),
             ('failed','failed'),
             ('compile-error','compile-error'),
             ('runtime-error','runtime-error'),
             ]
class CodeSubmission(models.Model):
    language=models.CharField(max_length=100, choices=languages)
    code=models.TextField()
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    problem =models.ForeignKey(Problem,on_delete=models.CASCADE,null=True)
    input_data=models.TextField(null=True,blank=True)
    output_data=models.TextField(null=True,blank=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=100,choices=status_flag,default='passed')
    passed_testcases=models.CharField(max_length=100,default='0')
    class Meta:
        ordering=['-timestamp']
    def __str__(self):
        return f"{self.user.username}{self.problem}{self.id}"