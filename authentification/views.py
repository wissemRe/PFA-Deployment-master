import copy
import os
import smtplib

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from application.models import EmailAlert
from core import settings
from core.settings import EMAIL_HOST_USER
from .forms import LoginForm, SignUpForm, ProfileUpdateForm, UserUpdateForm
from .models import UserProfile
from .utils import mqttuser

def login_view(request):
    if request.user.is_authenticated:
        return render(request, "index.html")

    form = LoginForm(request.POST or None)
    msg = None
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                #mqtt_user=mqttuser(username=username)
                #mqtt_user.sendorder()
                #mqtt_user.run()
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            #mqttuser.add_now_topic(username)

            email_alert = EmailAlert()
            subject = 'Welcome to PFA IOT Monitoring Family!'
            email_alert.subject = subject
            message = None

            recepient = str(form.cleaned_data.get("email"))
            email_alert.recipient = recepient

            ############################################################################
            html_message = render_to_string('mailTemplate.html', {'user': username})
            ############################################################################
            try:
                send_mail(subject, message, EMAIL_HOST_USER, [recepient], html_message=html_message,
                          fail_silently=False)

                form.save()
                email_alert.user = User.objects.get(username=username)
                email_alert.save()
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                profile = UserProfile.objects.create(user_id=request.user.id)
                profile.save()
                return redirect("/")
            except smtplib.SMTPException:
                msg = 'Address mail sending error!'

        else:
            msg = 'Information not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


def get_avatar_url(user):
    image_url = "/static/assets/img/faces/marc.jpg"
    try:
        directory = os.path.join(settings.MEDIA_ROOT, 'user_{0}'.format(user.id))
        files = os.listdir(directory)
        image_url = '/static/assets/avatars/user_{0}/'.format(user.id) + files[-1] if files else "/static/assets/img" \
                                                                                                 "/faces/marc.jpg "
        return image_url
    except:
        return image_url


@login_required
def updateProfile(request):
    user = copy.deepcopy(request.user)
    url = get_avatar_url(user)
    msg = ''
    success = False
    profile = UserProfile.objects.get(user_id=request.user.id)
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if p_form.is_valid() and u_form.is_valid():
            u_form.save()
            p_form.save()
            url = get_avatar_url(request.user)
            p_form = ProfileUpdateForm(instance=profile)
            u_form = UserUpdateForm(instance=request.user)
            success = True
            msg = 'Your Profile has been updated!'
        else:
            msg = 'Your Profile has not been updated! Please verify!'

    context = {'avatar': url, 'user': user, 'profile': profile, 'msg': msg, 'success': success, 'p_form': p_form,
               'u_form': u_form}

    try:
        emails = list(EmailAlert.objects.filter(user=request.user).values())
        emails = [i['subject'] for i in emails]
        inbox = len(emails)
        if inbox > 5:
            emails = emails[-5:]
            inbox = len(emails)
    except:
        emails = ['no massage inbox!']

    context.update({'inbox': inbox, 'emails': emails})

    return render(request, "page-user.html", context)
