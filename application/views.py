import ast
import json


from django import template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.csrf import ensure_csrf_cookie
from httplib2 import HTTPConnectionWithTimeout

from authentification.forms import ProfileUpdateForm, UserUpdateForm
from authentification.models import UserProfile
from authentification.views import get_avatar_url
from .models import SensorReading, Sensor, \
    Device, get_measurement_type, EmailAlert





@ensure_csrf_cookie
@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    data = dict()
    issues = 0
    chartcount = False
    user = request.user
    lastLogin = User.objects.get(id=user.id).last_login.__str__()[11:16]
    lastDateLogin = User.objects.get(id=user.id).last_login.__str__()[:10]

    for board in Device.objects.all():
        if user.id == board.user_id:
            if board.enabled:
                data.update({board.name: {}})
            else:
                issues += 1

    for sensor in Sensor.objects.all():
        board = Device.objects.get(id=sensor.Board_id).name
        if board in data.keys():
            if sensor.enabled:
                chartcount = True
                readings = dict()
                for reading in SensorReading.objects.all():
                    if reading.sensor_id == sensor.id:
                        readings.update({reading.timestamp.__str__()[5:19]: reading.value})

                # to make the charts interpretable
                if len(readings.keys()) > 10:
                    readings = dict(list(readings.items())[-10:])

                data[board].update(
                    {sensor.name: {'measure': sensor.measure, 'unit': get_measurement_type(sensor),
                                   'type': sensor.type, 'readings': readings}})
            else:
                issues += 1

    if request.is_ajax and request.method == "POST":
        # send to client side.
        return JsonResponse({"data": data}, status=200)
    else:
        try:
            emails = list(EmailAlert.objects.filter(user=user).values())
            emails = [i['subject'] for i in emails]
            inbox = len(emails)
            if inbox > 5:
                emails = emails[-5:]
                inbox = len(emails)
        except:
            emails = ['no massage inbox!']

        context.update(
            {'inbox': inbox, 'emails': emails, 'data': json.dumps(data), 'issues': issues, 'lastLogin': lastLogin,
             'lastDateLogin': lastDateLogin, 'chartcount': chartcount})

        html_template = loader.get_template('index.html')

        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]
        context['segment'] = load_template

        html_template = loader.get_template(load_template)
        if load_template == "page-user.html":
            profile = UserProfile.objects.get(user_id=request.user.id)
            p_form = ProfileUpdateForm(instance=request.user)
            u_form = UserUpdateForm(instance=profile)

            context.update(
                {'avatar': get_avatar_url(request.user), 'profile': profile, 'p_form': p_form, 'u_form': u_form})

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

        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:

        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))


