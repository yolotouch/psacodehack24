from django.shortcuts import render, redirect
from .forms import MentorSearchForm, SendQuestionForm
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from .models import Question

# Load the CSV file once at the start of the app (global scope)
csv_file_path = '/Users/kohziyang/Documents/wtf/psacodehack24/my_project_matching/employees.csv'  # Path to the CSV file
employee_df = pd.read_csv(csv_file_path)

from django.shortcuts import render, redirect

# View for entering the mentee's name
def enter_name(request):
    if request.method == 'POST':
        # Get the mentee name from the form
        mentee_name = request.POST.get('mentee_name')

        # Store the mentee name in the session
        request.session['mentee_name'] = mentee_name

        # Redirect to the home page after the name is stored
        return redirect('home')
    
    # Render the form if the method is GET
    return render(request, 'mentorship/enter_name.html')



# Home page view (after entering name)
def home(request):
    # Check if the user's name is stored in the session
    mentee_name = request.session.get('mentee_name', None)

    # If the user's name is not stored in the session, redirect to the enter_name page
    if not mentee_name:
        return redirect('enter_name')

    # If the user's name is found in the session, render the home page
    return render(request, 'mentorship/home.html', {'mentee_name': mentee_name})


def mentor_search(request):
    # Retrieve mentee's name from the session
    mentee_name = request.session.get('mentee_name', None)
    
    # If no name is stored in the session, redirect to the enter_name page
    if not mentee_name:
        return redirect('enter_name')
    
    # Load the employee dataset
    employee_df = pd.read_csv(csv_file_path)

    # Check if the mentee already has a mentor
    mentee_data = employee_df[employee_df['Name'] == mentee_name]
    if mentee_data.empty:
        return render(request, 'mentorship/search.html', {
            'error_message': f"No employee found with the name {mentee_name}. Please try again."
        })
    
    # If the mentee already has a mentor, redirect or show a message
    if not pd.isna(mentee_data.iloc[0]['Mentor']):
        mentor_name = mentee_data.iloc[0]['Mentor']
        return render(request, 'mentorship/already_have_mentor.html', {
            'mentee_name': mentee_name,
            'mentor_name': mentor_name,
        })
    # If mentee does not have a mentor, proceed with the mentor search
    mentee_data = mentee_data.iloc[0]
    mentee_skillset = mentee_data['Skillset']
    mentee_years_of_experience = mentee_data['Years_of_Experience']
    mentee_project_success_rate = mentee_data['Project_Success_Rate']

    mentor_candidates = employee_df[employee_df['Name'] != mentee_name]
    mentor_skillsets = mentor_candidates['Skillset'].tolist()
    mentor_skillsets.append(mentee_skillset)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(mentor_skillsets)

    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    mentor_candidates['Skill Match'] = cosine_sim[0]
    mentor_candidates['Experience Match'] = (
        mentor_candidates['Years_of_Experience'] / mentee_years_of_experience).apply(lambda x: min(x, 1))
    mentor_candidates['Success Rate Match'] = (
        mentor_candidates['Project_Success_Rate'] / mentee_project_success_rate).apply(lambda x: min(x, 1))

    mentor_candidates['Final_Score'] = round((
        0.6 * mentor_candidates['Skill Match'] +
        0.2 * mentor_candidates['Years_of_Experience'] / 20 +
        0.2 * mentor_candidates['Project_Success_Rate'])
    ,2) * 100

    top_mentors = mentor_candidates.sort_values(by='Final_Score', ascending=False).head(5)

    return render(request, 'mentorship/match_results.html', {
        'mentee_name': mentee_name,
        'mentors': top_mentors
    })


def mentor_select(request, mentor_name):
    # Load the employee dataset
    employee_df = pd.read_csv(csv_file_path)
    
    # Find the mentor in the dataset
    mentor_index = employee_df[employee_df['Name'] == mentor_name].index
    if not mentor_index.empty:
        # Retrieve mentee's name from the session
        mentee_name = request.session.get('mentee_name', None)

        # Check if mentee name is in session and valid
        if not mentee_name:
            return redirect('enter_name')

        # Find mentee index in the dataset
        mentee_index = employee_df[employee_df['Name'] == mentee_name].index
        if not mentee_index.empty:
            # Mark the mentor for the mentee
            employee_df.loc[mentee_index, 'Mentor'] = mentor_name

            # Save the updated CSV
            employee_df.to_csv(csv_file_path, index=False)

            # Render success page
            return render(request, 'mentorship/success.html', {
                'mentor_name': mentor_name,
                'message': f"Congratulations! You have successfully chosen {mentor_name} as your mentor."
            })
    else:
        return render(request, 'mentorship/match_results.html', {
            'error_message': "Mentor not found.",
        })


