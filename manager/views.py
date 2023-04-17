from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection, transaction
from .forms import CampForm, ProjectForm, HikeForm, UploadPostsForm, UploadPhotoForm, AnnounceForm, RequirementForm, BadgeForm, AddPatrolForm, EndPatrolForm, AssignPatrolForm, ActivateMemberForm, MembershipFeeForm, AssignRoleForm, AssignLeaderForm, MemberAttendanceForm, PatrolAttendanceForm, EventAttendanceForm, MembershipFeeListForm
from patrol.forms import AttendanceForm
from patrol.models import Attendance
from member.models import Hike, Camp, Project, Badge, Requirement
from core.models import Profile, MemberRole, Complete, Patrol, Communication, User, MembershipFee, Leader
from datetime import date
import datetime
from .models import Photo, Post, Announcement, Patrol
from .reports import generate_member_attendance_report, generate_patrol_attendance_report, generate_event_attendance_report, generate_member_attendance_report_new, generate_patrol_attendance_report_new, generate_event_attendance_report_new, generate_membership_fee_paid_report_new, generate_event_list_report_new


""" get current active user model, current is core.User"""
User = get_user_model()

today = date.today()

""" Add Attendance """


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


""" view tab for Attendance """


@ login_required()
def view_attendance(request):
    profile = Profile.objects.get(user=request.user)
    members = Profile.objects.filter().all()
    attends = Attendance.objects.filter(
        member__in=members).select_related('user')\
        .values(
            'title', 'marker__user__username', 'date', 'member__user__username', 'time'
    )\
        .order_by('-date')

    form = AttendanceForm(
        initial={'marker': profile, 'member': members})

    context = {
        'title': 'attendance',
        'attends': attends,
        'form': form,
    }

    return render(request, 'manager/attendance', context)


""" manage roles """


@ login_required
def manage_roles(request):
    activate_form = AssignRoleForm(initial={'role': 2})

    context = {
        'title': 'manage_roles',
        'activate_form': activate_form,
        'roles': MemberRole.objects.all(),
    }
    return render(request, 'manager/manage_role', context)


""" manage leaders """


@ login_required
def manage_leaders(request):

    leader_form = AssignLeaderForm()

    leaders = Leader.objects.all()

    context = {
        'title': 'manage_leaders',
        'leader_form': leader_form,
        'leaders': leaders,
    }
    return render(request, 'manager/manage_leader', context)


""" add membership fee """


@login_required()
def add_membership_fee(request):
    if request.method == 'POST':
        response_data = {}
        membershipFeeForm = MembershipFeeForm(request.POST)

        if membershipFeeForm.is_valid():
            amount = int(request.POST.get('amount'))
            for_year = request.POST.get('for_year')
            profile = int(request.POST.get('member'))
            is_paid = bool(request.POST.get('is_paid'))

            try:
                obj = MembershipFee.objects.get(
                    for_year=for_year, member_id=profile, is_paid=True)
                response_data['result'] = 'exist'
                print(f'Object Exist {obj.id}')
            except MembershipFee.DoesNotExist:
                obj = MembershipFee.objects.create(
                    for_year=for_year, member_id=profile, is_paid=is_paid, amount=amount)
                obj.save()
                print(f'Object Created {obj.id}')
                response_data['result'] = 'success'

        return HttpResponse(
            JsonResponse(response_data),
        )

    else:
        response_data['result'] = 'error'
        return HttpResponse(
            JsonResponse(response_data),
        )


""" activate member """


@login_required()
def activate_member(request):
    if request.method == 'POST':
        response_data = {}
        activateForm = ActivateMemberForm(request.POST)
        if activateForm.is_valid():
            is_active = bool(request.POST.get('active'))
            member = int(request.POST.get('member'))
            member = User.objects.get(id=member)
            member.is_active = is_active
            member.save()
            response_data['result'] = 'success'
        return HttpResponse(
            JsonResponse(response_data),
        )
    else:
        response_data['result'] = 'error'
        return HttpResponse(
            JsonResponse(response_data),
        )


""" ajax get announcements """


@login_required()
def get_announce(request):
    announcements = Announcement.objects.all()
    announcements = list(announcements.values())
    return JsonResponse(announcements, safe=False)


""" ajax add announcement """


