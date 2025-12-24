from django.db.models import Sum
from core.views import session_processor
import datetime
from django.contrib.auth.decorators import login_required
from core.models import Complete, Profile, User, UserFile
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from manager.models import Announcement, Communication, Patrol, Photo, Post

from .forms import (
    FilesUpdateForm,
    MemberCampForm,
    MemberHikeForm,
    MemberProjectForm,
    MemberRequirementForm,
    ProfileUpdateForm,
)
from .models import Badge, Camp, Hike, Project, Requirement

""" view saturday posts """


@login_required()
def saturday_posts(request):
    posts = Post.objects.all().order_by("-id")
    context = {
        "title": "articles",
        "posts": posts,
    }
    return render(request, "manager/post_list", context)


""" update profile details specific user """


@login_required()
def profile_update(request):
    try:
        if request.method == "POST":
            # POST para
            prof = request.POST.get("pro")
            print(prof)
            email = request.POST.get("email")
            skills = request.POST.get("skills")
            sports = request.POST.get("sports")
            address = request.POST.get("address")
            contact = request.POST.get("contact")

            # FILES para
            picture = request.FILES.get("picture")
            medical = request.FILES.get("medical")

            # get user and profile
            pro = Profile.objects.get(id=prof)
            user_id = pro.user.id
            print(f"uid is: {user_id}")
            user = User.objects.get(id=user_id)
            print(f"user is: {user}")
            print(user.username)
            files, _ = UserFile.objects.get_or_create(user=user)
            print(f"files is: {files}")
            profile, _ = Profile.objects.get_or_create(user=user)

            context = {}

            # save to object
            if email and profile:
                profile.email = email
                print(f"email set: {profile.email}")
            if skills and profile:
                profile.skills = skills
            if sports and profile:
                profile.sports = sports
            if address and profile:
                profile.address = address
            if picture and files:
                files.picture = picture
                print(f"picture set: {files.picture.name}")
            if contact and profile:
                profile.contact = contact

            if medical and files:
                files.medical = medical

            # update database
            if profile:
                profile.save()
            else:
                context = {"result": "User Does Not Exist"}
                print(context)

            if files:
                files.save()
                print(f"files saved: {files.picture.name}")
            else:
                context = {"result": "User files Does Not Exist"}
                print(context)

            if profile and files:
                context = {"result": "success"}

            return HttpResponse(JsonResponse(context))

    except Exception as e:
        print(e)
        context = {"result": "error"}
        return HttpResponse(JsonResponse(context))


""" view profile """


@login_required()
def view_profile(request):
    profile = Profile.objects.all()
    files = UserFile.objects.all()
    file_form = FilesUpdateForm()
    update_form = ProfileUpdateForm()

    context = {
        "title": "profile",
        "files": files,
        "profile": profile,
        "file_form": file_form,
        "update_form": update_form,
    }

    return render(request, "member/profile", context)


""" view profile details specific user """


@login_required()
def user_profile(request, user_id):
    result = session_processor(request)
    print(result)
    # Get the user with the specified ID
    user = User.objects.get(id=user_id)
    profile, _ = Profile.objects.get_or_create(user=user)
    files, _ = UserFile.objects.get_or_create(user=user)
    camps = profile.camps.all()
    nights = Camp.objects.filter(id__in=camps).aggregate(Sum("nights"))["nights__sum"]
    print(nights)

    file_form = FilesUpdateForm()
    update_form = ProfileUpdateForm()
    picture_url = files.picture.url if files.picture else static("img/symbol.png")

    context = {
        "title": "profile",
        "files": files,
        "profile": profile,
        "file_form": file_form,
        "update_form": update_form,
        "nights": nights,
        "picture_url": picture_url,
    }

    return render(request, "member/profile", context)


""" hikes for specific user done """


@login_required()
def hikes(request, user_id):
    add_hike = MemberHikeForm()
    user = User.objects.get(pk=user_id)
    profile, _ = Profile.objects.get_or_create(user=user)
    hikes = profile.hikes.all()
    context = {
        "title": "hikes",
        "hikes": hikes,
        "add_hike": add_hike,
        "profile": profile,
    }

    return render(request, "member/hikes", context)


""" add Hike to profile """


@login_required()
def add_hike(request):
    context = {"result": "not loaded"}
    if request.method == "POST":
        profile = int(request.POST.get("pro"))
        hike = int(request.POST.get("hike"))
        profile = Profile.objects.get(id=profile)
        hike = Hike.objects.get(id=hike)
        if hike:
            if profile.hikes.filter(id=hike.id).exists():
                print("hike already exists")
            else:
                profile.hikes.add(hike)
                profile.save()
                print("camp added")
        else:
            print("project does not exist")

        context = {"result": "success"}

    return HttpResponse(JsonResponse(context))


""" view hikes page """


@login_required()
def view_hikes(request):
    context = {"title": "hikes"}
    return render(request, "member/hikes", context)


""" badges """


