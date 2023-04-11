from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
import matplotlib.pyplot as plt
import pandas as pd
# imports for pdf
from django.contrib.auth.decorators import login_required
import datetime
from datetime import date
from django.db import connection, transaction
from django.http import JsonResponse, HttpResponse
from core.models import Profile, MemberRole, Complete, Patrol, Communication, User, MembershipFee, Leader
from django.shortcuts import render
from member.models import Hike, Camp, Project, Badge, Requirement
from .models import Photo, Post, Announcement, Patrol
from patrol.models import Attendance
from patrol.forms import AttendanceForm
from .forms import CampForm, ProjectForm, HikeForm, UploadPostsForm, UploadPhotoForm, AnnounceForm, RequirementForm, BadgeForm, AddPatrolForm, EndPatrolForm, AssignPatrolForm, ActivateMemberForm, MembershipFeeForm, AssignRoleForm, AssignLeaderForm
from django.db.models import Q, F
""" get current active user model, current is core.User"""
from django.contrib.auth import get_user_model
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


""" export attendance report """


@login_required()
def export_attendance(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'

    writer = csv.writer(response)
    writer.writerow(['Patrol', 'Date', 'Hike', 'Camp',
                    'Project', 'Meeting', 'Total'])

    patrols = Patrol.objects.all()
    for patrol in patrols:
        writer.writerow([patrol.name])
        for attendance in patrol.attendance_set.all():
            writer.writerow([attendance.date, attendance.hike, attendance.camp,
                            attendance.project, attendance.meeting, attendance.total])
        writer.writerow([])

    return response


""" generate pdf report """


def generate_attendance_report(year: int):
    # Query the database to get the attendance data for the given year
    attendance_data = Attendance.objects.filter(date__year=year)

    # Create a pandas DataFrame from the attendance data
    attendance_df = pd.DataFrame(list(attendance_data.values()))

    # Group the attendance data by member and calculate the total attendance for each member
    member_attendance = attendance_df.groupby(
        ['member']).size().reset_index(name='attendance_count')

    # Create a table from the member attendance data
    member_attendance_table = Table(
        data=[['Member', 'Attendance']] + [[row['member'], row['attendance_count']]
                                           for _, row in member_attendance.iterrows()],
        colWidths=[4.5*inch, 1*inch],
        hAlign='LEFT'
    )

    # Add a style to the table
    member_attendance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # Create a pandas DataFrame for the weekly attendance data
    weekly_attendance = attendance_df.groupby(pd.Grouper(
        key='date', freq='W')).size().reset_index(name='attendance_count')

    # Create a line graph of the weekly attendance data
    fig, ax = plt.subplots()
    ax.plot(weekly_attendance['date'], weekly_attendance['attendance_count'])
    ax.set(xlabel='Week', ylabel='Attendance', title='Weekly Attendance')
    ax.grid()

    # Generate the pdf report with the table and the line graph
    doc = SimpleDocTemplate(
        f'{year}_attendance_report.pdf', pagesize=landscape(letter))
    elements = []
    elements.append(member_attendance_table)
    elements.append(plt.gcf())
    doc.build(elements)
