"""
Course Knowledge Base
Contains all information about the course that the agent can reference
"""

COURSE_INFO = {
    "course_name": "Introduction to Artificial Intelligence",
    "course_code": "CS 151",
    "semester": "Spring 2026",
    
    "professor": {
        "name": "Advait Shinde",
        "email": "advait.shinde@sjsu.edu",
        "office": "MacQuarrie Hall, Room 408",
        "office_hours": "Tuesdays and Thursdays, 2:00 PM - 4:00 PM, or by appointment"
    },
    
    "course_description": """
    This course provides a comprehensive introduction to the field of Artificial Intelligence (AI). 
    Students will learn fundamental concepts including search algorithms, knowledge representation, 
    machine learning, neural networks, natural language processing, and computer vision. 
    The course combines theoretical foundations with practical applications through hands-on projects.
    """,
    
    "schedule": {
        "lecture_times": "Monday and Wednesday, 10:30 AM - 11:45 AM",
        "location": "Engineering Building, Room 301",
        "lab_sessions": "Fridays, 1:00 PM - 2:50 PM in Computer Lab B"
    },
    
    "important_dates": {
        "midterm_exam": "March 12, 2025",
        "final_exam": "May 15, 2025, 9:45 AM - 12:00 PM",
        "project_proposal_due": "February 20, 2025",
        "final_project_due": "May 8, 2025",
        "last_day_to_drop": "March 1, 2025"
    },
    
    "grading": {
        "breakdown": {
            "Assignments (5 total)": "30%",
            "Midterm Exam": "20%",
            "Final Project": "25%",
            "Final Exam": "20%",
            "Class Participation": "5%"
        },
        "grading_scale": {
            "A": "93-100",
            "A-": "90-92",
            "B+": "87-89",
            "B": "83-86",
            "B-": "80-82",
            "C+": "77-79",
            "C": "73-76",
            "C-": "70-72",
            "D": "60-69",
            "F": "Below 60"
        }
    },
    
    "assignments": [
        {
            "name": "Assignment 1: Search Algorithms",
            "due_date": "February 5, 2025",
            "topics": "BFS, DFS, A* search"
        },
        {
            "name": "Assignment 2: Knowledge Representation",
            "due_date": "February 26, 2025",
            "topics": "Propositional logic, first-order logic"
        },
        {
            "name": "Assignment 3: Machine Learning Basics",
            "due_date": "March 19, 2025",
            "topics": "Linear regression, classification"
        },
        {
            "name": "Assignment 4: Neural Networks",
            "due_date": "April 9, 2025",
            "topics": "Perceptrons, backpropagation"
        },
        {
            "name": "Assignment 5: NLP Application",
            "due_date": "April 30, 2025",
            "topics": "Text processing, sentiment analysis"
        }
    ],
    
    "topics_covered": [
        "Introduction to AI and Intelligent Agents",
        "Problem Solving and Search Algorithms",
        "Knowledge Representation and Reasoning",
        "Uncertainty and Probabilistic Reasoning",
        "Machine Learning Fundamentals",
        "Neural Networks and Deep Learning",
        "Natural Language Processing",
        "Computer Vision Basics",
        "Ethics in AI"
    ],
    
    "prerequisites": "CS 46B (Introduction to Data Structures) or equivalent",
    
    "textbook": {
        "title": "Artificial Intelligence: A Modern Approach",
        "authors": "Stuart Russell and Peter Norvig",
        "edition": "4th Edition",
        "required": True
    },
    
    "policies": {
        "late_submission": "Late assignments accepted up to 48 hours after deadline with 20% penalty. No submissions accepted after 48 hours.",
        "attendance": "Attendance is not mandatory but strongly encouraged. Class participation contributes to 5% of final grade.",
        "academic_integrity": "All work must be your own. Collaboration is allowed on assignments but you must write your own code. Plagiarism will result in failure of the course.",
        "makeup_exams": "Makeup exams only granted for documented emergencies. Must notify professor within 24 hours."
    },
    
    "resources": {
        "canvas": "All materials, assignments, and grades posted on Canvas",
        "piazza": "Use Piazza for course-related questions and discussions",
        "tutoring": "Free tutoring available at the CS Learning Center, Monday-Friday 10 AM - 5 PM"
    }
}


def get_course_context():
    """
    Returns formatted course information as context for the AI agent
    """
    context = f"""
        COURSE INFORMATION:

        Course: {COURSE_INFO['course_code']} - {COURSE_INFO['course_name']}
        Semester: {COURSE_INFO['semester']}

        PROFESSOR:
        Name: {COURSE_INFO['professor']['name']}
        Email: {COURSE_INFO['professor']['email']}
        Office: {COURSE_INFO['professor']['office']}
        Office Hours: {COURSE_INFO['professor']['office_hours']}

        DESCRIPTION:
        {COURSE_INFO['course_description']}

        SCHEDULE:
        Lectures: {COURSE_INFO['schedule']['lecture_times']}
        Location: {COURSE_INFO['schedule']['location']}
        Lab: {COURSE_INFO['schedule']['lab_sessions']}

        IMPORTANT DATES:
        - Midterm Exam: {COURSE_INFO['important_dates']['midterm_exam']}
        - Final Exam: {COURSE_INFO['important_dates']['final_exam']}
        - Project Proposal Due: {COURSE_INFO['important_dates']['project_proposal_due']}
        - Final Project Due: {COURSE_INFO['important_dates']['final_project_due']}
        - Last Day to Drop: {COURSE_INFO['important_dates']['last_day_to_drop']}

        GRADING:
        """
    for item, percentage in COURSE_INFO['grading']['breakdown'].items():
        context += f"- {item}: {percentage}\n"
    
    context += "\nGRADING SCALE:\n"
    for grade, range_val in COURSE_INFO['grading']['grading_scale'].items():
        context += f"- {grade}: {range_val}\n"
    
    context += "\nASSIGNMENTS:\n"
    for assignment in COURSE_INFO['assignments']:
        context += f"- {assignment['name']} (Due: {assignment['due_date']}): {assignment['topics']}\n"
    
    context += f"\nPREREQUISITES: {COURSE_INFO['prerequisites']}\n"
    
    context += "\nTEXTBOOK:\n"
    context += f"- {COURSE_INFO['textbook']['title']} by {COURSE_INFO['textbook']['authors']}, {COURSE_INFO['textbook']['edition']}\n"
    
    context += "\nPOLICIES:\n"
    for policy, description in COURSE_INFO['policies'].items():
        context += f"- {policy.replace('_', ' ').title()}: {description}\n"
    
    return context