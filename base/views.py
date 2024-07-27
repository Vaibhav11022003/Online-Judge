from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import CodeSubmission,Problem,TestCases,DummyTestCases
from .forms import CodeSubmissionForm,ProblemForm,TestCasesForm,DummyTestCasesForm
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count, Sum, Case, When, IntegerField, Q, OuterRef, Subquery
from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages
import os
import subprocess
import uuid
from pathlib import Path
from django.utils import timezone

topics=['arrays',
        'strings',
        'stack',
        'queue',
        'priority queue',
        'DP',
        'graphs',
        'maths']

def userProfile(request,pk):
    user=User.objects.get(id=int(pk))
    problems_created=user.problem_set.all().order_by('-created')
    submissions=user.codesubmission_set.all()
    submissions_passed=user.codesubmission_set.filter(status='passed')
    # easy_solved=problems_solved.filter(difficulty='easy').count()
    problem_ids = submissions_passed.values_list('problem', flat=True).distinct()
    
    # Filter the problems based on the problem ids
    problems_solved = Problem.objects.filter(id__in=problem_ids)

    # Calculate statistics
    total_solved = problems_solved.count()
    easy_solved = problems_solved.filter(difficulty='easy').count()
    medium_solved = problems_solved.filter(difficulty='medium').count()
    hard_solved = problems_solved.filter(difficulty='hard').count()
    total_score=easy_solved*50+hard_solved*200+medium_solved*100
    context={
        'user':user,
        'problems_created':problems_created,
        'submissions':submissions,
        'total_solved':total_solved,
        'easy_solved':easy_solved,
        'medium_solved':medium_solved,
        'hard_solved':hard_solved,
        'total_score':total_score
    }
    return render(request,'base/profile.html',context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=='POST':
        username=request.POST.get('username').lower()
        password=request.POST.get('password')
        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request,'user not exist...')
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            messages.success(request, 'Successfully signed in as {}'.format(user.username))
            return redirect('home')
        else :
            messages.error(request,'username or password does not exist...')

    context={
        'page':'login',
    }
    return render(request,'base/login_register.html',context)

def registerPage(request):
    form =UserCreationForm()
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request,user)
            messages.success(request, 'Successfully signed in as {}'.format(user.username))
            return redirect('home')
        else:
            messages.error(request,'an error occured while registration...')
    context={
        'page':'register',
        'form':form,
    }
    return render(request,'base/login_register.html',context)

def logoutPage(request):
    logout(request)
    return redirect('home')

def submissionPage(request,pk):
    codesubmission=CodeSubmission.objects.get(id=int(pk))
    context={'submission':codesubmission}
    return render(request,'base/submission-page.html',context)

def allSubmissions(request,pk):
    problem=Problem.objects.get(id=int(pk))
    submissions=problem.codesubmission_set.all()
    context={
        'submissions':submissions
    }
    return render(request,'base/submissions.html',context)

def userSubmissions(request,pk):
    if not request.user.is_authenticated:
        messages.error(request,'login or signup !')
        return redirect('login')
    problem=Problem.objects.get(id=int(pk))
    submissions=problem.codesubmission_set.filter(user=request.user)
    context={
        'submissions':submissions
    }
    return render(request,'base/submissions.html',context)

def home(request):
    q=request.GET.get('q')
    d=request.GET.get('d')
    if q==None:
        q=''
    if d==None:
        d=''
    selected_topic=q
    selected_difficulty=d
    if q=='my':
        problems=request.user.problem_set.filter(Q(difficulty__icontains=d))
    else :
        problems=Problem.objects.filter(Q(difficulty__icontains=d)&(Q(title__icontains=q)|Q(topics__icontains=q)))
    context={'problems':problems,
             'topics':topics,
             'selected_topic':selected_topic,
             'selected_difficulty':selected_difficulty}
    return render(request,'base/problemlist.html',context)

