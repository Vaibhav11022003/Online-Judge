from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name='home'),
    path('problem-page/<str:pk>/',views.problemPage,name='problem-page'),
    path('create-problem',views.createProblem,name='create-problem'),
    path('create-testcases/<str:pk>/',views.createTestCases,name='create-testcases'),
    path('create-dummytestcases/<str:pk>/',views.createDummyTestCases,name='create-dummytestcases'),
    path('login/',views.loginPage,name='login'),
    path('logout/',views.logoutPage,name='logout'),
    path('register/',views.registerPage,name='register'),
    path('profile/<str:pk>/',views.userProfile,name='profile'),
    path('submission-page/<str:pk>/',views.submissionPage,name='submission-page'),
    path('all-submissions/<str:pk>/',views.allSubmissions,name='all-submissions'),
    path('user-submissions/<str:pk>/',views.userSubmissions,name='user-submissions'),
    path('leaderboard/',views.leaderboard,name='leaderboard'),
    # path('submit-problem/<str:pk>/',views.submitProblem,name='submit-problem'),
]