from django import forms

from .models import Comment, Post, User


class CommentEditForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea({'rows': '3'})
        }


class PostEditForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', 'created_at')
        widgets = {
            'text': forms.Textarea({'rows': '5'}),
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
