from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"placeholder": "Your name", "class": "form-control"}
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": "you@example.com", "class": "form-control"}
        )
    )
    subject = forms.CharField(
        max_length=200, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
        min_length=10,
        max_length=1000,
    )
    priority = forms.ChoiceField(
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and "@spam.com" in email:
            raise forms.ValidationError("Spam email addresses are not allowed.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get("subject")
        message = cleaned_data.get("message")
        if subject and message and len(message) < len(subject):
            raise forms.ValidationError("Message should be longer than the subject!")
        return cleaned_data


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "status", "categories"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Post title..."}
            ),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "categories": forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            "status": "Draft = only you can see it. Published = everyone can see it.",
        }


class CustomRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        help_text="Tell us a little about yourself (optional)",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        """
        Override save() to also save the email field
        (UserCreationForm doesn't save email by default)
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            from .models import UserProfile

            UserProfile.objects.create(user=user, bio=self.cleaned_data.get("bio", ""))
        return user


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Write a comment...",
                }
            )
        }
        labels = {"body": "Your Comment"}
