# forms.py
from django import forms


class CourseSearchForm(forms.Form):
    cluster_points = forms.FloatField(required=False, label="Cluster Points")
    field_of_study = forms.CharField(required=False, label="Field of Study", max_length=100)
    institution_name = forms.CharField(required=False, label="Institution Name", max_length=100)
