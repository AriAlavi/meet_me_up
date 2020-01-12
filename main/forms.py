from django.forms import ModelForm
from main.models import Event
class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = "__all__"
