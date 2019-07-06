from django import forms

from markdownx.fields import MarkdownxFormField

from zhihu.articles.models import Article


class ArticleForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput())
    edited = forms.BooleanField(widget=forms.HiddenInput(),
                                initial=False, required=False)
    content = MarkdownxFormField()

    class Meta:
        fields = ['title', 'content', 'image', 'tags']
        model = Article
