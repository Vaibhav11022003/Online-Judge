from django.forms import ModelForm
from .models import CodeSubmission,Problem,TestCases,DummyTestCases

class CodeSubmissionForm(ModelForm):
    class Meta:
        model=CodeSubmission
        fields='__all__'
        exclude=['output_data','status','passed_testcases','user','problem']

class ProblemForm(ModelForm):
    class Meta:
        model=Problem
        fields='__all__'
        exclude=['user']
class TestCasesForm(ModelForm):
    class Meta:
        model=TestCases
        fields='__all__'
        exclude=['problem']

class DummyTestCasesForm(ModelForm):
    class Meta:
        model=DummyTestCases
        fields='__all__'
        exclude=['problem']
