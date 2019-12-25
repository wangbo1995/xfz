from django import forms
from apps.form import FormMixin

class PublicCommentForm(forms.Form, FormMixin):
    content = forms.CharField()
    news_id = forms.IntegerField()
