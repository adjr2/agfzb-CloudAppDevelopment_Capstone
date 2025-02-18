from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel, DealerReview
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request, get_dealer_by_id_from_cf, analyze_review_sentiments
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    print("Log out the user `{}`".format(request.user.username))
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("/djangoapp/")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://dhirajupadhy-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealerships = get_dealers_from_cf(url)
        context["dealerships"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        
        # Retrieve dealer details
        dealer_url = "https://dhirajupadhy-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id=dealer_id)
        context["dealer"] = dealer
    
        # Retrieve reviews
        review_url = f"https://dhirajupadhy-5000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews?dealer_id={dealer_id}"
        reviews = get_dealer_reviews_from_cf(review_url, dealer_id=dealer_id)
        print(reviews)
        context["reviews"] = reviews
        # Analyze sentiments for each review and store in the review object
        # for review in reviews:
        #     review.sentiment = analyze_review_sentiments(review.review)
        #     context["reviews"] = reviews
        
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    context = {}
    # If it is a GET request
    if request.method == "GET":
        url = "https://dhirajupadhy-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        # Get dealership by id from the URL
        dealer = get_dealer_by_id_from_cf(url, dealer_id)
        print(dealer)
        # retrieve all car objects
        cars = CarModel.objects.all()
        print(cars)
        # append the dealership to context
        context["dealer"] = dealer
        # append the cars to context
        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)
    
    if request.method == "POST":
        # check if the user is authenticated
        if request.user.is_authenticated:
            url = "https://dhirajupadhy-5000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"
            username = request.user.username
            # check if the user bought a car from the dealer
            if 'purchasecheck' in request.POST:
                was_purchased = True
            else:
                was_purchased = False

            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)

            review = {}
            review["id"] = dealer_id
            review["name"] = username
            review["dealership"] = dealer_id
            review["review"] = request.POST['content']
            review["purchase"] = was_purchased
            review["purchase_date"] = request.POST['purchasedate']
            review["car_make"] = car.make.name
            review["car_model"] = car.name
            review["car_year"] = car.year.strftime("%Y")
            json_payload = {}
            json_payload["review"] = review
            response = post_request(url, json_payload['review'], dealer_id=json_payload['review']['dealership'])
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
