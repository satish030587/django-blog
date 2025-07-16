from django.shortcuts import render, redirect
from .models import Post, Category, UserProfile
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PostForm, CustomUserCreationForm, CustomPasswordChangeForm, UserUpdateForm, UserProfileForm
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, logout
from .forms import UserUpdateForm, UserProfileForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

def post_list(request):
    posts = Post.objects.filter(published=True)

    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Category filtering
    category_filter = request.GET.get('category')
    selected_category_object = None
    if category_filter:
        posts = posts.filter(category_id=category_filter)
        selected_category_object = Category.objects.filter(id=category_filter).first()
    
    posts = posts.order_by('-created_at')
    post_count = posts.count()
    
    # Get all categories for filter dropdown
    categories = Category.objects.all()
    
    context = {
        'posts': posts,
        'post_count': post_count,
        'search_query': search_query,
        'selected_category': category_filter,
        'selected_category_object': selected_category_object,
        'categories': categories,
    }

    return render(request, 'blog/post_list.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id, published=True)

    context = {
        'post': post,
    }
    return render(request, 'blog/post_detail.html', context)
# Create your views here.


@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, f'Blog post "{post.title}" created successfully!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm()

        context = {
            'form': form,
            'title': 'Create New Post'
        }
    return render(request, 'blog/add_post.html', context)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this post.')
        return redirect('post_detail', post_id=post.id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, f'Blog post "{post.title}" was updated successfully!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    context = {
        'form': form,
        'title': f'Edit Post: {post.title}',
        'post': post,
    }                             
    return render(request, 'blog/edit_post.html', context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('post_detail', post_id=post.id)

    if request.method == 'POST':
        post_title = post.title
        post.delete()
        messages.success(request, f'Blog post "{post_title}" was deleted successfully!')
        return redirect('post_list')

    context = {
        'post': post,
        'title': f'Delete Post: {post.title}'
    }
    return render(request, 'blog/delete_post.html', context)

@login_required
def my_posts(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')

    context = {
        'posts': posts,
        'post_count': posts.count(),
        'page_title': 'My Posts',
        'show_drafts': True,
    }
    return render(request, 'blog/my_posts.html', context)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You are now logged in.')
            login(request, user)  # Automatically log in the user
            return redirect('post_list')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Create Account'
    }
    return render(request, 'registration/register.html', context)


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                
                # Redirect to next page or default
                next_page = request.GET.get('next')
                return redirect(next_page) if next_page else redirect('post_list')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'title': 'Sign In'
    }
    return render(request, 'registration/login.html', context)

def user_logout(request):
    if request.method == 'POST':
        username = request.user.username
        logout(request)
        messages.success(request, f'You have been logged out successfully, {username}!')
    return redirect('post_list')


@login_required
def user_profile(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
    user_posts = Post.objects.filter(author=user, published=True).order_by('-created_at')[:5]
    
    context = {
        'profile_user': user,
        'profile': profile,
        'user_posts': user_posts,
        'post_count': user_posts.count(),
        'is_own_profile': user == request.user,
    }
    return render(request, 'blog/user_profile.html', context)

@login_required
def edit_profile(request):

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('user_profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Edit Profile'
    }
    return render(request, 'blog/edit_profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('user_profile', username=request.user.username)
    else:
        form = CustomPasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'title': 'Change Password'
    }
    return render(request, 'blog/change_password.html', context)


@login_required
def user_dashboard(request):
    user = request.user
    
    # User statistics
    total_posts = Post.objects.filter(author=user).count()
    published_posts = Post.objects.filter(author=user, published=True).count()
    draft_posts = total_posts - published_posts
    
    # Recent activity
    recent_posts = Post.objects.filter(author=user).order_by('-created_date')[:5]
    
    context = {
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'recent_posts': recent_posts,
        'title': 'Dashboard'
    }
    return render(request, 'blog/user_dashboard.html', context)


def user_directory(request):
    users = User.objects.filter(is_active=True).order_by('username')
    search_query = request.GET.get('search')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    context = {
        'users': users,
        'search_query': search_query,
        'title': 'User Directory'
    }
    return render(request, 'blog/user_directory.html', context)