# from django.db.models import Count
# from django.db.models import Max
# from django.contrib.sessions.models import Session
# from manager.models import Patrol
from member.models import Camp
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from core.models import Complete, Profile, UserFile, User
from .forms import ResultForm, AttendanceForm, SelectMember
from .cryptography import encrypt_value, decrypt_value
from django.http import JsonResponse
from .models import Attendance
from datetime import date
# Create your views here.


today = date.today()


@ login_required()
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
                title=title, member=member, date=today).exists()

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


@ login_required()
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


@ login_required()
def contact(request):
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


@ login_required()
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

            comp.completed = today
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


@ login_required()
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


@ login_required()
def view_examine(request):
    """ view tab badges """

    # badges applied for
    applies = Complete.objects.filter(stage=1).all()

    context = {
        'title': 'examine',
        'applies': applies,
    }
    return render(request, 'patrol/badges', context)


""" view member profiles """


@ login_required()
def view_member(request, user_id):

    profile = Profile.objects.get(user=user_id)
    patrol_m = profile.patrol.id
    patrol_l = request.session.get('s_patrol_id')
    print(f'Patrol id is -- {patrol_l} and {patrol_m}')
    valid = False
    profiles = Profile.objects.filter(patrol=patrol_l).all()
    form = SelectMember(initial={'members': profiles})

    try:
        if (patrol_m == patrol_l):
            valid = True

        if (valid):
            # badges completed
            badges = profile.badges.all()
            # badges applied for
            applies = Complete.objects.filter(stage=1).all()

            context = {
                'title': 'profiles',
                'badges': badges,
                'profile': profile,
                'applies': applies,
                'form': form,
            }
            return render(request, 'patrol/profile', context)

        members = Profile.objects.filter(patrol=patrol_l).all()
        # .select_related('badges').select_related('requirement').annotate(
        #     max_level=Max('badge__level')).order_by('-level').first()

        context = {
            'title': 'profiles',
            'members': members,
            'form': form,
        }
        return render(request, 'patrol/profile', context)
    except:
        context = {
            'title': 'profiles',
            'members': members,
            'form': form,
        }
        return render(request, 'patrol/profile', context)


""" view prifile tab """


def view_profile(request):

    patrol_l = request.session.get('s_patrol_id')
    profiles = Profile.objects.filter(patrol=patrol_l).all()
    form = SelectMember(initial={'members': profiles})

    try:
        name = request.GET.get('member')
        profile = Profile.objects.get(pk=name)
        user = profile.user
        files = UserFile.objects.get(user=user)
        hikes = profile.hikes.all()
        camps = profile.camps.all()
        projects = profile.projects.all()
        nights = Camp.objects.filter(id__in=camps).aggregate(
            Sum('nights'))['nights__sum']

    except Exception as e:
        print(e)
        print("no profile")
        user = None
        files = None
        camps = None
        nights = None
        profile = None
        hikes = None
        projects = None
        camps = None
        files = None

    context = {
        'title': 'profiles',
        'files': files,
        'profile': profile,
        'nights': nights,
        'form': form,
        'camps': camps,
        'hikes': hikes,
        'projects': projects,
        'files': files,
    }

    return render(request, 'patrol/profile', context)


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
