from django import forms

from .models import Chai


class ChaiVarityForm(forms.ModelForm):
    chai_varity = forms.ModelChoiceField(
        queryset=Chai.objects.all(),label="Select Chai Varity", empty_label="Choose...")