@login_required()
def add_announce(request):
    if request.method == 'POST':
        response_data = {}
        announceForm = AnnounceForm(request.POST, request.FILES)
        if announceForm.is_valid():
            title = request.POST.get('title')
            content = request.POST.get('content')
            file = request.FILES.get('file')
            announcement = Announcement.objects.create(
                title=title, content=content, file=file)
            announcement.save()
            response_data['result'] = 'success'
        return HttpResponse(
            JsonResponse(response_data),
        )
    else:
        response_data['result'] = 'error'
        return HttpResponse(
            JsonResponse(response_data),
        )


""" ajax assign patrol to member """


@login_required()
def assign_patrol(request):
    if request.method == 'POST':
        response_data = {}
        assignForm = AssignPatrolForm(request.POST)
        if assignForm.is_valid():
            patrol = request.POST.get('patrol')
            member = request.POST.get('member')
            patrol = Patrol.objects.get(id=patrol)
            profile = Profile.objects.get(id=member)
            profile.patrol = patrol
            profile.save()
            response_data['result'] = 'success'
        return HttpResponse(
            JsonResponse(response_data),
        )
    else:
        response_data['result'] = 'error'
        return HttpResponse(
            JsonResponse(response_data),
        )


""" ajax remove leader from leader list """


@login_required()
def rm_leader(request):
    if request.method == 'POST':
        response_data = {}
        patrolForm = AddPatrolForm(request.POST)
        print(patrolForm.errors)
        if patrolForm.is_valid():
            patrolForm.save()
            response_data['result'] = 'success'
        return HttpResponse(
            JsonResponse(response_data),
        )
    else:
        response_data['result'] = 'error'
        return HttpResponse(
            JsonResponse(response_data))


""" ajax add leader to leader list or deactivate """


@login_required()
def toggle_leader(request):
    if request.method == 'POST':

        response_data = {}
        name = int(request.POST.get('name'))
        patrol = int(request.POST.get('patrol'))
        form = AssignLeaderForm(request.POST)

        if form.is_valid():
            name = Profile.objects.get(id=name)
            patrol = Patrol.objects.get(id=patrol)
            print(name)
            print(patrol)

            pat = name.patrol
            print(name.patrol)

            is_same = True
            if (pat != patrol):
                is_same = False

            exist = Leader.objects.filter(
                name=name, patrol=patrol)\
                .exists()

            if (exist and is_same):
                with transaction.atomic():
                    ml = Leader.objects.get(name=name, patrol=patrol)
                    ml.is_active = not ml.is_active
                    if (not ml.is_active):
                        ml.end = datetime.date.today()
                    else:
                        ml.end = None
                    ml.save()

                response_data['result'] = 'exist'
                print(
                    f'Object Exist\t pk - {ml.pk}\t Patrol - {ml.patrol} \t leader - {ml.name} \t active - {ml.is_active}')
            else:
                ml = Leader.objects.create(name=name, patrol=patrol)
                ml.save()

            print('form is valid')

            response_data['result'] = 'success'

            return HttpResponse(
                JsonResponse(response_data),
            )

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    print(error)

            response_data['result'] = 'invalid'
            return HttpResponse(
                JsonResponse(response_data),
            )
    else:
        response_data['result'] = 'error'
        return HttpResponse(
            JsonResponse(response_data))


""" get roles """


@login_required()
def get_roles(request):
    roles = MemberRole.objects.all()
    roles = list(roles.values())
    return JsonResponse(roles, safe=False)


""" ajax add role to role list """


def set_auth_role(profile, role):
    try:
        #user = User.objects.get(id=profile.user)
        user = profile.user
        print('user is - ' + str(user))

        mr = MemberRole.objects.get(profile=profile, role=role)

        print(mr.pk)

        print(f'mr is - {str(mr.pk)} \t {mr.role} \t {mr.active}')

        active = mr.active
        if (role == 1):
            if (active):
                user.is_staff = True
                print('is_admin')
            else:
                user.is_staff = False

        elif (role == 2):
            if (active):
                user.is_mem = True
                print('is_mem')
            else:
                user.is_mem = False

        elif (role == 3):
            if (active):
                user.is_sec = True
                print('is_sec')
            else:
                user.is_sec = False

        elif (role == 4):
            if (active):
                user.is_skr = True
                print('is_skr')
            else:
                user.is_skr = False

        user.save()

    except Exception as e:
        print(e)
        print('error')


