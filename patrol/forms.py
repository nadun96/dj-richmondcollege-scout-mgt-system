from django import forms
from core.models import Complete, Profile, UserFile
from .models import Attendance


""" profile tab forms """


class ReadOnlyWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        attrs = {'class': 'form-select', 'readonly': True}
        value = Profile.objects.get(user=value)
        return value, attrs


class ResultForm(forms.ModelForm):

    class Meta:
        model = Complete
        fields = ['user', 'requirement', 'stage', 'examiner']

        widgets = {
            'user': forms.Select(attrs={'class': 'form-control  col-lg-12 col-sm-12', 'readonly': True, 'disabled': True}),
            'examiner': forms.Select(attrs={'class': 'form-control  col-lg-12 col-sm-12', 'readonly': True, 'disabled': True}),
            'requirement': forms.Select(attrs={'class': 'form-control  col-lg-12 col-sm-12', 'readonly': True, 'disabled': True}),
            'stage': forms.Select(attrs={'class': 'form-control selectize col-lg-12 col-sm-12', 'style': 'width: 100%'}),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['title', 'marker', 'member']
        widgets = {
            'marker': forms.Select(attrs={'id': 'id_marker', 'class': 'form-control selectize col-lg-12 col-sm-12', 'disabled': True}),
            'member': forms.Select(attrs={'id': 'id_member', 'class': 'form-control selectize col-lg-12 col-sm-12', 'placeholder': 'Select a member'}),
        }


class SelectMember(forms.Form):
    member = forms.ModelChoiceField(queryset=Profile.objects.all(), widget=forms.Select(attrs={'class': 'form-control selectize col-lg-12 col-sm-12', 'placeholder': 'Select a member'}))