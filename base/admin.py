from django.contrib import admin
from .models import CodeSubmission,Problem,DummyTestCases,TestCases
# Register your models here.
admin.site.register(CodeSubmission)
admin.site.register(Problem)
admin.site.register(DummyTestCases)
admin.site.register(TestCases)