from django.forms import ModelForm

from .models import Goal, Checkin


class GoalForm(ModelForm):
    class Meta:
        model = Goal
        fields = ['name', 'description']


class CheckinForm(ModelForm):
    class Meta:
        model = Checkin
        fields = ['goal', 'message']