def leaderboard(request):
    if not request.user.is_authenticated:
        messages.error(request,'Want to see yourself in Hall of Fame, fast! create an account.')
    allusers=User.objects.all()
    users=[]
    for user in allusers:
        submissions_passed=user.codesubmission_set.filter(status='passed')
    # easy_solved=problems_solved.filter(difficulty='easy').count()
        problem_ids = submissions_passed.values_list('problem', flat=True).distinct()
    
    # Filter the problems based on the problem ids
        problems_solved = Problem.objects.filter(id__in=problem_ids)

    # Calculate statistics
        total_solved = problems_solved.count()
        easy_solved = problems_solved.filter(difficulty='easy').count()
        medium_solved = problems_solved.filter(difficulty='medium').count()
        hard_solved = problems_solved.filter(difficulty='hard').count()
        total_score=easy_solved*50+hard_solved*200+medium_solved*100
        item={
            'id':user.id,
            'username':user.username,
            'total_solved':total_solved,
            'easy_solved':easy_solved,
            'medium_solved':medium_solved,
            'hard_solved':hard_solved,
            'total_score':total_score
        }
        users.append(item)
        users = sorted(users, key=lambda x: (x['total_score'], x['hard_solved'], x['medium_solved'], x['easy_solved']), reverse=True)
    context={
        'users':users
    }


    return render(request, 'base/leaderboard.html', context)

def createProblem(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
            messages.error(request,'You dont have admin level privileges')
            return redirect('home')
    form=ProblemForm()
    if request.method=='POST':
        form=ProblemForm(request.POST)
        if form.is_valid():
            problem=form.save(commit=False)
            problem.user=request.user
            problem.save()
            return redirect('home')
    context={
        'form':form,
        }
    return render(request,'base/add_problem.html',context)

def createTestCases(request,pk):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request,'You dont have admin level privileges')
        return redirect('home')
    problem=Problem.objects.get(id=int(pk))
    dummy_test_cases=problem.dummytestcases_set.all()
    form=TestCasesForm()
    if request.method=='POST':
        print(form)
        form=TestCasesForm(request.POST)
        if form.is_valid():
            test_case=form.save(commit=False)
            test_case.problem=problem
            test_case.save()
            return redirect('home')
        else:
            print("notvalid")
    context={
        'form':form,
        'problem':problem,
        'dummy_test_cases':dummy_test_cases
    }
    return render(request,'base/add_testcases.html',context)

def createDummyTestCases(request,pk):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request,'You dont have admin level privileges')
        return redirect('home')
    problem=Problem.objects.get(id=int(pk))
    form=DummyTestCasesForm()
    dummy_test_cases=problem.dummytestcases_set.all()
    if request.method=='POST':
        print(form)
        form=DummyTestCasesForm(request.POST)
        if form.is_valid():
            test_case=form.save(commit=False)
            test_case.problem=problem
            test_case.save()
            return redirect('home')
        else:
            print("notvalid")
    context={
        'form':form,
        'problem':problem,
        'dummy_test_cases':dummy_test_cases
    }
    return render(request,'base/add_dummytestcases.html',context)

def problemPage(request,pk):
    last=-1
    r=range(0)
    problem=Problem.objects.get(id=int(pk))
    dummy_test_cases=problem.dummytestcases_set.all()
    test_cases=problem.testcases_set.all()
    form=CodeSubmissionForm()
    if request.method=='POST':
        if not request.user.is_authenticated:
            return redirect('login')
        run_submit=request.POST.get('run_submit')
        form=CodeSubmissionForm(request.POST)
        if form.is_valid():
            submission=form.save(commit=False)
            if run_submit=='submit_code':
                passed=True
                for ind,test_case in enumerate(test_cases):
                    flag,output=run_code(submission.language,submission.code,test_case.input_data)
                    print(flag)
                    if flag=='compile-error':
                        submission.status=flag
                        submission.passed_testcases=0
                        submission.output_data=output
                        passed=False
                        break
                    elif flag=='runtime-error':
                        submission.status=flag
                        submission.passed_testcases=ind
                        passed=False
                        submission.output_data=output
                        break
                    output = output.rstrip()
                    output_list = [line.rstrip() for line in output.splitlines()]
                    req_output_list = [line.rstrip() for line in test_case.output_data.splitlines()]
                    if output_list!=req_output_list:
                        submission.status='failed'
                        submission.passed_testcases=ind
                        submission.output_data="FAILED"
                        passed=False
                        break
                if passed==True:
                    submission.status='passed'
                    submission.output_data="PASSED"
                    submission.passed_testcases=len(test_cases)
                else:
                    last=submission.passed_testcases
                form.output_data=submission.output_data
                submission.user=request.user
                submission.problem=problem
                r=range(submission.passed_testcases)
                submission.save()
            else:
                submission=form.save(commit=False)
                flag,output=run_code(submission.language,submission.code,submission.input_data)
                form.output_data=output
    context={
        'problem':problem,
        'dummy_test_cases':dummy_test_cases,
        'form':form,
        'range':r,
        'last':last
    }
    return render(request,'base/problem_page.html',context)

