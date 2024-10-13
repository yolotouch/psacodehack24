import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.shortcuts import render, redirect
from .forms import EmployeeForm, TrendAnalysisForm
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import openai
import logging
from bs4 import BeautifulSoup

# Set up logger
logger = logging.getLogger(__name__)

# Course data (including scraped courses)
courses = {
    'Course Name': [
        'Python for Data Science', 
        'Leadership Development', 
        'Advanced Machine Learning', 
        'Process Optimization', 
        'Data Visualization with Python', 
        'Project Management Fundamentals', 
        'Cloud Computing Essentials', 
        'Blockchain Technology', 
        'Cybersecurity Basics', 
        'Big Data Analytics'
    ],
    'Skills Covered': [
        'Python, Data Science', 
        'Leadership', 
        'Machine Learning, Python', 
        'Process Improvement', 
        'Data Visualization, Matplotlib, Seaborn', 
        'Project Management, Planning, Execution', 
        'Cloud Infrastructure, AWS, Azure', 
        'Blockchain, Distributed Systems', 
        'Cybersecurity, Network Security', 
        'Big Data, Hadoop, Spark'
    ]
}
course_df = pd.DataFrame(courses)

# Base page for user selection (HR or Employee)
def base_page(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        if user_type == 'hr':
            return redirect('trend_analysis')
        elif user_type == 'employee':
            return redirect('employee_recommendation')
    return render(request, 'courserecco/base_page.html')

# Helper function to vectorize course skills
def vectorize_courses(vectorizer, course_df):
    course_df['Skills Covered'] = course_df['Skills Covered'].apply(lambda x: x.replace(', ', ' '))
    return vectorizer.transform(course_df['Skills Covered'])

# Calculate skill similarity
def calculate_skill_similarity(employee_skills, required_skills, vectorizer):
    employee_skills_str = ' '.join(employee_skills)
    required_skills_str = ' '.join(required_skills)
    skill_vectors = vectorizer.transform([employee_skills_str, required_skills_str])
    return cosine_similarity(skill_vectors[0], skill_vectors[1])[0][0]

# Find suitable role for employee
def find_suitable_role_for_employee(employee_skills, job_skill_storage, vectorizer):
    suitability_scores = []
    for role, required_skills in job_skill_storage.items():
        similarity_score = calculate_skill_similarity(employee_skills, required_skills, vectorizer)
        suitability_scores.append((role, similarity_score, required_skills))
    
    if not suitability_scores:
        return None  # No suitable role found
    
    return sorted(suitability_scores, key=lambda x: x[1], reverse=True)[0]

# Scraping function
def scrape_course_for_skill(skill):
    url = f"https://www.classcentral.com/search?q={skill.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Scrape course name and URL from the site (this depends on the site's structure)
            course = soup.find('a', class_='course-name')  # Adjust this based on the site structure
            if course:
                title = course.get_text(strip=True)
                course_url = f"https://www.classcentral.com{course['href']}"
                return title, course_url
        return None, None
    except Exception as e:
        logger.error(f"Error scraping course for skill {skill}: {e}")
        return None, None

# Recommend courses based on missing skills
# Recommend courses based on missing skills
def recommend_courses_for_employee(employee_skills, suitable_role, required_skills, course_df, vectorizer):
    missing_skills = set(required_skills) - set(employee_skills)
    recommended_courses = []
    
    if missing_skills:
        for skill in missing_skills:
            # Scrape courses for each missing skill
            course_name, course_url = scrape_course_for_skill(skill)
            if course_name and course_url:
                recommended_courses.append({
                    'Skill': skill,
                    'Course_Title': course_name,  # No space in the key name
                    'Course_URL': course_url      # No space in the key name
                })

        return {
            'Suitable_Role': suitable_role,
            'Missing_Skills': list(missing_skills),
            'Recommended_Courses': recommended_courses
        }
    
    return {'Suitable_Role': suitable_role, 'Missing_Skills': [], 'Recommended_Courses': []}

def employee_recommendation(request):
    job_skill_storage = request.session.get('job_skill_storage', {})

    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            current_role = form.cleaned_data['current_role']
            career_goal = form.cleaned_data['career_goal']
            current_skillset = form.cleaned_data['current_skillset'].split(', ')

            logger.info(f"Employee Skillset: {current_skillset}")
            logger.info(f"Job Skill Storage: {job_skill_storage}")

            if not job_skill_storage:
                return render(request, 'courserecco/no_skill_data.html', {
                    'message': 'No job data available. Please run trend analysis first.'
                })

            all_skills = current_skillset + [skill for skills in job_skill_storage.values() for skill in skills]
            vectorizer = TfidfVectorizer().fit(all_skills)

            try:
                suitable_role_data = find_suitable_role_for_employee(current_skillset, job_skill_storage, vectorizer)
            except Exception as e:
                logger.error(f"Error during role matching: {e}")
                return render(request, 'courserecco/recommendation_result.html', {
                    'form': form,
                    'current_role': current_role,
                    'career_goal': career_goal,
                    'recommendation': {
                        'Suitable Role': 'Error in calculation.',
                        'Missing Skills': [],
                        'Recommended Courses': []
                    }
                })

            if not suitable_role_data:
                return render(request, 'courserecco/recommendation_result.html', {
                    'form': form,
                    'current_role': current_role,
                    'career_goal': career_goal,
                    'recommendation': {
                        'Suitable Role': 'No suitable role found for your skillset.',
                        'Missing Skills': [],
                        'Recommended Courses': []
                    }
                })

            suitable_role, similarity_score, required_skills = suitable_role_data
            logger.info(f"Suitable Role: {suitable_role}, Similarity Score: {similarity_score}, Required Skills: {required_skills}")

            recommendation = recommend_courses_for_employee(current_skillset, suitable_role, required_skills, course_df, vectorizer)

            logger.info(f"Recommendation: {recommendation}")

            recommendation['Compatibility_Percentage'] = round(similarity_score * 100, 2)

            return render(request, 'courserecco/recommendation_result.html', {
                'form': form,
                'recommendation': recommendation,
                'current_role': current_role,
                'career_goal': career_goal
            })

    else:
        form = EmployeeForm()

    return render(request, 'courserecco/employee_form.html', {'form': form})


# Function to scrape the content of a URL
def scrape_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            article_content = soup.find_all(['p', 'div', 'article'])[:20]
            article_text = ' '.join(paragraph.get_text() for paragraph in article_content if paragraph.get_text())
            return re.sub(r'\s+', ' ', article_text).strip()
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return ""

# Use ThreadPoolExecutor to gather content from multiple URLs concurrently
def fetch_all_urls(urls):
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(scrape_url, url): url for url in urls}
        results = []
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error fetching data from {url}: {e}")
        return results
    
