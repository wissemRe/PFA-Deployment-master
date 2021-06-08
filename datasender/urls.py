from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from datasender.views import DataRecordView

app_name = 'datasender'
urlpatterns = [
    path('getData/', csrf_exempt(DataRecordView.as_view()), name='data'),
]