@login_required()
def toggle_role(request):
    if request.method == 'POST':
        response_data = {}
        profile = int(request.POST.get('profile'))
        role = request.POST.get('role')
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            print('form is valid')

            profile = Profile.objects.get(id=profile)

            val = Profile.objects.filter(id=profile.id).values()

            print(val)

            exist = MemberRole.objects.filter(
                profile=profile, role=role)\
                .exists()

            if (exist):
                mr = MemberRole.objects.get(profile=profile, role=role)
                mr.active = not mr.active
                response_data['result'] = 'exist'
                mr.save()

                print(f'Object Exist \
                    {mr.pk}-{mr.role}-{mr.profile}-{mr.active}')

                set_auth_role(profile=mr.profile, role=mr.role)
            else:
                mr = MemberRole.objects.create(profile=profile, role=role)
                mr.save()
                set_auth_role(profile=mr.profile, role=mr.role)

            response_data['result'] = 'success'

            return HttpResponse(
                JsonResponse(response_data),
            )

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    print(error)

            response_data['result'] = 'invalid'
            return HttpResponse(
                JsonResponse(response_data),
            )
    else:
        response_data['result'] = 'error'
        return HttpResponse(
            JsonResponse(response_data))


""" ajax add patrol to patrol list """


@login_required()
def add_patrol(request):
    if request.method == 'POST':
        response_data = {}
        patrolForm = AddPatrolForm(request.POST)
        print(patrolForm.errors)
        if patrolForm.is_valid():
            patrolForm.save()
            response_data['result'] = 'success'
        return HttpResponse(
            JsonResponse(response_data),
        )
    else:
        response_data['result'] = 'error'
        return HttpResponse(
            JsonResponse(response_data),
        )


""" ajax get profiles """


@login_required()
def get_profiles(request):
    if request.method == 'POST':
        profiles = Profile.objects.all()
        profiles = list(profiles.values())
        return JsonResponse(profiles, safe=False)


""" delete patrol from patrol list """


@login_required()
def del_patrol(request):

    try:
        if request.method == 'POST':

            response_data = {}
            patrolForm = EndPatrolForm(request.POST)

            if patrolForm.is_valid():
                patrol = request.POST.get('patrol')
                patrol = Patrol.objects.get(id=patrol)
                patrol.delete()
                response_data['result'] = 'success'
            return HttpResponse(
                JsonResponse(response_data),
            )

        else:
            response_data['result'] = 'error'
            return HttpResponse(
                JsonResponse(response_data),
            )

    except Exception as e:
        print(e)
        response_data['result'] = 'error'
        return HttpResponse(
            JsonResponse(response_data),
        )


""" ajax view patrol in patrol table """


@login_required()
def get_patrol(request):
    patrols = Patrol.objects.all().values()
    return JsonResponse(list(patrols), safe=False)


""" ajax add badge to badge list """


@login_required()
def add_badge(request):
    if request.method == 'POST':
        response_data = {}
        badgeForm = BadgeForm(request.POST)
        if badgeForm.is_valid():
            badgeForm.save()
            response_data['result'] = 'success'
        return HttpResponse(
            JsonResponse(response_data),
        )
    else:
        response_data['result'] = 'error'
        return HttpResponse(
            JsonResponse(response_data),
        )


""" ajax badges in badge table """


@login_required()
def get_badges(request):
    badges = Badge.objects.all().values()
    return JsonResponse(list(badges), safe=False)


""" ajax add requirement to requirement list """


@login_required()
def add_requirement(request):
    if request.method == 'POST':
        response_data = {}
        requirementForm = RequirementForm(request.POST)
        print(requirementForm.errors)
        if requirementForm.is_valid():
            requirementForm.save()
            response_data['result'] = 'success'
        return HttpResponse(
            JsonResponse(response_data),
        )
    else:
        response_data['result'] = 'error'
        return HttpResponse(
            JsonResponse(response_data),
        )


""" ajax requirements in requirements table """


@login_required()
def get_requirements(request):
    requirements = Requirement.objects.all().select_related('badge').values(
        'id', 'number', 'badge__name', 'name', 'description').order_by('badge__level', 'number')
    return JsonResponse(list(requirements), safe=False)


""" ajax add photo event to home wall """


