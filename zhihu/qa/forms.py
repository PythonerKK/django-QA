from django import forms

from zhihu.qa.models import Question

from markdownx.fields import MarkdownxFormField


class QuestionForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())
    content = MarkdownxFormField()

    class Meta:
        model = Question
        fields = ['title', 'content', 'tags', 'status']

