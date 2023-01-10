from django.db.models import Count
from django.forms import modelform_factory
from django.http import HttpResponse
from django.shortcuts import redirect, render
from core.models import Complete, Profile, UserFile
from .forms import ResultForm, AttendanceForm
import datetime
from .cryptography import encrypt_value, decrypt_value
from django.http import JsonResponse
from django.db.models import Max
from django.contrib.sessions.models import Session
from manager.models import Patrol
from .models import Attendance
from datetime import date
# Create your views here.


today = date.today()


def add_attendance(request):
    """ ajax add Attendance """
    try:
        if request.method == 'POST':
            # check and get variables
            print("Form submitted:")
            print("----------------")
            title = request.POST.get('title')
            # marker = request.POST.get('marker')
            marker = request.session.get('_auth_user_id')
            print(f'marker is {marker}')
            member = request.POST.get('member')
            print(f'member is {member}')
            print("----------------")

            # check if already marked
            exist = Attendance.objects.filter(
                title=title, marker=marker, member=member, date=today).exists()

            print('exist: ', exist)

            # validate form
            form = AttendanceForm(request.POST)
            valid = form.is_valid()

            print("form is valid: ", valid)

            # check user == examiner
            if (marker == member or exist):
                valid = False

            if (valid):

                # get the object
                marker = Profile.objects.get(id=marker)
                member = Profile.objects.get(id=member)

                # create the object
                attend = Attendance.objects.create(
                    marker=marker, member=member, title=title)

                print("-------------------------")
                print(f"Attendance object marker: {attend.marker}")
                print(f"Attendance object member: {attend.member}")
                print(f"Attendance object date: {attend.date}")
                print(f"Attendance object time: {attend.time}")
                print("-------------------------")

                context = {
                    'result': 'success',
                }
                return HttpResponse(JsonResponse(context))
            else:
                context = {
                    'result': 'exist',
                }
                return HttpResponse(JsonResponse(context))

    except Exception as e:
        print(e)
        context = {
            'result': 'error',
        }
        return HttpResponse(JsonResponse(context))


def view_attendance(request):
    """ view tab for Attendance """

    patrol = request.session.get('s_patrol_id')
    profile = request.session.get('s_profile_id')
    print(f'Patrol id is -- {patrol}')

    members = Profile.objects.filter(patrol=patrol).all()
    attends = Attendance.objects.filter(
        member__in=members).select_related('user')\
        .values(
            'title', 'marker__user__username', 'date', 'member__user__username', 'time'
    )\
        .order_by('-date')

    """ attends = Attendance.objects.filter(member__in=members) \
                            .values('date') \
                            .annotate(count=Count('id')) """

    form = AttendanceForm(
        initial={'marker': profile, 'member': members})

    context = {
        'title': 'attendance',
        'attends': attends,
        'form': form,
    }

    return render(request, 'patrol/attendance', context)


def view_members(request):
    """ view tab members """

    patrol = request.session.get('s_patrol_id')
    print(f'Patrol id is -- {patrol}')
    members = Profile.objects.filter(patrol=patrol).all()
    # .select_related('badges').select_related('requirement').annotate(
    #     max_level=Max('badge__level')).order_by('-level').first()

    context = {
        'title': 'members',
        'members': members,
    }
    return render(request, 'patrol/members', context)


def evaluate(request):
    """ pass fail or apply for badge """
    context = {

    }

    if request.method == 'POST':
        # check and get variables
        print("Form submitted:")
        print("----------------")
        user = request.POST.get('user')
        print(f'user is {user}')
        examiner = request.POST.get('examiner')
        print(f'examiner is {examiner}')
        stage = request.POST.get('stage')
        print(f'stage is {stage}')
        requirement = request.POST.get('requirement')
        print(f'requirement is {requirement}')
        print("----------------")

        # validate form
        form = ResultForm(request.POST)
        valid = form.is_valid()

        # check user == examiner
        if (user == examiner):
            valid = False

        # check object exists
        exist = Complete.objects.filter(
            user=user, stage=1, requirement=requirement).exists()

        # check object count if multiple
        count = Complete.objects.filter(
            user=user, stage=1, requirement=requirement).count()

        print(f'is {requirement}, is {count} times is {exist}')

        if (valid and exist and count == 1):

            # get the object
            comp = Complete.objects.get(
                user=user, stage=1, requirement=requirement)

            # get the examiner
            examiner = Profile.objects.get(user=examiner)
            comp.examiner = examiner

            # update the object
            comp.stage = stage

            comp.completed = datetime.date.today()
            comp.save()

            print("-------------------------")
            print(f"Complete object user: {comp.user}")
            print(f"Complete object examiner: {comp.examiner}")
            print(f"Complete object stage: {comp.stage}")
            print(f"Complete object requirement: {comp.requirement}")
            print(f"Complete object applied: {comp.applied}")
            print(f"Complete object completed: {comp.completed}")
            print("-------------------------")

            context['result'] = 'success'

        return HttpResponse(JsonResponse(context))
    else:
        context['result'] = 'fail'
        return HttpResponse(JsonResponse(context))


def examine_form(request, pk):
    """ load examine form in a new tab after clicking on table link"""

    # get the object
    comp = Complete.objects.get(id=pk)
    # get the examiner
    examiner = Profile.objects.get(user=request.user)
    comp.examiner = examiner

    form = ResultForm(instance=comp)

    context = {
        'title': 'examine',
        'form': form,
    }
    return render(request, 'patrol/examine', context)


def view_examine(request, user_id):
    """ view tab badges """

    profile = Profile.objects.get(user=user_id)
    # badges completed
    badges = profile.badges.all()
    # badges applied for
    applies = Complete.objects.filter(stage=1).all()

    context = {
        'title': 'examine',
        'badges': badges,
        'profile': profile,
        'applies': applies,
    }
    return render(request, 'patrol/badges', context)


""" encrypt """


def view(request):
    # Encrypt the value
    encrypted_value = encrypt_value("my value")

    # Pass the encrypted value to the template
    return render(request, 'template', {'encrypted_value': encrypted_value})


""" decrypt """


def view(request):
    # Get the encrypted value from the request
    encrypted_value = request.POST.get('encrypted_value')

    # Decrypt the value
    decrypted_value = decrypt_value(encrypted_value, key)
