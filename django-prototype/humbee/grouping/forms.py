from django import forms
from django.utils.safestring import mark_safe
import os

with open(os.path.join(os.path.dirname(__file__), "../etc/default.txt"), "r") as f:
	default_text = f.read()

class GroupingForm(forms.Form):
	problem = forms.CharField(label = 'Grouping problem',
	                          widget = forms.Textarea(attrs={'rows': 40, 'cols': 120}),
	                          initial = default_text)