def submit(request,pk):
    problem=Problem.objects.get(id=int(pk))
    dummy_test_cases=problem.dummytestcases_set.all()
    form=CodeSubmissionForm()
    if request.method=='POST':
        run_submit=request.POST.get('run_submit')
        print(run_submit)
        print('hello')
        form=CodeSubmissionForm(request.POST)
        if form.is_valid():
            submission=form.save(commit=False)
            passed=True
            for ind,test_case in enumerate(dummy_test_cases):
                flag,output=run_code(submission.language,submission.code,test_case.input_data)
                print(flag)
                if flag=='compile-error':
                    submission.status=flag
                    submission.passed_testcases=0
                    submission.output_data=output
                    passed=False
                    break
                elif flag=='runtime-error':
                    submission.status=flag
                    submission.passed_testcases=ind
                    passed=False
                    submission.output_data=output
                    break
                output = output.rstrip()
                output_list = [line.rstrip() for line in output.splitlines()]
                req_output_list = [line.rstrip() for line in test_case.output_data.splitlines()]
                print(output_list)
                print(req_output_list)
                if output_list!=req_output_list:
                    submission.status='failed'
                    submission.passed_testcases=ind
                    submission.output_data="FAILED"
                    passed=False
                    break
            if passed==True:
                submission.status='passed'
                submission.output_data="PASSED"
                submission.passed_testcases=len(dummy_test_cases)
            form.output_data=submission.output_data
            submission.user=request.user
            submission.problem=problem
            submission.save()
    context={
        'problem':problem,
        'dummy_test_cases':dummy_test_cases,
        'form':form,
    }  
    return render(request,'base/problem_page.html',context)

def run_code(language,code,input_data):

    project_path=Path(settings.BASE_DIR)
    directories=["codes","inputs","outputs"]

    for directory in directories:
        directory_path=project_path / directory
        if not directory_path.exists():
            directory_path.mkdir(parents=True,exist_ok=True)    
    

    codes_dir=project_path / "codes"
    inputs_dir=project_path / "inputs"
    outputs_dir=project_path / "outputs"

    unique=str(uuid.uuid4())

    code_file_name=f"{unique}.{language}"
    input_file_name=f"{unique}.txt"
    output_file_name=f"{unique}.txt"

    code_file_path=codes_dir / code_file_name
    input_file_path=inputs_dir / input_file_name
    output_file_path=outputs_dir / output_file_name

    with open(code_file_path,'w') as code_file:
        code_file.write(code)

    with open(input_file_path,'w') as input_file:
        input_file.write(input_data)

    with open(output_file_path,'w') as output_file:
        pass

    if language=="cpp":
        excutable_path=codes_dir / unique
        compile_result=subprocess.run(
            ["g++" ,str(code_file_path) ,"-o" ,str(excutable_path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
        if compile_result.stderr:
            error_index = compile_result.stderr.lower().find('error')
            return ['compile-error',compile_result.stderr[error_index:]]
        else:
            if compile_result.returncode==0:
                with open(input_file_path,'r') as input_file:
                    with open(output_file_path,'w') as output_file:
                        subprocess.run(
                            [str(excutable_path)],
                            stdin=input_file,
                            stdout=output_file,
                            )
            else:
                error_index = compile_result.stderr.lower().find('error')
                return ['runtime-error',compile_result.returncode[error_index:]]
    elif language=="py":
        with open(input_file_path,'r') as input_file:
            with open(output_file_path,'w') as output_file:
                subprocess.run(
                    ['python3',str(code_file_path)],
                    stdin=input_file,
                    stdout=output_file,
                )
    elif language=="java    ":
        excutable_path=codes_dir / unique
        compile_result=subprocess.run(
            ["g++" ,str(code_file_path) ,"-o" ,str(excutable_path)]
            )
        if compile_result.returncode==0:
            with open(input_file_path,'r') as input_file:
                with open(output_file_path,'w') as output_file:
                    subprocess.run(
                        [str(excutable_path)],
                        stdin=input_file,
                        stdout=output_file,
                        )
    
    with open(output_file_path,'r') as output_file:
        output_data=output_file.read()
    return ['passed',output_data]