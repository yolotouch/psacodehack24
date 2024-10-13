from django.shortcuts import render
import pandas as pd
import random
from faker import Faker
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import accuracy_score
from django.http import HttpResponse
import csv

fake = Faker()

# Global variables to hold the dataframes
employee_df = None
tasks_df = None
task_assignment_df = None

# View to generate employee data
def generate_employee_data(request):
    global employee_df
    # Generate employee data
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

    department_skillsets = {
        'Operations': [
            'Project Management', 'Teamwork', 'Data Analysis', 'Time Management', 'Process Improvement', 'Risk Management'
        ],
        'Engineering': [
            'Python', 'Java', 'Machine Learning', 'Data Analysis', 'CAD Design', 'Systems Engineering', 'Electrical Engineering'
        ],
        'Logistics': [
            'Communication', 'Data Analysis', 'Networking', 'Supply Chain Management', 'Inventory Management', 'Warehouse Management'
        ],
        'IT': [
            'Networking', 'Communication', 'Python', 'Java', 'Cybersecurity', 'Cloud Computing', 'System Administration'
        ],
        'Customer Service': [
            'Communication', 'Teamwork', 'Customer Relationship Management', 'Problem Solving', 'Conflict Resolution'
        ]
    }

    data = []
    while len(data) < 100:
        name = fake.name()
        age = random.randint(25, 55)
        department = random.choice(list(departments_roles.keys()))
        years_of_experience = random.randint(1, 20)
        role = next((r for r, (min_exp, max_exp) in departments_roles[department].items() if min_exp <= years_of_experience < max_exp), None)
        
        if role:
            num_skills = random.randint(1, 4)
            selected_skills = random.sample(department_skillsets[department], num_skills)
            skillset = ', '.join(selected_skills)
            project_success_rate = round(random.uniform(0.5, 1.0), 2)
            working_hours_available = random.randint(20, 40)
            data.append([name, age, department, role, years_of_experience, skillset, project_success_rate, working_hours_available])

    employee_df = pd.DataFrame(data, columns=['Name', 'Age', 'Department', 'Role', 'Years_of_Experience', 'Skillset', 'Project_Success_Rate', 'Working_Hours_Available'])
    return HttpResponse("Employee data generated successfully.")

# View to generate task data
def generate_task_data(request):
    global tasks_df
    task_roles = {
        'Operations': {
            'required_skills': ['Data Analysis', 'Time Management', 'Project Management', 'Risk Management'],
            'hours_required': [4, 6, 8],
            'urgency': [1, 2, 3, 4, 5]
        },
        'Engineering': {
            'required_skills': ['CAD Design', 'Systems Engineering', 'Python', 'Machine Learning'],
            'hours_required': [4, 5, 8],
            'urgency': [2, 3, 4, 5]
        },
        'Logistics': {
            'required_skills': ['Supply Chain Management', 'Data Analysis', 'Inventory Management'],
            'hours_required': [3, 5, 6],
            'urgency': [3, 4, 5]
        },
        'IT': {
            'required_skills': ['Networking', 'Cybersecurity', 'System Administration'],
            'hours_required': [4, 6, 8],
            'urgency': [1, 3, 5]
        },
        'Customer Service': {
            'required_skills': ['Communication', 'Problem Solving', 'Conflict Resolution'],
            'hours_required': [2, 4, 5],
            'urgency': [3, 4, 5]
        }
    }

    tasks_data = []
    num_tasks = 50
    for _ in range(num_tasks):
        department = random.choice(list(task_roles.keys()))
        task_name = fake.bs().title()
        required_skills = ', '.join(random.sample(task_roles[department]['required_skills'], 2))
        hours_required = random.randint(5, 15)  # Adjusted range for hours required
        urgency = random.choice(task_roles[department]['urgency'])
        tasks_data.append([department, task_name, required_skills, hours_required, urgency])

    tasks_df = pd.DataFrame(tasks_data, columns=['Department', 'Task', 'Required_Skillset', 'Hours_Required', 'Urgency'])
    return HttpResponse("Task data generated successfully.")

