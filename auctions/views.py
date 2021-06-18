from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment, Category



def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(is_open=True)
    })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))



def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# my code starts here
# TODO should probably be django forms to validate data types and lengths...


@login_required
def new(request):
    message = None
    if request.method == "POST":

        # required:
        item = request.POST["item"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        # optional:
        image_URL = request.POST["image_URL"] # check if valid url?
        if request.POST["category"]:
            category = Category.objects.get(id=request.POST["category"])
        else:
            category = None

        # verification:
        if not item:
            message = "Item Name must not be blank."
        elif not description:
            message = "Item Description must not be blank."
        elif not starting_bid or float(starting_bid) <= 0:
            message = "Starting Bid must be above zero."

        # once verified:
        if message is None:
            new_listing = Listing(item=item, description=description, starting_bid=starting_bid, image_URL=image_URL, seller=request.user, category=category)
            new_listing.save()
            message = "Listing posted successfully!"

    return render(request, "auctions/new.html", {
        "categories": Category.objects.all().order_by('name'),
        "message": message
    })



def listing(request, id):
    message = None
    listing = Listing.objects.get(id=id)

    if listing.highest_bid:
        allowed_bid = (float(listing.highest_bid.bid)*100+1)/100

    else:
        allowed_bid = listing.starting_bid

    if request.method == "POST":
        # post comment
        if request.POST["action"] == "Post Comment":
            comment = request.POST["comment"]
            new_comment = Comment(comment=comment, listing=listing, commenter=request.user)
            new_comment.save()
            message = "Comment posted successfully."

        # place bid
        elif request.POST["action"] == "Place Bid":
            bid = float(request.POST["bid"])

            if bid < allowed_bid:
                message = "Invalid bid."
            else:
                new_bid = Bid(bid=bid, listing=listing, bidder=request.user)
                new_bid.save()
                listing.highest_bid = new_bid
                listing.save()
                message = "Bid posted successfully."

        # close listing
        elif request.POST["action"] == "Close Listing":
            listing.is_open = False
            listing.save()
            message = "Listing closed."
        
        # add from watchlist
        elif request.POST["action"] == "Add to Watchlist":
            user = request.user
            user.watchlist.add(listing)
            user.save()
            message = "Added to Watchlist."

        # remove from watchlist
        elif request.POST["action"] == "Remove from Watchlist":
            user = request.user
            user.watchlist.remove(listing)
            user.save()
            message = "Removed from to Watchlist."

    # highest_bid = Bid.objects.filter(listing=listing).order_by('-bid').first() # is set to None if there are no bids yet

    # check if user is the winner
    if listing.highest_bid:
        is_winner = request.user == listing.highest_bid.bidder
    else:
        is_winner = False

    # check if in watchlist:
    if request.user.is_authenticated:
        in_watchlist = listing in request.user.watchlist.all()
    else:
        in_watchlist = False

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid_count": listing.bids.count(),
        "comments": listing.comments.order_by('-id'),
        "is_owner": request.user == listing.seller,
        "is_winner": is_winner,
        "in_watchlist": in_watchlist,
        "allowed_bid": allowed_bid,
        "message": message
    })


@login_required
def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "watchlist": request.user.watchlist.all()
    })


def category(request):
    return render(request, "auctions/category.html", {
        "categories": Category.objects.all()
    })


def filtered(request, my_id):
    if int(my_id) == 0:
        category_name = "Uncategorized"
        listings = Listing.objects.filter(category=None)
    else:
        category = Category.objects.get(id=my_id)
        category_name = category.name
        listings = Listing.objects.filter(category=category)

    return render(request, "auctions/filtered.html", {
        "category_name": category_name,
        "listings": listings
    })