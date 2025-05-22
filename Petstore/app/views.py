from django.shortcuts import render, HttpResponse, redirect
from .models import Pet
from django.contrib.auth.models import User

# Create your views here.

from datetime import datetime


def index(req):
    allpets = Pet.objects.all()
    # petsdata = Pet.objects.filter(petname="Mini")
    # print(petsdata)
    return render(req, "index.html", {"allpets": allpets})


from django.core.exceptions import ValidationError


def validate_password(password):
    if len(password) < 8 and len(password) > 128:
        raise ValidationError(
            "Password must be atleast 8 character long and less than 128"
        )

    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False
    specialchars = "@$!%*?&"

    for char in password:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
        elif char in specialchars:
            has_special = True

    if not has_upper:
        raise ValidationError("Password must contain at least one uppercase letter")

    if not has_lower:
        raise ValidationError("Password must contain at least one lowercase letter")

    if not has_digit:
        raise ValidationError("Password must contain at least one digit letter")

    if not has_special:
        raise ValidationError(
            "Password must contain at least one special char (e.g. @$!%*?&)"
        )

    commonpassword = ["password", "123456", "qwerty", "abc123"]
    if password in commonpassword:
        raise ValidationError("This password is too common. Please choose another one.")


def signup(req):
    if req.method == "GET":
        print(req.method)  # GET
        return render(req, "signup.html")
    else:
        print(req.method)  # POST
        uname = req.POST["uname"]
        uemail = req.POST["uemail"]
        upass = req.POST["upass"]
        ucpass = req.POST["ucpass"]
        print(uname, upass, ucpass, uemail)
        context = {}
        try:
            validate_password(upass)
        except ValidationError as e:
            context["errmsg"] = str(e)
            return render(req, "signup.html", context)

        if upass != ucpass:
            errmsg = "Password and Confirm password must be same"
            context = {"errmsg": errmsg}
            return render(req, "signup.html", context)
        elif uname == upass:
            errmsg = "Password should not be same as email id"
            context = {"errmsg": errmsg}
            return render(req, "signup.html", context)
        else:
            try:
                userdata = User.objects.create(
                    username=uname, email=uemail, password=upass
                )
                userdata.set_password(upass)
                userdata.save()
                print(User.objects.all())
                return redirect("signin")
            except:
                errmsg = "User already exists. Try with different username"
                context = {"errmsg": errmsg}
                return render(req, "signup.html", context)


from django.contrib.auth import authenticate, login, logout


def signin(req):
    if req.method == "GET":
        print(req.method)
        return render(req, "signin.html")
    else:
        uname = req.POST.get("uname")
        uemail = req.POST.get("uemail")
        upass = req.POST["upass"]
        print(uname, uemail, upass)
        # userdata = User.objects.filter(email=uemail, password=upass)
        userdata = authenticate(username=uname, email=uemail, password=upass)
        print(userdata)  # if matched with user then it show its id
        if userdata is not None:
            login(req, userdata)
            # return render(req, "dashboard.html")
            return redirect("dashboard")
        else:
            context = {}
            context["errmsg"] = "Invalid email or password"
            return render(req, "signin.html", context)


def dashboard(req):
    print(req.user)
    username = req.user
    allpets = Pet.objects.all()
    print(allpets)
    return render(req, "dashboard.html", {"username": username, "allpets": allpets})


def userlogout(req):
    logout(req)
    return redirect("/")


def petdetails(req, petid):
    petdata = Pet.objects.get(petid=petid)
    context = {"petdata": petdata}
    return render(req, "petdetails.html", context)


from .forms import PetForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView


class PetRegister(CreateView):
    model = Pet
    fields = "__all__"
    success_url = "/dashboard"


class PetUpdate(UpdateView):
    model = Pet
    template_name_suffix = "_update_form"
    fields = "__all__"
    success_url = "/dashboard"


class PetDelete(DeleteView):
    model = Pet
    success_url = "/dashboard"


from django.contrib import messages
from django.db.models import Q


def searchpets(req):
    query = req.GET["q"]
    print(query)
    allpets = Pet.objects.filter(
        Q(petname__icontains=query) | Q(description__icontains=query)
    )
    print(allpets, len(allpets))

    if len(allpets) == 0:
        messages.error(req, "No result found!!")

    context = {"allpets": allpets}

    if req.user.is_authenticated:
        return render(req, "dashboard.html", context)
    else:
        return render(req, "index.html", context)


def searchbygender(req):
    gender = req.GET["gender"]
    if gender == "male":
        allpets = Pet.objects.filter(gender__exact="Male")
    else:
        allpets = Pet.objects.filter(gender__exact="Female")
    print(allpets)
    context = {"allpets": allpets}
    return render(req, "index.html", context)


def req_password(req):
    if req.method == "POST":
        uemail = req.POST["uemail"]
        try:
            user = User.objects.get(email=uemail)
            print(user.email, user)
            return redirect("reset_password", uemail=user.email)

        except User.DoesNotExist:
            messages.error(req, "No account found with this email id.")
            return render(req, "req_password.html")
    else:
        return render(req, "req_password.html")


def reset_password(req, uemail):
    user = User.objects.get(email=uemail)
    print(user)
    if req.method == "POST":
        upass = req.POST["upass"]
        ucpass = req.POST["ucpass"]
        if upass != ucpass:
            messages.error(req, "Confirm password and password do not match.")
            return render(req, "reset_password.html", {"uemail": uemail})
        else:
            validate_password(ucpass)
            user.set_password(upass)
            user.save()
            return redirect("signin")
    else:
        return render(req, "reset_password.html", {"uemail": uemail})
