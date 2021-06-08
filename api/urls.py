from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import UserRecordView

app_name = 'api'
urlpatterns = [
    path('user/', csrf_exempt(UserRecordView.as_view()), name='users'),
]