@login_required()
def add_photo(request):
    if request.method == 'POST':
        response_data = {}
        photoForm = UploadPhotoForm(request.POST, request.FILES)
        print(photoForm.is_valid())
        print(photoForm.errors)
        if photoForm.is_valid():
            photoForm.save()
            response_data['result'] = 'success'
            print(response_data)
            return HttpResponse(
                JsonResponse(response_data),
            )
    else:
        response_data['result'] = 'error'
        print(photoForm.errors)
        return HttpResponse(
            JsonResponse(response_data),
        )


""" ajax add post to saturday wall """


@login_required()
def add_post(request):
    if request.method == 'POST':
        response_data = {}
        postForm = UploadPostsForm(request.POST, request.FILES)
        print(postForm.errors)
        if postForm.is_valid():
            postForm.save()
            response_data['result'] = 'success'
        return HttpResponse(
            JsonResponse(response_data),
        )
    else:
        response_data['result'] = 'error'
        return HttpResponse(
            JsonResponse(response_data),

        )


""" ajax add hike """


@ login_required
def add_hike(request):
    response_data['result'] = 'not loaded'
    if request.method == 'POST':
        response_data = {}
        form = HikeForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            response_data['result'] = 'success'
        return HttpResponse(
            JsonResponse(response_data),
        )
    else:
        response_data['result'] = 'error'

    return HttpResponse(
        JsonResponse(response_data),

    )


""" ajax add camp """


@login_required()
def add_camp(request):
    if request.method == 'POST':
        response_data = {}
        form = CampForm(request.POST)
        print(form)
        if form.is_valid():
            form.save()
            response_data['result'] = 'success'
        return HttpResponse(
            JsonResponse(response_data),
        )
    else:
        response_data['result'] = 'error'
        return HttpResponse(
            JsonResponse(response_data),

        )


""" ajax add project """


@login_required()
def add_project(request):
    if request.method == 'POST':
        response_data = {}
        form = ProjectForm(request.POST)

        print(form.is_valid())
        if form.is_valid():
            form.save()
            response_data['result'] = 'success'
        return HttpResponse(
            JsonResponse(response_data),
        )
    else:
        response_data['result'] = 'error'
        return HttpResponse(
            JsonResponse(response_data),

        )


""" navbar view tab rendering """


@login_required()
def manage_view(request):
    hikes = Hike.objects.all()
    projects = Project.objects.all()
    camps = Camp.objects.all()
    context = {
        'title': 'manage_view',
        'hikes': hikes,
        'projects': projects,
        'camps': camps,

    }
    return render(request, 'manager/manage_view', context)


""" navbar edit tab rendering """


@login_required()
def manage_events(request):
    hikes = HikeForm()
    camps = CampForm()
    projects = ProjectForm()
    context = {
        'title': 'manage_edit',
        'hikes': hikes,
        'camps': camps,
        'projects': projects,
    }
    return render(request, 'manager/manage_events', context)


""" navbar Uploads tab rendering """


@login_required()
def manage_wall(request):
    posts = UploadPostsForm()
    photo = UploadPhotoForm()
    context = {
        'title': 'manage_wall',
        'posts': posts,
        'photo': photo,
    }
    return render(request, 'manager/manage_wall', context)


""" navbar Home tab rendering """


@login_required()
def manage_patrols(request):
    add_patrol = AddPatrolForm()
    end_patrol = EndPatrolForm()
    assign_patrol = AssignPatrolForm()
    patrols = Patrol.objects.all()
    profiles = Profile.objects.all()
    context = {
        'title': 'manage_patrols',
        'add_patrol': add_patrol,
        'end_patrol': end_patrol,
        'patrols': patrols,
        'assign_patrol': assign_patrol,
        'profiles': profiles,
    }
    return render(request, 'manager/manage_patrols', context)


""" navbar Member tab rendering """


@login_required()
def manage_member(request):
    profiles = Profile.objects.all()
    activate = ActivateMemberForm()
    fees = MembershipFeeForm()
    pays = MembershipFee.objects.all().select_related('member').select_related('member__user').values(
        'id', 'member__user__username', 'for_year', 'member__user__is_active', 'is_paid')
    users = User.objects.all().values(
        'id', 'username', 'is_active', 'is_skr', 'is_mem', 'is_sec', 'is_ldr', 'is_exa', 'last_login')

    """ .select_related(
        'user').values_list('id', 'member__user_user', 'for_year', 'member__user__is_active', 'is_paid')
    #is_superuser, last_login, last_name, leader, logentry, message, password, profile, receiver, user_permissions, #username
    date_joined, email, first_name, groups, id, is_active, is_exa, is_ldr, is_mem, is_sec, is_skr, is_staff,
    print(profiles.values_list()) """

    context = {
        'title': 'manage_member',
        'profiles': profiles,
        'activate': activate,
        'fees': fees,
        'pays': pays,
        'users': users,
    }

    return render(request, 'manager/manage_member', context)


