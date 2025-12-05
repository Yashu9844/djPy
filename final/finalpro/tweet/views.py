from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from .forms import TweetForm, UserRegistrationForm
from .models import Tweet

from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
def index(request):
    """Render the home page."""
    return render(request, "index.html")

@login_required
def create_tweet(request):
    """Create a new tweet."""
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect("tweet_list")
    else:
        form = TweetForm()

    return render(request, "create_tweet.html", {"form": form})


def tweet_list(request):
    """List all tweets."""
    tweets = Tweet.objects.all().order_by("-created_at")
    return render(request, "tweet_list.html", {"tweets": tweets})

@login_required
def tweet_edit(request, pk):
    """Edit an existing tweet."""
    tweet = get_object_or_404(Tweet, pk=pk)

    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            form.save()
            return redirect("tweet_list")
    else:
        form = TweetForm(instance=tweet)

    return render(request, "tweet_edit.html", {"form": form})

@login_required
def tweet_delete(request, pk):
    """Delete an existing tweet."""
    tweet = get_object_or_404(Tweet, pk=pk)
    if request.method == "POST":
        tweet.delete()
        return redirect("tweet_list")

    return render(request, "tweet_delete.html", {"tweet": tweet})



def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.save()
            login(request, user)
            return redirect("tweet_list")
    else:
        form = UserRegistrationForm()
    return render(request, "registration/register.html", {"form": form})