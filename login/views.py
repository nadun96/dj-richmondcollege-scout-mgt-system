
from django.urls import reverse
import os
import time
from manager.models import Post, Photo
from member.models import Requirement
from core.models import Profile, UserFile
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.validators import FileExtensionValidator
from django.core.files.storage import default_storage
from django.views.generic import ListView
from django.conf import settings
from django.db.models import Max
from django.contrib.auth import get_user_model
User = get_user_model()
# current active user model


def home(request):
    context = {
        'title': 'home'
    }
    return render(request, 'login/login', context)


def signup(request):
    # generate student number
    max_id = User.objects.aggregate(id=Max('id'))
    max_id = int(max_id['id']) + 1
    currentYear = time. strftime("%Y")
    username = f'SC/{currentYear}/{str(max_id)}'

    # pass data to  context
    context = {
        'title': 'register',
        'next_id': username
    }
    return render(request, 'login/signup', context)


def register(request):

    context = {}

    if request.method == "POST":

        # variables request.POST
        student_surname = request.POST.get('student_surname')
        student_initials = request.POST.get('student_initials')
        student_birthday = request.POST.get('student_birthday')
        student_username = request.POST.get('student_username')
        student_email = request.POST.get('student_email')
        student_entrance = request.POST.get('student_entrance')
        student_contact = request.POST.get('student_contact')
        student_residence = request.POST.get('student_residence')
        student_father = request.POST.get('student_father')
        student_other_skills = request.POST.get('student_skills')
        student_sports = request.POST.get('student_sports')
        student_password = request.POST.get('student_password')

        # variables request.FILES
        student_letter = request.FILES['student_letter']
        student_medical = request.FILES['student_medical']
        student_photo = request.FILES['student_photo']

        # validate files
        image_validator = FileExtensionValidator(['jpg', 'jpeg', 'png'])
        file_validator = FileExtensionValidator(
            ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])
        image_validator(student_photo)
        file_validator(student_letter)
        file_validator(student_medical)

        # Change the file name to a custom name with the same file type
        _, file_extension = os.path.splitext(student_photo.name)
        student_photo.name = repr(student_username) + file_extension

        _, file_extension = os.path.splitext(student_letter.name)
        student_letter.name = repr(student_username) + file_extension

        _, file_extension = os.path.splitext(student_medical.name)
        student_medical.name = repr(student_username) + file_extension

        # create user object
        user = User.objects.create_user(
            username=student_username,
            email=student_email,
            password=student_password
        )

        # save user FILES object
        user_files = UserFile.objects.create(
            user=user, letter=student_letter, medical=student_medical, picture=student_photo)

        user_files.save()

        # instead of signals
        student_profile = Profile.objects.create(
            user=user,  # this is the foreign key
            surname=student_surname,
            initials=student_initials,
            entrance_number=student_entrance,
            email=student_email,
            father=student_father,
            skills=student_other_skills,
            sports=student_sports,
            birthday=student_birthday,
            contact=student_contact,
            address=student_residence,
        )

        student_profile.save()

        context = {'title': 'success'}

        render(request, 'login/login', context)


""" # call auth login function """


def user_login(request):

    # try:
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        #next_url = request.POST.get('next', '/')
        # return redirect(next_url)
        return redirect(reverse('member:profile', kwargs={'user_id': request.user.id}))

    else:
        context = {
            'title': 'login',
            'messages': messages.get_messages(request)
        }
        LOG_IN_URL = reverse('home:home')
        return redirect(LOG_IN_URL, context)


""" # call auth logout function """


def user_logout(request):
    logout(request)
    return redirect(reverse('home:home'))


""" view home events """


def events(request):
    photos = Photo.objects.all().order_by('-date')

    context = {
        'title': 'events',
        'photos': photos,
    }

    return render(request, 'login/events', context)


def requirements(request):

    requires = Requirement.objects.all().select_related('badge')\
        .values(
        'badge__level', 'badge__name', 'badge__description', 'number', 'name', 'description')\
        .order_by('badge__level', 'number')

    context = {
        'title': 'badges',
        'requires': requires,
    }

    print(requires)
    return render(request, 'login/badges', context)


class MyCardView(ListView):
    model = Photo
    template_name = 'events'
    context_object_name = 'photos'
    paginate_by = 2
