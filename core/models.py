from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from member.models import Camp, Project, Hike, Requirement
from django.utils.translation import gettext as _
from manager.models import Patrol, Communication


class User(AbstractUser):
    is_active = models.BooleanField(default=True)
    is_mem = models.BooleanField(default=False)
    is_skr = models.BooleanField(default=False)
    is_sec = models.BooleanField(default=False)
    is_ldr = models.BooleanField(default=False)
    is_exa = models.BooleanField(default=False)

    def __str__(self):
        return self.username


# user profiles
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    surname = models.CharField(max_length=50, blank=True)
    initials = models.CharField(max_length=10, blank=True)
    entrance_number = models.CharField(max_length=10, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    father = models.CharField(max_length=50, blank=True)
    skills = models.CharField(max_length=50, blank=True)
    sports = models.CharField(max_length=50, blank=True)
    birthday = models.DateField(null=True, blank=True)
    contact = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    camps = models.ManyToManyField(Camp, blank=True)
    hikes = models.ManyToManyField(Hike, blank=True)
    projects = models.ManyToManyField(Project, blank=True)
    badges = models.ManyToManyField(Requirement, blank=True)
    patrol = models.ForeignKey(
        Patrol, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username


""" # group contact details """


class Group(models.Model):
    name = models.CharField(max_length=50, blank=False)
    address = models.CharField(max_length=100, null=True, blank=True)
    telephone = models.CharField(max_length=11, null=True, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    about = models.TextField(max_length=500, blank=True)
    fee = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


"""  Member roles """

ROLES = {
    (1, 'Admin'),
    (2, 'Member'),
    (3, 'Secretary'),
    (4, 'Storekeeper'),
}


class MemberRole(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    role = models.IntegerField(choices=ROLES, blank=True)
    active = models.BooleanField(default=True)
    start = models.DateField(auto_now_add=True, blank=True)
    end = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.role


"""  user files """


class UserFile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def profile_image_upload_path(instance, filename):
        return f'img/profile/{filename}'

    picture = models.ImageField(
        upload_to=profile_image_upload_path, blank=True)

    def profile_letter_upload_path(instance, filename):
        return f'files/letter/{filename}'

    letter = models.FileField(upload_to=profile_letter_upload_path, blank=True)

    def profile_medical_upload_path(instance, filename):
        return f'files/medical/{filename}'

    medical = models.FileField(
        upload_to=profile_medical_upload_path, blank=True)

    def __str__(self):
        return self.user.username


""" badge complete model """

COMPLETE_CHOICES = [(1, 'Applied'), (2, 'Pass'), (3, 'Fail')]


class Complete(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    examiner = models.ForeignKey(
        Profile, on_delete=models.CASCADE, null=True, blank=True, related_name='examiner')
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    applied = models.DateField(blank=False, auto_now_add=True)
    completed = models.DateField(blank=True, null=True)
    stage = models.IntegerField(choices=COMPLETE_CHOICES, validators=[
                                MinValueValidator(1)], blank=False)

    class Meta:
        verbose_name = _("Complete")
        verbose_name_plural = _("Completes")


""" # leaders model """


class Leader(models.Model):
    name = models.ForeignKey(Profile, on_delete=models.CASCADE)
    start = models.DateField(auto_now_add=True, blank=False)
    end = models.DateField(blank=True, null=True)
    patrol = models.ForeignKey(
        Patrol, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.patrol.name + ' | ' + self.name.user.username


"""  message model """


class Message(Communication):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='receiver')
    content = models.CharField(max_length=50, blank=False)
    date = models.DateField(blank=False)

    def __str__(self):
        return self.title


""" Membership Fee Modal """


class MembershipFee(models.Model):
    member = models.ForeignKey(
        Profile, on_delete=models.CASCADE, blank=False)
    amount = models.DecimalField(
        max_digits=5, decimal_places=2, blank=False, validators=[MinValueValidator(0)])
    for_year = models.DateField(blank=False)
    date = models.DateField(auto_now_add=True, blank=False)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.member)
