from faker import Faker
import pandas as pd
import random

fake = Faker()

# Define realistic departments, roles, and separate skillsets for each department
departments_roles = {
    'Operations': {
        'Operations Manager': (7, 15),
        'Logistics Coordinator': (1, 5),
    },
    'Engineering': {
        'Junior Engineer': (0, 3),
        'Engineer': (3, 6),
        'Senior Engineer': (6, 10),
    },
    'Logistics': {
        'Logistics Coordinator': (1, 5),
    },
    'IT': {
        'IT Support': (0, 3),
    },
    'Customer Service': {
        'Customer Service Executive': (0, 4),
    }
}

# Define skillsets for each department
department_skillsets = {
    
    'Operations': [
        'Project Management', 
        'Teamwork', 
        'Data Analysis', 
        'Time Management', 
        'Process Improvement', 
        'Risk Management'
    ],
    'Engineering': [
        'Python', 
        'Java', 
        'Machine Learning', 
        'Data Analysis', 
        'CAD Design', 
        'Systems Engineering', 
        'Electrical Engineering'
    ],
    'Logistics': [
        'Communication', 
        'Data Analysis', 
        'Networking', 
        'Supply Chain Management', 
        'Inventory Management', 
        'Warehouse Management'
    ],
    'IT': [
        'Networking', 
        'Communication', 
        'Python', 
        'Java', 
        'Cybersecurity', 
        'Cloud Computing', 
        'System Administration'
    ],
    'Customer Service': [
        'Communication', 
        'Teamwork', 
        'Customer Relationship Management', 
        'Problem Solving', 
        'Conflict Resolution', 
    ]
}

# Function to generate a random skillset based on department skillsets
def generate_skillsets(allowed_skills, num_skills=3):
    return random.sample(allowed_skills, min(num_skills, len(allowed_skills)))

# Ensure we generate exactly 100 rows
data = []
while len(data) < 3000:  # Loop until we have exactly 100 valid rows
    name = fake.name()
    age = random.randint(25, 55)  # Age between 25 and 55
    department = random.choice(list(departments_roles.keys()))
    
    # Set a higher probability of years of experience based on age
    if age < 30:
        years_of_experience = random.randint(0, 2)
    elif age < 40:
        years_of_experience = random.randint(3, 7)
    elif age < 50:
        years_of_experience = random.randint(6, 12)
    else:
        years_of_experience = random.randint(10, 20)
    
    # Determine role based on years of experience and department
    role = next((r for r, (min_exp, max_exp) in departments_roles[department].items() if min_exp <= years_of_experience < max_exp), None)
    
    # Only append data if a valid role is found
    if role:
        if years_of_experience < 3:
            num_skills = fake.random_int(min=1, max = 2)
        elif years_of_experience < 7:
            num_skills = fake.random_int(min=2, max = 3)
        elif years_of_experience < 10:
            num_skills = fake.random_int(min=3, max = 4)
        else :
            num_skills = fake.random_int(min=4, max = 6)
        #num_skills = fake.random_int(min=1, max=len(department_skillsets[department]))  # Randomly decide how many skills the person has
        selected_skills = random.sample(department_skillsets[department], num_skills)
        skillset = ', '.join(selected_skills)  # Choose skillsets based on department
        project_success_rate = round(random.uniform(0.5, 1.0), 2)  # Random success rate between 0.5 and 1.0
        if years_of_experience < 5:
            mentee = "NA"
            mentor = ""
        else:
            mentee = ""
            mentor = "NA"
        data.append([name, age, department, role, years_of_experience, skillset, project_success_rate, mentor , mentee])

# Create a DataFrame
df = pd.DataFrame(data, columns=['Name', 'Age', 'Department', 'Role', 'Years_of_Experience', 'Skillset', 'Project_Success_Rate',"Mentor","Mentee"])

# Save to CSV
df.to_csv('employees.csv', index=False)


print(df)