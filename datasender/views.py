from django.contrib.auth.models import User
from django.http import HttpResponseServerError, HttpResponse
from rest_framework import permissions
from rest_framework.utils import json
from rest_framework.views import APIView
from application.models import SensorReading, Sensor, Device, get_measurement_type


class DataRecordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        json_data = json.loads(request.body)
        try:
            username = json_data['username']
        except KeyError:
            return HttpResponseServerError("Corrupted data!")

        context = {}
        for board in Device.objects.all():
            if board.enabled:
                user = User.objects.get(id=board.user_id).username
                if user == username:
                    context.update({board.name: {}})

        for sensor in Sensor.objects.all():
            if sensor.enabled:
                board = Device.objects.get(id=sensor.Board_id).name
                if board in context.keys():
                    readings = {}
                    for reading in SensorReading.objects.all():
                        if reading.sensor_id == sensor.id:
                            readings.update({reading.timestamp.__str__()[:19]: reading.value})
                    context[board].update(
                        {sensor.name: {'measure': sensor.measure, 'unit': get_measurement_type(sensor),
                                       'type': sensor.type, 'readings': readings}})

        return HttpResponse(json.dumps(context))
