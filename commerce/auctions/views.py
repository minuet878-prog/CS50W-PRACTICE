from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Category, Bid, Comment
from decimal import Decimal

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(is_active=True)
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
    
def create(request):
    if request.method == "GET":
        return render(request, "auctions/create.html", {
            "categories": Category.objects.all()
        })
    if request.method == "POST":
        item = request.POST.get("item")
        start_price = request.POST.get("start_price")
        img = request.POST.get("image")
        description = request.POST.get("description")
        seller = request.user
        category = Category.objects.get(id=request.POST.get("category"))
        Listing.objects.create(item=item, start_price=start_price, image=img, description=description, seller=seller, category=category)
        return HttpResponseRedirect(reverse("index"))
    
def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    highest_bid = listing.bid_items.order_by("-bid_price").first()
    bid_count = listing.bid_items.count()
    is_winner = highest_bid and highest_bid.bidder == request.user
    is_closed = not listing.is_active
    has_won = is_closed and highest_bid and highest_bid.bidder == request.user
    if highest_bid:
        current_price = highest_bid.bid_price
    else:
        current_price = listing.start_price
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "current_price": current_price,
        "bid_count": bid_count,
        "is_winner": is_winner,
        "comments": listing.comment_items.all(),
        "is_closed": is_closed,
        "has_won": has_won
    })

def bid(request, listing_id):
    if request.method == "POST":
        bid_price = request.POST.get("bid_price")
        listing = Listing.objects.get(pk=listing_id)
        highest_bid = listing.bid_items.order_by("-bid_price").first()
        bid_count = listing.bid_items.count()
        is_winner = highest_bid and highest_bid.bidder == request.user
        request.user.watchlist.add(listing)
        if highest_bid:
            current_price = highest_bid.bid_price
        else:
            current_price = listing.start_price
        if request.user == listing.seller:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "current_price": current_price,
                "error": "You cannot bid on your own listing."
            })
        if Decimal(bid_price) > current_price:
            Bid.objects.create(bid_price=bid_price, bidder=request.user, bid_item=listing)
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))
        else:
            return render(request, "auctions/listing.html",{
                "listing": listing,
                "current_price": current_price,
                "error": "Bid must be higher than current price.",
                "bid_count": bid_count,
                "is_winner": is_winner
            })

def category(request):
    return render(request, "auctions/category.html", {
        "categories": Category.objects.all()
    })

def allocate(request, name):
    return render(request, "auctions/allocate.html",{
        "listings": Listing.objects.filter(is_active=True, category__name=name),
        "categories_name": name
    })

def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "watchlists": request.user.watchlist.all()
    })

def add(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        request.user.watchlist.add(listing)
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    
def comment(request, listing_id):
    if request.method== "POST":
        listing = Listing.objects.get(pk=listing_id)
        comment = request.POST.get("comment")
        Comment.objects.create(
            comment = comment,
            comment_item = listing,
            comment_user = request.user
        )
    return HttpResponseRedirect(reverse("listing", args=[listing_id]))

def close_auction(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        listing.is_active = False
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    
def remove(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        request.user.watchlist.remove(listing)
        return HttpResponseRedirect(reverse("listing", args=[listing_id]))
