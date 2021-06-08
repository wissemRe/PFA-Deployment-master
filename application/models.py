from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


def get_measurement_type(sensor):
    return SensorSetting.objects.get(id=Sensor.objects.get(id=sensor.id).SensorSetting_id).measurement_type


#
### Sensor, Settings, and Readings
#
class Device(models.Model):
    """
    Model for Embedded Device.
    - name
    - enabled
    """

    name = models.CharField(
        max_length=30,
        blank=True,
        null=False,
        unique=True
    )
    enabled = models.BooleanField(
        default=False
    )
    user = models.ForeignKey(User, default=None, on_delete=models.SET_DEFAULT)

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return 'Board ' + str(self.id) + ': ' + self.name

    def save(self, *args, **kwargs):
        super(Device, self).save(*args, **kwargs)
        self.full_clean()
        if self.name == '':
            self.name = 'Board ' + str(self.id)
            self.save()


class Sensor(models.Model):
    """
    Model for Sensor.
    - measure type
    - type
    - name
    - enabled
    """
    Board = models.ForeignKey(
        'Device', related_name='+',
        blank=True, null=False, default=None, on_delete=models.SET_DEFAULT
    )
    user = Device.user

    MEASURE_TYPES = (
        ('TEMPERATURE', 'Temperature'),
        ('HUMIDITY', 'Humidity'),
        ('PRESSION', 'Pression'),
        ('WIND', 'Wind'),
    )
    measure = models.CharField(
        choices=MEASURE_TYPES,
        max_length=15
    )
    SensorSetting = models.ForeignKey(
        'SensorSetting', related_name='+',
        blank=True, null=False, default=None, on_delete=models.SET_DEFAULT
    )
    SENSOR_TYPES = (
        ('DHT11', 'DHT11'),
        ('DHT22', 'DHT22'),
    )
    type = models.CharField(
        choices=SENSOR_TYPES,
        max_length=5
    )
    name = models.CharField(
        max_length=30,
        blank=True,
        unique=True
    )
    enabled = models.BooleanField(
        default=False
    )

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return 'Sensor ' + str(self.id) + ': ' + str(self.name)

    def clean(self):
        # Only allow one setting of TemperatureSensor model
        # validate_only_one_instance(self)
        pass

    def save(self, *args, **kwargs):
        super(Sensor, self).save(*args, **kwargs)
        self.full_clean()
        if self.name == '':
            self.name = str(self.name) + 'Sensor ' + str(self.id)
            self.save()


class SensorSetting(models.Model):
    """
    Model for Sensor Settings.
    - sensor (FK)
    - measurement_type
    """

    name = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        unique=True
    )
    MEASUREMENT_TYPES = (
        ('%', '%'),
        ('F', 'Fahrenheit'),
        ('°C', 'Celsius'),
        ('Pa', 'Pascal'),
        ('Bar', 'Bar'),
        ('KmH', 'Km/h'),
        ('Mh', 'Miles/h'),
    )
    measurement_type = models.CharField(
        choices=MEASUREMENT_TYPES,
        max_length=3
    )

    def __unicode__(self):
        return u'%s' % self.name

    def __str__(self):
        return self.name + ' ' + str(self.id)

    def save(self, *args, **kwargs):
        super(SensorSetting, self).save(*args, **kwargs)
        self.full_clean()
        if not self.name:
            self.name = self.name + ' Set ' + str(self.id)
            self.save()


class SensorReading(models.Model):
    """
    Model for Sensor Reading.
    - sensor (FK)
    - measurement_type
    - timestamp
    - value
    """

    sensor = models.ForeignKey(
        'Sensor', related_name='+',
        blank=True, null=False, default=None, on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(
        default=timezone.now
    )
    value = models.IntegerField(
        validators=[
            MinValueValidator(-150),
            MaxValueValidator(150)
        ]
    )

    def __str__(self):
        return str(self.value) + ' ' + get_measurement_type(self.sensor)

    def __unicode__(self):
        return u'%d' % self.value


#
### Email Alerts
#
class EmailAlert(models.Model):
    """
    Model for Email Alert.
    - timestamp
    - end
    - recipient
    - user
    - sensor
    - min_value
    - max_value
    """

    user = models.ForeignKey(User, default=None, on_delete=models.CASCADE)
    board = models.ForeignKey(Device, blank=True, null=True, default=None, on_delete=models.CASCADE)
    sensor = models.ForeignKey(Sensor, blank=True, null=True, default=None, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(
        default=timezone.now
    )
    subject = models.CharField(blank=True, default='', max_length=150)
    recipient = models.EmailField()
    min_value = models.IntegerField(default=0, blank=True, null=True,
                                    validators=[
                                        MinValueValidator(-150),
                                        MaxValueValidator(150)
                                    ]
                                    )
    max_value = models.IntegerField(default=0, blank=True, null=True,
                                    validators=[
                                        MinValueValidator(-150),
                                        MaxValueValidator(150)
                                    ]
                                    )

    def __str__(self):
        return "User '" + str(self.user.username) + "': " + self.subject