def manage_mentorship(request):
    import pandas as pd


def manage_mentorship(request):
    # Get the mentee's name from the session
    mentee_name = request.session.get('mentee_name', None)

    # If the mentee's name is not in the session, redirect to enter name
    if not mentee_name:
        return redirect('enter_name')

    # Load the employee dataset
    employee_df = pd.read_csv(csv_file_path)

    # Find the mentee's data
    mentee_data = employee_df[employee_df['Name'] == mentee_name]
    
    if mentee_data.empty:
        return render(request, 'mentorship/manage_mentorship.html', {
            'error_message': f"No employee found with the name {mentee_name}. Please try again."
        })

    # Get the mentor's name from the mentee's data
    mentor_name = mentee_data.iloc[0]['Mentor']

    if not pd.isna(mentor_name):
        # Get the mentor's data
        mentor_data = employee_df[employee_df['Name'] == mentor_name]
        
        if not mentor_data.empty:
            mentor_info = mentor_data.iloc[0]
            # Pass mentor details to the template
            return render(request, 'mentorship/manage.html', {
                'mentee_name': mentee_name,
                'mentor_name': mentor_info['Name'],
                'mentor_role': mentor_info['Role'],
                'mentor_department': mentor_info['Department'],
                'mentor_years_of_experience': mentor_info['Years_of_Experience'],
                #'mentor_intro': mentor_info.get('Introduction', 'No introduction available')  # Customize this field
            })

    return render(request, 'mentorship/manage_mentorship.html', {
        'mentee_name': mentee_name,
        'mentor_name': None
    })

def home(request):
    # This is the homepage where the user can choose to manage or find a mentor
    return render(request, 'mentorship/home.html')

def already_have_mentor(request):
    # Retrieve the mentee's name from the session
    mentee_name = request.session.get('mentee_name', None)

    # If no mentee name in session, redirect to enter name page
    if not mentee_name:
        return redirect('enter_name')

    # Load the employee dataset
    employee_df = pd.read_csv(csv_file_path)

    # Find the mentee's data
    mentee_data = employee_df[employee_df['Name'] == mentee_name]
    
    # If mentee does not exist, redirect to the enter name page
    if mentee_data.empty:
        return redirect('enter_name')

    # Get the mentor's name from the data
    mentor_name = mentee_data.iloc[0]['Mentor']

    # Render the already_have_mentor page if a mentor exists
    if pd.notna(mentor_name):
        return render(request, 'mentorship/already_have_mentor.html', {
            'mentee_name': mentee_name,
            'mentor_name': mentor_name
        })
    
    # If for some reason the mentee doesn't have a mentor, redirect to find a mentor
    return redirect('find_mentor')

def send_question(request):
    mentee_name = request.session.get('mentee_name')
    
    # Load the employee dataset to find the mentor of this mentee
    employee_df = pd.read_csv(csv_file_path)
    mentee_data = employee_df[employee_df['Name'] == mentee_name]
    
    if mentee_data.empty:
        return redirect('enter_name')  # If no mentee found, redirect to enter name page
    
    mentor_name = mentee_data.iloc[0]['Mentor']
    
    if request.method == 'POST':
        form = SendQuestionForm(request.POST)
        if form.is_valid():
            # Save the question in the database
            question = Question.objects.create(
                mentor_name=mentor_name,
                mentee_name=mentee_name,
                question_text=form.cleaned_data['question']
            )
            

            return redirect('question_sent_success')  # Redirect to a success page after submission
    else:
        form = SendQuestionForm()

    return render(request, 'mentorship/send_question.html', {
        'form': form,
        'mentor_name': mentor_name,
    })

def view_questions(request):
    mentee_name = request.session.get('mentee_name')
    questions = Question.objects.filter(mentee_name=mentee_name)
    
    return render(request, 'mentorship/view_questions.html', {'questions': questions})

def question_sent_success(request):
    return render(request, 'mentorship/question_sent_success.html')