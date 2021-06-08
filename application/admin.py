from django.contrib import admin

import application.models as models

admin.site.site_header = 'PFA IoT Project Dashboard'
admin.site.register(models.Device)
admin.site.register(models.Sensor)
admin.site.register(models.SensorSetting)
admin.site.register(models.SensorReading)
admin.site.register(models.EmailAlert)
