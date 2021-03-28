import datetime
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import User, Item, Watchlist, Bid, Comment

class NewBid(forms.Form):
    productid = forms.IntegerField(widget=forms.HiddenInput())
    bidprop = forms.DecimalField(decimal_places=2)

def index(request):

    # Return all active items
    return render(request, "auctions/index.html", {
        "items": Item.objects.filter(active=True)
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

@login_required
def additem(request):

    # Predefined list of categories
    CATEGORIES = [
        "Shirts",
        "Pants",
        "Shoes",
        "Socks",
        "Jackets"
    ]
    name = request.POST.get("name")
    description = request.POST.get("description")
    category= request.POST.get("category")
    startingbid = request.POST.get("startingbid")
    image = request.POST.get("url")
    submit = request.POST.get("submit")

    create_listing = Item(name=name, description=description, startingbid=startingbid, 
    category=category, image=image, author=request.user.id)

    # Check for valid input
    if submit and Item != None:
        create_listing.save()
        messages.success(request, 'You have created new listing.')      

    return render(request, "auctions/additem.html", {
        "categories": CATEGORIES
    })

def listing(request, item): 

    # Get access to item viewed currently
    itemdetails = Item.objects.get(id=item)
    itemId = itemdetails.id 
    name = itemdetails.name
    description = itemdetails.description
    image = itemdetails.image
    startingbid = itemdetails.startingbid
    category = itemdetails.category
    listingactive = itemdetails.active
    winnername = " "
    visitoriswinner = False
    comments = Comment.objects.filter(item_id=item) 
  
    try:
        # Check if Watchlist is populated
        if Watchlist.objects.get(item_id=itemId, user_id=request.user.id):
            itemOnList = True
        
    except:
            
        itemOnList = False
     
    try:
        # Get last bid
        currentbid = Bid.objects.filter(item_id=item).last().bid

    except:
        # If no bids yet, set default bid value
        currentbid = startingbid
    
    try:
        # Check if current user is author of listing
        if Item.objects.get(id=itemId, author=request.user.id):
            author = True

    except:

        author = False

    try:

        # Check if current user is winner of this auction
        winnerbid = Bid.objects.filter(item_id=itemId).last()   
        winner = User.objects.get(id=winnerbid.user_id)
        winnername = winner.username
        if winner.id == request.user.id:
            visitoriswinner = True

    except:
        
        pass
    
    return render(request, "auctions/listing.html", {
        "name": name,
        "description": description,
        "image": image,
        "startingbid": startingbid,
        "category": category,  
        "itemId": itemId,
        "itemOnList": itemOnList,
        "NewBid": NewBid(initial = {'bidprop': currentbid, 'productid': itemId}),
        "currentbid": currentbid,
        "author": author,       
        "listingactive": listingactive,
        "winnername": winnername,
        "visitoriswinner": visitoriswinner,
        "comments": comments
    })

@login_required
def addtowatch(request, itemId):
 
    try:
        # If already on watchlist - delete
        if Watchlist.objects.get(item_id = itemId, user_id = request.user.id): 
            Watchlist.objects.filter(item_id = itemId, user_id = request.user.id).delete()

    except:
        # If not on watchlist - save
        Watchlist(item_id = itemId, user_id = request.user.id).save()

    return HttpResponse(status=204)

@login_required
def watchlist(request):
    
    # Get Watchlist objects according to current user id
    getwatchlist = Watchlist.objects.filter(user_id = request.user.id)

    # Declaration of list of watchlistitems
    watchlistitems = []

    # Handle empty watchlist
    if len(getwatchlist) == 0:
        return render(request, 'auctions/error.html', {
                "msg": "No items on watchlist. Add items to watchlist to see them here."
            })
    else:
        # Populate watchlistitems[]
        for i in range(len(getwatchlist)):
            watchlistitems.append(Item.objects.get(id = getwatchlist[i].item_id))
    
    return render(request, "auctions/watchlist.html", {
        "watchlistitems": watchlistitems
    })

@login_required
def bid(request):
    nobids = False
       
    if request.method == "POST":

        newbid = NewBid(request.POST)
       
        if newbid.is_valid():

            productid = newbid.cleaned_data["productid"]
            bidprop = newbid.cleaned_data["bidprop"]
            
            try:
                # Extract current bid
                currentbid = Bid.objects.filter(item_id=productid).last().bid

            except: 
                # If no bids yet, currentbid = startingbid
                nobids = True
                currentbid = Item.objects.get(id=productid).startingbid
               
            
            if nobids:
                # If no bids for item, let user bid if his bid => startingbid
                if float(bidprop) < float(currentbid):
                    messages.error(request, 'Bid is too small. Try again!')                   
                    return redirect('/listing/'+str(productid))

                else:
                    # Save user bid
                    Bid(item_id=productid, user_id=request.user.id, bid=bidprop).save()
                    currentbid = Bid.objects.filter(item_id=productid).last().bid
                    update = Item.objects.get(id=productid)
                    update.startingbid = currentbid
                    update.save(update_fields=['startingbid'])
                    messages.success(request, 'Congratulations! You are first bidder!')                   
                    return redirect('/listing/'+str(productid))

            # If bids exist, let user bid only if his bid > currentbid
            else:         

                if float(bidprop) <= float(currentbid):
                    messages.error(request, 'Bid is too small. Try again!')                   
                    return redirect('/listing/'+str(productid))

                else:
                    # Save user bid and extract most recent bid
                    Bid(item_id=productid, user_id=request.user.id, bid=bidprop).save()
                    currentbid = Bid.objects.filter(item_id=productid).last().bid  
                               
                    update = Item.objects.get(id=productid)
                    update.startingbid = currentbid
                    update.save(update_fields=['startingbid'])
                    messages.success(request, 'Congratulations! Your bid has been accepted.')                   
                    return redirect('/listing/'+str(productid))
                        
        else:
            # Handle invalid form error     
            return render(request, 'auctions/error.html', {
                "msg": 'Something went wrong. Click here to go back.'
            })
    
    else:
        return redirect('/listing/'+str(productid))

@login_required
def close(request, itemId):
    
    # Get author of the listing
    findauthor = Item.objects.get(id = itemId)
    author = findauthor.author

    # Verify if visitor is author
    if author != request.user.id:
        author = False

    else:
        author = True
    
    # Let author close listing (HTML button visible only if author = True)
    if request.method == "GET":

        update = Item.objects.get(id = itemId)
        update.active = False
        update.save(update_fields=["active"])

        # Remove from Watchlist while listing closed
        Watchlist.objects.filter(item_id=itemId).delete()

        try:
            
            # Save winner of auctions
            highestbid = Bid.objects.filter(item_id=itemId).last()
            highestbid.winner = True
            highestbid.save(update_fields=["winner"])
            
        
        except:
            
            # If no bidders close with proper information
            messages.success(request, 'Listing closed without bids.')   
            return redirect('/')
    
    messages.success(request, 'Listing closed.')
    return redirect('/')
    
def closed(request):

    # Display not active listings
    return render(request, "auctions/closed.html", {
        "items": Item.objects.filter(active=False)
    })

def comments(request, itemId):
    
    if request.method == "GET":
        # Collect user comment and save it
        content = request.GET.get('comment')
        Comment(item_id=itemId, user_id=request.user, content=content).save()
        messages.success(request, 'Your comment has been added.')

    return redirect('/listing/'+str(itemId))

def categories(request):
     
    if request.method == "POST":
        # Collect category choosen by user and display all items from this category
        category = request.POST.get("category")
        return render(request, "auctions/index.html", {
            "items": Item.objects.filter(category=category, active=True)
        })

    return render(request, "auctions/categories.html")
