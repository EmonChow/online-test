import json
import random
from django.shortcuts import get_object_or_404, render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from teacher import models as TMODEL
from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist


#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/studentsignup.html',context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)

def start_exam_view(request, pk):
    course = get_object_or_404(QMODEL.Course, id=pk)
    all_questions = QMODEL.Question.objects.filter(course=course)
    total_questions = all_questions.count() 
    # Check if there are at least 7 questions available for this course
    if all_questions.count() < 7:
        return HttpResponse("Not enough questions available for this course.")

    # Select 7 random questions from the database
    random_questions = random.sample(list(all_questions), 7)

    if request.method == 'POST':
        pass

    # Create a list of question data including options
    question_data = [{'number': i + 1, 'question_text': question.question,
                     'options': [question.option1, question.option2,
                                 question.option3, question.option4]}
                    for i, question in enumerate(random_questions)]

    # Group consecutive two-digit numbers
    grouped_numbers = []
    current_group = []
    for digit in range(1, 7):  # Display only 7 questions
        current_group.append(str(digit))
        if len(current_group) == 6 or digit == 7:  # Group by 6 for 7 questions
            grouped_numbers.append(current_group)
            current_group = []

    context = {
        'course': course,
        'question_data': question_data,
        'grouped_numbers': grouped_numbers,
        'questions_json': json.dumps(question_data), 
        'total_questions': total_questions,
        # Convert question data to JSON
    }

    return render(request, 'student/start_exam.html', context)




@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course=QMODEL.Course.objects.get(id=course_id)
        
        total_marks=0
        questions=QMODEL.Question.objects.all().filter(course=course)
        for i in range(len(questions)):
            
            selected_ans = request.COOKIES.get(str(i+1))
            actual_answer = questions[i].answer
            if selected_ans == actual_answer:
                total_marks = total_marks + questions[i].marks
        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.marks=total_marks
        result.exam=course
        result.student=student
        result.save()

        return HttpResponseRedirect('view-result')




@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/view_result.html',{'courses':courses})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request, id):
    # Retrieve the specific course using get_object_or_404
    course = get_object_or_404(QMODEL.Course, id=id)

    # Get all questions related to the specified course
    submitted_questions = QMODEL.Question.objects.filter(course=course)

    # Create a dictionary to store question results
    question_results = {}

    for question in submitted_questions:
        # Fetch the result for the specific question and course
        result = QMODEL.Result.objects.filter(exam=course, student=request.user.student).first()

        # Store the question and result in the dictionary
        question_results[question] = result

    context = {
        'course': course,
        'submitted_questions': question_results,
    }

    return render(request, 'student/check_marks.html', context)


# @login_required(login_url='studentlogin')  # Ensure the user is logged in to access this view


# def check_marks_view(request, pk):
#     try:
#         # Get the logged-in user (student) by primary key
#         student = models.Student.objects.get(pk=pk)
        
#         # Filter questions based on the courses taken by the student
#         submitted_questions = QMODEL.Question.objects.filter(course__student=student)
        
#         return render(request, 'student/check_marks.html', {'submitted_questions': submitted_questions})
#     except ObjectDoesNotExist:
#         # Handle the case where the student does not exist
#         # You can return an error page or redirect to another view
#         return render(request, 'student/student_not_found.html')


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_marks.html',{'courses':courses})
  

# @login_required(login_url='studentlogin')  
# def view_results(request):
#     # Get all the submitted questions and their options
#     submitted_questions = QMODEL.Question.objects.all()

#     # Get the results for each submitted question
#     question_results = []
#     for question in submitted_questions:
#         results = QMODEL.Result.objects.filter(exam=question.course, student=request.user.student)
#         question_results.append((question, results))

#     context = {
#         'submitted_questions': question_results,
#     }

#     return render(request, 'student/check_marks.html', context)