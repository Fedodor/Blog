from django import forms

from .models import Comment, Post, User


class CommentEditForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class PostEditForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%d %H:%M',
            ),
        }


class UserEditForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
