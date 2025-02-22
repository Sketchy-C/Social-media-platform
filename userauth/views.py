from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, logout, authenticate
from .models import Profile, Post, LikePost, Followers,Comment
from django.db import IntegrityError
from django.db.models import Q
from .forms import CommentForm


def login(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        password = request.POST.get('password')
        user = authenticate(request,username=fname,password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('/')
        
        invalid = 'Invalid Credentials'
        return render(request,'login.html',{'invalid':invalid})
    
    return render(request,'login.html')

def signup(request):
    try:
        if request.method == 'POST':
            fname = request.POST.get('fname')
            emailid = request.POST.get('emailid')
            password = request.POST.get('password')

            my_user = User.objects.create_user(username=fname,email=emailid, password=password)
            my_user.save()

            user_model = User.objects.get(username=fname)
            new_profile = Profile.objects.create(user=user_model,id_user=user_model.id)
            new_profile.save()

            login(request,my_user)
            return redirect('/')
       
    except IntegrityError:
        invalid = 'User Already Exists \n You will only need to login to the account'
        return render(request, 'signup.html', {'invalid': invalid})
    except Exception as e:
        invalid = str(e)
        invalid = 'Account created succesfully'
        render(request, 'signup.html', {'invalid': invalid})
        return redirect('/login')

    return render(request, 'signup.html')

def logoutt(request):
    logout(request)
    return redirect('/login')


def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image=request.FILES.get('image-upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')
    

def home(request):
    post = Post.objects.all().order_by('create_at').reverse()
    profile = Profile.objects.get(user=request.user)
    context = {
        'post':post,
        'profile':profile
    }
    return render(request, 'main.html',context)

def likes(request, id):
    if request.method == 'GET':
        username = request.user.username
        post = get_object_or_404(Post,id=id)
        like_filter = LikePost.objects.filter(post_id = id, username=username).first()
        
        if like_filter is None:
            LikePost.objects.create(post_id = id,username=username)
            post.no_of_likes = post.no_of_likes + 1
            return redirect('/')
        else:
            like_filter.delete()
            post.no_of_likes = post.no_of_likes - 1

        post.save() 

        return redirect(f'/#{id}')

def home_posts(request,id):
    post = Post.objects.get(id=id)
    profile = Profile.objects.get(user=request.user)
    context = {
        'post':post,
        'profile':profile
    }
    return render(request, 'main.html',context)


def explore(request, id):
    post = Post.objects.get(id=id)
    profile = Profile.objects.get(user=request.user)
    context = {
        'post':post,
        'profile':profile
    }
    return render(request, 'explore.html',context)
    

def profile(request, id_user):
    user_object = User.objects.get(username=id_user)
    profile = Profile.objects.get(user=request.user)
    user_profile = Profile.objects.get(user=user_object)
    user_posts= Post.objects.filter(user=id_user).order_by('create_at')
    user_post_length = len(user_posts)

    follower = request.user.username
    user = id_user

    if Followers.objects.filter(follower=follower, user=user).first():
        follow_unfollow = 'Unfollow'
    else:
        follow_unfollow = 'Follow'

    user_followers = len(Followers.objects.filter(user = id_user))
    user_following = len(Followers.objects.filter(follower=id_user))

    context = {
        'user_object': user_object,
        'profile':profile,
        "user_profile":user_profile,
        "user_posts":user_posts,
        "user_post_length":user_post_length,
        'follow_unfollow':follow_unfollow,
        "user_followers":user_followers,
        "user_following":user_following
    }

    
    if request.user.username == id_user:
        if request.method == 'POST':
            if request.FILES.get('image') == None:
             image = user_profile.profileimg
             bio = request.POST['bio']
             location = request.POST['location']

             user_profile.profileimg = image
             user_profile.bio = bio
             user_profile.location = location
             user_profile.save()
            if request.FILES.get('image') != None:
             image = request.FILES.get('image')
             bio = request.POST['bio']
             location = request.POST['location']

             user_profile.profileimg = image
             user_profile.bio = bio
             user_profile.location = location
             user_profile.save()
            

            return redirect('/profile/'+id_user)
        else:
            return render(request, 'profile.html', context)
    return render(request, 'profile.html', context)


def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if Followers.objects.filter(follower=follower, user=user).first():
            delete_follower = Followers.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = Followers.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('/')


def delete(request, id):
    post = Post.objects.get(id=id)
    post.delete()

    return redirect('/profile/'+request.user.username)

def search_results(request):
    query = request.GET.get('q')

    users = Profile.objects.filter(user__username__icontains=query)
    posts = Post.objects.filter(caption__icontains=query)

    context = {
        'query': query,
        'users': users,
        'posts': posts,
    }
    return render(request, 'search_user.html', context)

def comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    # postobj = Post.objects.get(id=id)
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            new_comment.save()
            return redirect(f'/comment/{post.id}')

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'profile':profile,
    }

    return render(request, 'post_detail.html', context)