@login_required()
def view_badges(request):
    context = {"title": "badges"}
    return render(request, "member/badges", context)


""" get badges for specific user """


@login_required()
def badges(request, user_id):
    user = User.objects.get(id=user_id)
    profile, _ = Profile.objects.get_or_create(user=user)
    # badges completed
    badges = profile.badges.all()
    # badges applied for
    applies = Complete.objects.all()

    context = {
        "title": "badges",
        "badges": badges,
        "apply_form": MemberRequirementForm(),
        "profile": profile,
        "applies": applies,
    }
    return render(request, "member/badges", context)


""" add Badge to profile """


@login_required()
def apply_requirement(request):
    context = {"result": "not loaded"}

    if request.method == "POST":
        # save profile and requirement id to objects
        pro = request.POST.get("pro")
        print(f"pro is {pro}")
        pro = int(pro)
        print(f"int pro is {pro}")
        requirement = request.POST.get("requirement")
        print(f"require is {requirement}")
        requirement = int(requirement)
        print(f"int require is {requirement}")

        # check if profile and requirement exist
        profile_exist = Profile.objects.filter(pk=pro).exists()
        if profile_exist:
            print("profile exists")
            profile = Profile.objects.get(pk=pro)
            print(f"profile is {profile}")

        requirement_exist = Requirement.objects.filter(pk=requirement).exists()
        if requirement_exist:
            print("requirement exists")
            requirement = Requirement.objects.get(pk=requirement)
            print(f"requirement is {requirement}")

        # get profile and requirement objects
        if profile_exist and requirement_exist:
            no_record = False
        else:
            no_record = True

        # check if requirement already exists
        exist = Complete.objects.filter(
            user=profile.id, requirement=requirement.id, stage=1
        ).exists()

        # check applied count is less than two
        today = datetime.date.today()
        greater = False

        today_count = Complete.objects.filter(
            user=profile, stage=1, applied=today
        ).count()

        if today_count > 2:
            greater = True
            print("applied count more than two")
            context = {"result": "applied count is more than 2"}

        # if requirement does not exist, add requirement to complete
        if (not exist) and (not greater) and (not no_record):
            complete = Complete(user=profile, requirement=requirement, stage=1)
            complete.save()
            print(f"requirement added id :{complete.id}")
            context = {"result": "success"}
        else:
            print(f"requirement already applied!")
            context = {"result": "exist"}

        return HttpResponse(JsonResponse(context))

    return HttpResponse(JsonResponse(context))


""" projects """


@login_required()
def view_projects(request):
    context = {"title": "projects"}
    return render(request, "member/projects", context)


""" get projects for specific user """


@login_required()
def projects(request, user_id):
    select_project = MemberProjectForm()
    user = User.objects.get(id=user_id)
    profile, _ = Profile.objects.get_or_create(user=user)
    projects = profile.projects.all()

    context = {
        "title": "projects",
        "projects": projects,
        "user_project": projects,
        "profile": profile,
        "select_project": select_project,
    }
    return render(request, "member/projects", context)


""" add project to profile """


@login_required()
def add_project(request):
    context = {"result": "not loaded"}
    if request.method == "POST":
        profile = int(request.POST.get("pro"))
        project = int(request.POST.get("project"))
        profile = Profile.objects.get(id=profile)
        project = Project.objects.get(id=project)

        if project:
            if profile.projects.filter(id=project.id).exists():
                print("project already exists")
            else:
                profile.projects.add(project)
                profile.save()
                print("project added")
        else:
            print("project does not exist")

        context = {"result": "success"}

    return HttpResponse(JsonResponse(context))


""" camps """


@login_required()
def view_camps(request):
    context = {"title": "camps"}
    return render(request, "member/camps", context)


""" get camps for specific user """


@login_required()
def camps(request, user_id):
    select_camp = MemberCampForm()
    user = User.objects.get(id=user_id)
    profile, _ = Profile.objects.get_or_create(user=user)
    camps = profile.camps.all()
    print(camps.values_list())
    context = {
        "title": "camps",
        "select_camp": select_camp,
        "user_camps": camps,
        "profile": profile,
    }
    return render(request, "member/camps", context)


""" add Camp to profile  not done"""


@login_required()
def add_camp(request):
    context = {"result": "not loaded"}
    if request.method == "POST":
        pro = int(request.POST.get("pro"))
        camp = request.POST.get("camp")
        profile = Profile.objects.get(id=pro)
        camp = Camp.objects.get(id=camp)
        if camp:
            if profile.camps.filter(id=camp.id).exists():
                print("camp already exists")
            else:
                profile.camps.add(camp)
                print("camp added")
            profile.save()
        else:
            print("camp does not exist")
        context = {"result": "success"}

    return HttpResponse(JsonResponse(context))


""" announce """


@login_required()
def view_announce(request):
    context = {"title": "messages"}

    # announcements = Announcement.objects.all()

    return render(request, "member/messages", context)