""" navbar Announce tab rendering """


@login_required()
def manage_announcements(request):
    announce_form = AnnounceForm()
    announce_table = Announcement.objects.all()
    context = {
        'title': 'manage_announce',
        'announce_form': announce_form,
        'announce_table': announce_table,
    }
    return render(request, 'manager/manage_announce', context)


""" manage badges tab render """


@login_required()
def manage_badges(request):

    context = {

    }
    add_badge = BadgeForm()
    add_requirement = RequirementForm()

    badges = Badge.objects.all().values()
    requirements = Requirement.objects.all().select_related('badge').values(
        'id', 'number', 'badge__name', 'name', 'description').order_by('badge__level', 'number')

    context = {
        'title': 'manage_badges',
        'add_badge': add_badge,
        'add_requirement': add_requirement,
        'badges': badges,
        'requirements': requirements,
    }

    return render(request, 'manager/manage_badge', context)


""" view reports tab render test function """


def test_pdf(request):
    # Generate the PDF report
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, "Attendance Report for John Doe - 2022")
    p.drawString(100, 730, "Date")
    p.drawString(200, 730, "Time")
    p.drawString(300, 730, "Title")
    p.drawString(100, 710, "01/01/2022")
    p.drawString(200, 710, "10:00 AM")
    p.drawString(300, 710, "Meeting")
    p.drawString(100, 690, "01/15/2022")
    p.drawString(200, 690, "02:30 PM")
    p.drawString(300, 690, "Training")
    p.showPage()
    p.save()

    # Set the buffer pointer to the beginning
    buffer.seek(0)

    # Return the PDF file as a response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=test_report.pdf'
    return response


""" view reports tab render function """

@login_required()
def view_reports(request):

    matf = MemberAttendanceForm()
    eatf = EventAttendanceForm()
    patf = PatrolAttendanceForm()
    
    myf = MembershipFeeListForm()

    context = {
        'title': 'reports',
        'matf': matf,
        'eatf': eatf,
        'patf': patf,
        'myf': myf,
    }

    return render(request, 'manager/reports', context)

""" member attendance report """

@login_required()
def member_attendance_report(request):

    if request.method == 'POST':
        form = MemberAttendanceForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data['year']
            member = form.cleaned_data['member']

            response = generate_member_attendance_report_new(year,member)
             
            #response = generate_member_attendance_report(
            #   year, member)
            return response

""" patrol attendance report """

@login_required()
def patrol_attendance_report(request):
    if request.method == 'POST':
        form = PatrolAttendanceForm(request.POST)
        if form.is_valid():
            year = form.cleaned_data['year']
            patrol = form.cleaned_data['patrol']

            print(year, patrol)

            response = generate_patrol_attendance_report_new(
                year, patrol)
            # response = generate_patrol_attendance_report(
            #     year, patrol)
            return response

""" event attendance report """

@login_required()
def events_attendance_report(request):
    if request.method == 'POST':
        form = PatrolAttendanceForm(request.POST)      
        if form.is_valid():
            title = request.POST.get('title')
            year = request.POST.get('year')
            print(year, title)
            response = generate_event_attendance_report_new(
                year, title)
            # response = generate_event_attendance_report(
            #     year, title)
            return response

""" membership fee paid report by year """

def extract_year(date_string):
    """
    Extracts the year part from a string in the format 'YYYY-MM-DD'.
    """
    year = date_string.split('-')[0]
    return year

""" membership fee paid report """

@login_required()
def membership_fee_paid_report(request):
    if request.method == 'POST':
        form = MembershipFeeListForm(request.POST)
        # if form.is_valid():
        year = form.data['year']
        year = extract_year(year)
        
        print(year)
        
        response = generate_membership_fee_paid_report_new(
                year)
        return response
    
""" event list report """

@login_required()
def events_list_report(request):
    if request.method == 'POST':
        form = MembershipFeeListForm(request.POST)
        # if form.is_valid():
        year = form.data['year']
        year = extract_year(year)
        
        print(year)
        
        response = generate_event_list_report_new(
                year)
        return response