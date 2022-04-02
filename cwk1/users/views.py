from curses.ascii import HT
from urllib import response
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Student, Module, Professor, Dep_Mod, Dep_Stud, Department, Rating, Prof_Rating, Prof_Mod
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound
import json

# Create your views here.


def main_page(request,username):

    user = Student.objects.get(student=request.user)
    print(request.session)
    dep_stud = Dep_Stud.objects.get(student = user)

    modules = Dep_Mod.objects.filter(department = dep_stud.department)
    #user2 = User.objects.get(pk=4)
    #professor = Professor.objects.get(professor=user2)
    #prof_rating = Prof_Rating.objects.filter(professor=professor)
    

    context = {
        'modules' : modules,
    }

    print(modules)
    return render(request, 'main_page.html',context)


def Login(request):

    if request.method == 'POST':
        data = request.POST
        print(data.get('username'))
        userName = data.get('username')
        print(data.get('password'))
        user = authenticate(username=data.get('username'),password=data.get('password'))
        print(user)
        if user is not None:
            print(user.id)
            request.session['id'] = user.id
            request.session['username'] = user.username
            login(request,user)
            return HttpResponse("user found")
        else:
            return HttpResponseNotFound("user not found")   
            
    if request == 'GET':
        print("we are in get")
    return render(request,'login.html')


def register(request):

    if request.method == 'POST':
        data = request.POST
        print(data.get('email'))
        print(data.get('username'))
        print(data.get('password'))
        emailIn = data.get('email')
        usernameIn = data.get('username')
        passwordIn = data.get('password')
        
        print(emailIn)
        print(usernameIn)
        if (User.objects.filter(email=emailIn).exists() == True) or (User.objects.filter(username = usernameIn).exists() == True):
            print("user exists")
            return HttpResponseNotFound("user already exists")
        else:
            user = User.objects.create_user(email=emailIn,username=usernameIn, password=passwordIn)
            idIn = generate_id(str(usernameIn))
            ppap = (validate_id(idIn))
            print(ppap)
            stud = Student(student = user,student_code = ppap)
            stud.save()
            print("user created")
        return HttpResponse("user created")
    
    if request.method == 'GET':
         return render(request,'login.html')
    
def rating(request):
    
    if request.method == 'POST':
        data = request.POST
        name = data.get('name')
        user2 = User.objects.get(username = name)
        professors = Professor.objects.all()
        rating = []
        if professors.count() > 0:
            
            for p in professors:
                print(p)
                prof_rating = Prof_Rating.objects.filter(professor=p).all()
                rating.append(prof_rating)
            
            print(rating[0][0].module.year)
            context = {
                'rating' : rating,
            }
            return render(request,'rating.html',context)

        else:
            return HttpResponseNotFound("user not found")
        
    if request.method == 'GET':
        return render(request,'ratingform.html')

def average(request):
    if request.method == 'GET':
        return render(request, "average.html")

    if request.method == 'POST':
        data = request.POST
        name = data.get('name')
        module = data.get('module_code')

        professor = Professor.objects.filter(professor_code = name).first()
        module = Module.objects.filter(module_code = module).all()
        total_rating_points = 0
        total_rating = 0
        for m in module:
            ratings = Prof_Mod.objects.filter(professor = professor, module = m).all()
            for rating in ratings:
                print(rating.rating.rating)
                total_rating_points = total_rating_points + int(rating.rating.rating)
                total_rating += 1
        if total_rating_points == 0:
            average_rating =  0
        else:
            average_rating = total_rating_points/total_rating

        print(average_rating)
        if average_rating:

            context = {
                professor.professor.username : (average_rating)
            }
            print(context)
            return HttpResponse(json.dumps(context), content_type="application/json")
        else:
            return HttpResponseNotFound("not found")
    return render(request,"average.html")

def rate(request):
    if request.method == 'GET':
        return render(request, "rateform.html")

    if request.method == 'POST':
        data = request.POST
        year = data.get('year')
        module_code = data.get('module_code')
        semester = data.get('semester')
        module = Module.objects.get(module_code = module_code,year = year,semester=semester)
        if not module:
            return HttpResponseNotFound("module not found")
        code = data.get('prof_code')

        professor = Professor.objects.get(professor_code = code)
        if not professor:
            return HttpResponseNotFound("professor not found")
        rating = int(data.get('rating'))
        rating = Rating.objects.get(pk = rating)
        prof_rating = Prof_Mod(professor = professor, module = module, rating = rating)
        prof_rating.save()
        print(prof_rating)
        print(request.POST)
        return HttpResponse('found')


def check(profIn, listIn):

    for p in listIn:
        if profIn == p:
            return False
    return True


def list(request):
    if request.method == 'GET':
        modules = Module.objects.all()
        prof_mod2 = Prof_Mod.objects.all()
        prof_mod = {}
        professors = []
        i = 1     
        for m in modules.iterator():   
            string = "module_" + str(i)
            prof_mod[string] = m.module_name
            string = "year_" + str(i)
            prof_mod[string] = m.year
            string = "semester_" + str(i)
            prof_mod[string] = m.semester
            
            for prof in prof_mod2.iterator():

                if m == prof.module:
                    if len(professors) == 0:
                        professors.append(prof.professor.professor.username)
                    else:
                        print(prof.professor)
                        print(professors)
                        print(check(prof.professor.professor.username,professors))
                        if check(prof.professor.professor.username,professors) == True:
                            professors.append(prof.professor.professor.username)
                    
            string = "professor_" + str(i)
            prof_mod[string] = professors
            i += 1
            professors = []


    return HttpResponse(json.dumps(prof_mod), content_type="application/json")

def Logout(request):
    logout(request)
    print(request.user)
    return HttpResponse("logged out")

def view(request):
    context = {}

    professors = Professor.objects.all()

    for professor in professors:
        professor_name = professor.professor.username
        total_rating = 0
        prof_ratings = Prof_Mod.objects.filter(professor = professor).all()
        print(len(prof_ratings))
        if len(prof_ratings) == 0:
            average_rating = 0
        else: 
            for prof_rating in prof_ratings:
                print(prof_rating)
                total_rating += prof_rating.rating.rating
            average_rating = int(total_rating/len(prof_ratings))
        context[professor_name] = average_rating
    
    return HttpResponse(json.dumps(context), content_type="application/json")

def generate_id(strIn):
    id = strIn[0] + strIn[-1].upper() + str(1)
    return id

def extract_int(strIn):
    string = ""
    for c in strIn:
        if c.isdigit() == True:
            string += c
    return int(string)

def validate_id(idIn):
    ids = []
    print(idIn)
    
    students = Student.objects.all()
    professors = Professor.objects.all()
    for student in students:
        ids.append(student.student_code)

    for professor in professors:
        ids.append(professor.professor_code)
    print(ids)
    str2 = idIn
    add = False
    for id in ids:
        num = 0
        if str2 == id:
            num = extract_int(str2) + 1
            str2 = ""
            for char in range(len(idIn)-1):
                str2 += idIn[char]
            print("str2 =",str2)
            print(num)
            add = True
        if add == True:
            str2 += str(num)
            add = False
        else:
            add == False
            
    
    print("str2 =",str2)
    return str2

