from django.urls import path
from . import views

urlpatterns = [
    # Home page after entering name
    path('', views.home, name='home'),  # Root URL directs to home view
    
    # Page to enter mentee's name
    path('enter_name/', views.enter_name, name='enter_name'),  
    
    # Find mentor page (only accessible if mentee has no mentor)
    path('find_mentor/', views.mentor_search, name='find_mentor'),  
    
    # Manage mentorship page
    path('manage_mentorship/', views.manage_mentorship, name='manage_mentorship'),  
    
    # Mentor selection (if mentee selects a mentor)
    path('mentor_select/<str:mentor_name>/', views.mentor_select, name='mentor_select'),
    
    # Page indicating mentor is already selected
    path('already_have_mentor/', views.already_have_mentor, name='already_have_mentor'),

    path('send_question/', views.send_question, name='send_question'),
    path('view_questions/', views.view_questions, name='view_questions'),
    path('question_sent_success/', views.question_sent_success, name='question_sent_success'),
]



