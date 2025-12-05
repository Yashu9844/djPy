from django.shortcuts import get_object_or_404, redirect, render

from .forms import TweetForm
from .models import Tweet


def index(request):
    """Render the home page."""
    return render(request, "index.html")


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


def tweet_delete(request, pk):
    """Delete an existing tweet."""
    tweet = get_object_or_404(Tweet, pk=pk)
    if request.method == "POST":
        tweet.delete()
        return redirect("tweet_list")

    return render(request, "tweet_delete.html", {"tweet": tweet})
