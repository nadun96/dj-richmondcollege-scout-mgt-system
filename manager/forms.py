from bootstrap_datepicker_plus.widgets import DatePickerInput
from member.models import Camp, Project, Hike, Badge, Requirement
from core.models import Profile, MembershipFee, MemberRole, Leader
from bootstrap_datepicker_plus.widgets import YearPickerInput
from .models import Photo, Post, Announcement, Patrol  # MembershipFee
from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()

""" Requirements form """


class RequirementForm(forms.ModelForm):

    badge = forms.ModelChoiceField(queryset=Badge.objects.all(),
                                   widget=forms.Select(
        attrs={'class': 'form-control selectize', 'placeholder': 'Select the badge'}))

    description = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 3, 'class': 'py-2'}))

    class Meta:
        model = Requirement
        fields = "__all__"


""" Badge form """


class BadgeForm(forms.ModelForm):

    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Badge
        fields = "__all__"


""" hike form """


class HikeForm(forms.ModelForm):
    class Meta:
        model = Hike

        fields = ['title', 'description', 'year', 'date',
                  'time', 'nights', 'is_day', 'location']

        widgets = {

            'year': YearPickerInput(),
            'date': forms.DateInput(format='%Y/%m/%d', attrs={'type': 'date'}),
            'time': forms.TimeInput(format='%H', attrs={'type': 'time'}),

        }


""" project form """


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'date', 'time', 'location']

        widgets = {
            'date': forms.DateInput(format='%Y/%m/%d', attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(format='%H', attrs={'type': 'time', 'class': 'form-control'}),
        }


""" camp form """


class CampForm(forms.ModelForm):
    class Meta:
        model = Camp
        fields = ['title', 'description', 'date', 'time', 'nights',
                  'is_day', 'is_overseas', 'country', 'location']
        widgets = {
            'date': forms.DateInput(format='%Y/%m/%d', attrs={'type': 'date'}),
            'time': forms.TimeInput(format='%H', attrs={'type': 'time'}),
        }


""" upload Photo form  """


class UploadPhotoForm(forms.ModelForm):

    class Meta:
        model = Photo
        fields = ['title', 'description', 'date', 'location', 'file',]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'date': forms.DateInput(
                format='%Y/%m/%d', attrs={'type': 'date'})
        }


""" upload posts form """


class UploadPostsForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'description', 'file', 'picture']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 10}),
            'file': forms.FileInput(attrs={'class': 'form-control-file', 'Multiple': True}),
        }


""" Announce form """


class AnnounceForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }


""" Add Assign Members to Patrol form """


class AssignPatrolForm(forms.Form):
    member = forms.ModelChoiceField(queryset=Profile.objects.all(),
                                    widget=forms.Select(
                                        attrs={'class': 'form-control selectize', 'placeholder': 'select member'}))
    patrol = forms.ModelChoiceField(queryset=Patrol.objects.all(),
                                    widget=forms.Select(
                                        attrs={'id': 'assign_patrol', 'class': 'form-control selectize', 'placeholder': 'select patrol'}))


""" Member Activation / Deactivate form """


class ActivateMemberForm(forms.Form):
    member = forms.ModelChoiceField(queryset=User.objects.all(),
                                    widget=forms.Select(
                                        attrs={'class': 'form-control selectize ', 'placeholder': 'select member'})
                                    )

    active = forms.BooleanField(required=False, widget=forms.CheckboxInput(
        attrs={'id': 'a_m_member', 'data-toggle': 'toggle', 'data-style': 'ios'}))


""" Member Membership Fee form """


class MembershipFeeForm(forms.ModelForm):
    class Meta:
        model = MembershipFee
        fields = '__all__'
        widgets = {
            'member': forms.Select(
                attrs={'id': 'a_f_member', 'class': 'form-control  selectize ', 'placeholder': 'select member'}),
            'for_year': YearPickerInput(),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Rs.100'}),
        }
        initial = {'member': ''}


""" Assign Role form """


ROLES = {
    (2, 'Member'),
    (3, 'Secretary'),
    (4, 'Storekeeper'),
}


class AssignRoleForm(forms.Form):
    role = forms.ChoiceField(choices=ROLES, widget=forms.Select(
        attrs={'id': 'rf_select_role', 'class': 'form-control selectize '}))
    profile = forms.ModelChoiceField(queryset=Profile.objects.all(), widget=forms.Select(
        attrs={'id': 'rf_select_profile', 'class': 'form-control selectize ', 'placeholder': 'select profile'}))


""" Assign Leader form  """


class AssignLeaderForm(forms.ModelForm):
    class Meta:
        model = Leader
        fields = ['name', 'patrol']
        widgets = {

            'name': forms.Select(attrs={'class': 'form-control selectize', 'placeholder': 'select member'}),

            'patrol': forms.Select(attrs={'class': 'form-control selectize', 'placeholder': 'select patrol'}),

        }

        initial = {'name': '', 'patrol': ''}


""" Patrol forms """


class AddPatrolForm(forms.ModelForm):
    class Meta:
        model = Patrol
        fields = ['name']


class EndPatrolForm(forms.Form):
    patrol = forms.ModelChoiceField(queryset=Patrol.objects.all(),
                                    widget=forms.Select(
                                        attrs={'class': 'form-control selectize ', 'id': 'end-form-select-patrol', 'placeholder': 'select patrol'}))