# View to assign tasks based on the Random Forest model
def assign_tasks(request):
    global employee_df, tasks_df, task_assignment_df

    if employee_df is None or tasks_df is None:
        return HttpResponse('Generate employee and task data first.', status=400)

    # Encode skills as binary values for modeling
    mlb = MultiLabelBinarizer()
    skills_encoded = mlb.fit_transform(employee_df['Skillset'])
    df_skills = pd.DataFrame(skills_encoded, columns=mlb.classes_)
    employee_df = pd.concat([employee_df, df_skills], axis=1)

    # Generate pairwise combinations of employees and tasks for training the model
    employee_task_combinations = []
    for _, employee in employee_df.iterrows():
        for _, task in tasks_df.iterrows():
            match = bool(set(task['Required_Skillset']) & set(employee['Skillset']))
            if match and employee['Working_Hours_Available'] >= task['Hours_Required']:
                employee_task_combinations.append([employee['Name'], task['Task'], 1])  # Suitable assignment
            else:
                employee_task_combinations.append([employee['Name'], task['Task'], 0])  # Not suitable

    comb_df = pd.DataFrame(employee_task_combinations, columns=['Employee', 'Task', 'Assigned'])

    # Prepare features and labels for the model
    X = comb_df.drop('Assigned', axis=1)
    y = comb_df['Assigned']
    X = pd.get_dummies(X, columns=['Employee', 'Task'])

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train RandomForestClassifier
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Create task-employee pairs for prediction
    employee_task_pairs = create_employee_task_pairs(employee_df, tasks_df)
    pred_df = pd.DataFrame(employee_task_pairs, columns=['Employee', 'Task', 'Required_Skillset', 'Hours_Required', 'Urgency'])
    pred_X = pd.get_dummies(pred_df[['Employee', 'Task']])
    pred_X = pred_X.reindex(columns=X_train.columns, fill_value=0)

    # Predict suitability
    pred_df['Suitability'] = model.predict(pred_X)

    # Assign tasks to employees
    task_assignments = assign_tasks_to_employees(pred_df, employee_df, tasks_df)

    # Convert task assignments to DataFrame and return as CSV
    task_assignment_data = []
    for task, employees in task_assignments.items():
        for employee, hours_worked in employees:
            task_assignment_data.append([task, employee, hours_worked])

    task_assignment_df = pd.DataFrame(task_assignment_data, columns=['Task', 'Assigned_Employee', 'Hours_Worked'])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="task_assignments.csv"'
    task_assignment_df.to_csv(path_or_buf=response, index=False)

    return response

def create_employee_task_pairs(employee_df, tasks_df):
    pairs = []
    for _, employee in employee_df.iterrows():
        for _, task in tasks_df.iterrows():
            pairs.append([employee['Name'], task['Task'], task['Required_Skillset'], task['Hours_Required'], task['Urgency']])
    return pairs

def assign_tasks_to_employees(pred_df, employee_df, tasks_df):
    task_assignments = {task: [] for task in tasks_df['Task']}

    for _, task in tasks_df.iterrows():
        suitable_employees = pred_df[(pred_df['Task'] == task['Task']) & (pred_df['Suitability'] == 1)]
        suitable_employees = suitable_employees.merge(employee_df[['Name', 'Working_Hours_Available']], left_on='Employee', right_on='Name')
        suitable_employees = suitable_employees[suitable_employees['Working_Hours_Available'] >= task['Hours_Required']]
        suitable_employees = suitable_employees.sort_values(by='Working_Hours_Available', ascending=False)

        assigned_employees = []
        for _, employee in suitable_employees.iterrows():
            if len(assigned_employees) < 3:
                assigned_employees.append(employee['Employee'])
                # Reduce the employee's available hours proportionally later
            else:
                break

        # Divide task hours equally among assigned employees
        if assigned_employees:
            hours_per_employee = task['Hours_Required'] / len(assigned_employees)
            for employee in assigned_employees:
                # Assign the calculated hours per employee
                task_assignments[task['Task']].append((employee, hours_per_employee))
                # Reduce the working hours available for that employee
                employee_df.loc[employee_df['Name'] == employee, 'Working_Hours_Available'] -= hours_per_employee

    return task_assignments

# Index page view
def index(request):
    return render(request, 'index.html')
