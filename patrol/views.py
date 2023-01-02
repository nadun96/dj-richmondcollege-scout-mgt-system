from django.http import HttpResponse
from django.shortcuts import redirect, render
from core.models import Complete, Profile, UserFile
from .forms import ResultForm
from .cryptography import encrypt_value, decrypt_value
from django.http import JsonResponse
import datetime
# Create your views here.

""" pass fail or apply for badge """


def evaluate(request):
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


""" load examine form in a new tab after clicking on table link"""


def examine_form(request, pk):
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


""" view tab badges """


def view_examine(request, user_id):
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