# Parse job roles and skills from GPT response
def parse_job_roles_and_skills(response_text):
    job_skills_dict = {}
    lines = response_text.strip().split("\n")

    current_job_role = None
    for line in lines:
        line = re.sub(r'^\d+\.\s*', '', line).strip()  # Remove list numbers (e.g., 1. 2. etc.)
        line = re.sub(r'^-\s*', '', line).strip()  # Remove dashes before skills

        if line.startswith("Job Role:"):
            current_job_role = line.split("Job Role:", 1)[1].strip()
            job_skills_dict[current_job_role] = []
        elif current_job_role and line.startswith("Skills:"):
            skills = line.split("Skills:", 1)[1].strip().split(", ")
            job_skills_dict[current_job_role].extend(skills)

    return job_skills_dict

# Function to split large text into chunks of a specified size
def split_text(text, chunk_size=5000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Function to count tokens in a given text
def count_tokens(text):
    return len(text.split())

# Function to count the total tokens in the job_skill_storage dictionary
def count_tokens_in_dict(job_skill_storage):
    total_tokens = 0
    for job, skills in job_skill_storage.items():
        total_tokens += count_tokens(job) + sum(count_tokens(skill) for skill in skills)
    return total_tokens

def analyze_content(text, job_skill_storage, max_token_limit):
    chunks = split_text(text)

    for chunk in chunks:
        total_tokens = count_tokens_in_dict(job_skill_storage)
        if total_tokens >= max_token_limit:
            break

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant extracting job roles and skills."},
                {"role": "user", "content": f"Extract job roles and their skills in this format: \nJob Role: <Job Role>\nSkills: <Skill 1>, <Skill 2>, ...\nText:\n{chunk}"}
            ],
            max_tokens=500,
            temperature=0.7
        )

        response_text = response['choices'][0]['message']['content'].strip()
        job_roles_and_skills = parse_job_roles_and_skills(response_text)
        job_skill_storage.update(job_roles_and_skills)

def trend_analysis(request):
    if request.method == 'POST':
        form = TrendAnalysisForm(request.POST)
        if form.is_valid():
            urls = form.cleaned_data['urls'].splitlines()

            # Fetch all URLs concurrently
            contents = fetch_all_urls(urls)

            # Initialize job_skill_storage
            job_skill_storage = {}
            max_token_limit = 1000

            # Analyze each content concurrently
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(analyze_content, content, job_skill_storage, max_token_limit): content for content in contents}

                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Error processing content: {e}")

            # Save job_skill_storage in session
            request.session['job_skill_storage'] = job_skill_storage

            return render(request, 'courserecco/trend_analysis_result.html', {
                'job_skill_storage': dict(list(job_skill_storage.items())[:5])
            })
    else:
        form = TrendAnalysisForm()

    return render(request, 'courserecco/trend_analysis.html', {'form': form})