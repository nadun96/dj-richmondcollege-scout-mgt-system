from django import forms
from core.models import Profile, UserFile
from .models import Hike, Project, Camp, Requirement

""" profile tab forms """


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user', 'email', 'skills', 'sports',
                  'birthday', 'contact', 'address']


class FilesUpdateForm(forms.ModelForm):
    class Meta:
        model = UserFile
        fields = ['user', 'picture', 'medical']


""" hike tab forms """


class MemberHikeForm(forms.Form):
    hike = forms.ModelChoiceField(queryset=Hike.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-control selectize pt-2 col-lg-10 col-md-10 col-sm-12', 'id': 'hike_field', 'placeholder': 'Select a hike...'}))


""" camp tab forms """


class MemberCampForm(forms.Form):
    camp = forms.ModelChoiceField(queryset=Camp.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-control selectize  pt-2 col-lg-10 col-md-10 col-sm-12', 'id': 'camp_field', 'placeholder': 'Select a camp...'}))


""" project tab forms """


class MemberProjectForm(forms.Form):
    project = forms.ModelChoiceField(queryset=Project.objects.all(
    ), widget=forms.Select(attrs={'class': 'form-control selectize pt-2 col-lg-10 col-md-10 col-sm-12', 'id': 'project_field',  'placeholder': 'Select a project...'}))


""" badges tab forms """


class MemberRequirementForm(forms.Form):
    requirement = forms.ModelChoiceField(queryset=Requirement.objects.all().order_by('badge__level', 'number'), widget=forms.Select(
        attrs={'class': 'form-control selectize pt-2  col-lg-10 col-md-10 col-sm-12', 'id': 'requirement_field', 'placeholder': 'Select your requirement...'}))
