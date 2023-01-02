import datetime
from django.db import connection, transaction
from django.http import JsonResponse, HttpResponse
from core.models import Profile, MemberRole, Complete, Patrol, Communication, User, MembershipFee, Leader
from member.models import Hike, Camp, Project, Badge, Requirement
from django.shortcuts import render
from .models import Photo, Post, Announcement, Patrol
from .forms import CampForm, ProjectForm, HikeForm, UploadPostsForm, UploadPhotoForm, AnnounceForm, RequirementForm, BadgeForm, AddPatrolForm, EndPatrolForm, AssignPatrolForm, ActivateMemberForm, MembershipFeeForm, AssignRoleForm, AssignLeaderForm
from django.db.models import Q, F
""" get current active user model, current is core.User"""
from django.contrib.auth import get_user_model
User = get_user_model()


""" manage roles """


def manage_roles(request):
    activate_form = AssignRoleForm()

    context = {
        'title': 'manage_roles',
        'activate_form': activate_form,
        'roles': MemberRole.objects.all(),
    }
    return render(request, 'manager/manage_role', context)


""" manage leaders """


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


def get_announce(request):
    announcements = Announcement.objects.all()
    announcements = list(announcements.values())
    return JsonResponse(announcements, safe=False)


""" ajax add announcement """


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


def toggle_leader(request):
    if request.method == 'POST':

        response_data = {}
        name = int(request.POST.get('name'))
        patrol = int(request.POST.get('patrol'))
        form = AssignLeaderForm(request.POST)

        if form.is_valid():
            name = Profile.objects.get(id=name)
            patrol = Patrol.objects.get(id=patrol)

            exist = Leader.objects.filter(
                name=name, patrol=patrol)\
                .exists()

            if (exist):
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


def get_roles(request):
    roles = MemberRole.objects.all()
    roles = list(roles.values())
    return JsonResponse(roles, safe=False)


""" ajax add role to role list """


def toggle_role(request):
    if request.method == 'POST':

        response_data = {}
        profile = int(request.POST.get('profile'))
        role = request.POST.get('role')
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            profile = Profile.objects.get(id=profile)

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
            else:
                mr = MemberRole.objects.create(profile=profile, role=role)
                mr.save()

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


""" ajax add patrol to patrol list """


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


def get_profiles(request):
    profiles = Profile.objects.all()
    profiles = list(profiles.values())
    return JsonResponse(profiles, safe=False)


""" delete patrol from patrol list """


def del_patrol(request):
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


""" ajax view patrol in patrol table """


def get_patrol(request):
    patrols = Patrol.objects.all().values()
    return JsonResponse(list(patrols), safe=False)


""" ajax add badge to badge list """


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


def get_badges(request):
    badges = Badge.objects.all().values()
    return JsonResponse(list(badges), safe=False)


""" ajax add requirement to requirement list """


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


def get_requirements(request):
    requirements = Requirement.objects.all().select_related('badge').values(
        'id', 'number', 'badge__name', 'name', 'description').order_by('badge__level', 'number')
    return JsonResponse(list(requirements), safe=False)


""" ajax add photo event to home wall """


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


def add_hike(request):
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


def manage_edit(request):
    hikes = HikeForm()
    camps = CampForm()
    projects = ProjectForm()
    context = {
        'title': 'manage_edit',
        'hikes': hikes,
        'camps': camps,
        'projects': projects,
    }
    return render(request, 'manager/manage_edit', context)


""" navbar Uploads tab rendering """


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


def manage_member(request):
    profiles = Profile.objects.all()
    activate = ActivateMemberForm()
    fees = MembershipFeeForm()
    pays = MembershipFee.objects.all().select_related('member').select_related('member__user').values(
        'id', 'member__user__username', 'for_year', 'member__user__is_active', 'is_paid')
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
    }

    return render(request, 'manager/manage_member', context)


""" navbar Announce tab rendering """


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
