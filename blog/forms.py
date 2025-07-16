from django import forms
from .models import Post, Category, UserProfile
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title',
                'maxlength': '200'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your post content here',
                'rows': 10
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'published': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['category'].empty_label = "Select a category"
    self.fields['categgory'].required = False
    self.fields['published'].help_text = "Check to publish this post immediately."
            
def clean_title(self):
        title = self.cleaned_data.get('title')
        
        # Check minimum length
        if len(title) < 5:
            raise ValidationError("Title must be at least 5 characters long.")
        
        # Check for inappropriate words (basic example)
        inappropriate_words = ['spam', 'fake', 'scam']
        for word in inappropriate_words:
            if word.lower() in title.lower():
                raise ValidationError(f"Title cannot contain inappropriate content: '{word}'")
        
        # Check if similar title already exists
        if self.instance.pk:
            # Editing existing post - exclude current post from check
            existing_posts = Post.objects.filter(title__iexact=title).exclude(pk=self.instance.pk)
        else:
            # Creating new post
            existing_posts = Post.objects.filter(title__iexact=title)
            
        if existing_posts.exists():
            raise ValidationError("A post with this title already exists. Please choose a different title.")
        
        return title
    
def clean_content(self):
    content = self.cleaned_data.get('content')
    
    # Check minimum length
    if len(content) < 50:
        raise ValidationError("Post content must be at least 50 characters long.")
    
    # Check maximum length
    if len(content) > 10000:
        raise ValidationError("Post content cannot exceed 10,000 characters.")
    
    return content

def clean(self):
    cleaned_data = super().clean()
    title = cleaned_data.get('title')
    content = cleaned_data.get('content')
    published = cleaned_data.get('published')
    
    # If publishing, ensure content is substantial
    if published and content and len(content) < 100:
        raise ValidationError("Published posts should have at least 100 characters of content.")
    
    return cleaned_data

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

        self.fields['username'].help_text = "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        self.fields['password1'].help_text = "Your password can't be too similar to your other personal information. It must contain at least 8 characters, and can't be a commonly used password."


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'website', 'location', 'birth_date', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        
        self.fields['old_password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Old password'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'New password'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm new password'})  

        