from django.shortcuts import render
# custom_code.py
from django.contrib.sessions.models import Session
from django.shortcuts import render
from .models import Leader, MemberRole, User, Profile


def session_processor(request):
    # get the user id from the session
    user_id = request.session.get('_auth_user_id')
    #print(f'User id is -- {user_id}')

    try:
        user = User.objects.get(id=user_id)
        troop_leader = user.is_ldr
        if (troop_leader):
            request.session['is_troopleader'] = True
        print(troop_leader)
    except Exception as e:
        print(e)

    # get the profile id
    profile = Profile.objects.get(user=user_id)
    #print(f'User id is -- {profile}')

    #request.session['s_profile'] = profile
    request.session['s_profile_id'] = profile.id
    request.session['s_patrol_id'] = profile.patrol.id

    # use the profile id to get the leader object
    is_leader = Leader.objects.filter(
        name=profile.id).exists()
    if (is_leader):
        request.session['is_leader'] = True

    # use the profile object to get the member role object
    profile_roles_exist = MemberRole.objects.filter(
        profile_id=profile.id, active=True).exists()

    print('This is working!')

    if (profile_roles_exist):
        profile_roles = MemberRole.objects.filter(
            profile_id=profile.id, active=True)

        is_storekeeper = profile_roles.filter(role=4).exists()
        if (is_storekeeper):
            request.session['is_storekeeper'] = True

        is_secretary = profile_roles.filter(role=3).exists()
        if (is_secretary):
            request.session['is_secretary'] = True

        is_member = profile_roles.filter(role=2).exists()
        if (is_member):
            request.session['is_member'] = True

        is_admin = profile_roles.filter(role=1).exists()
        if (is_admin):
            request.session['is_admin'] = True

        print('Roles Processed!')

        request.session['profile_roles_exist'] = True

    return 'Session processed!'


# def another_view_function(request):
#     # Retrieve the variable from the session
#     my_variable = request.session.get('my_variable')
#     # Do something with the variable...
#     return render(request, 'another_template.html')
