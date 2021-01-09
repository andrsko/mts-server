from django.db.models import Model, EmailField, CharField, DateTimeField

# submitted through client
class Feedback(Model):
    email = EmailField(max_length=100, null=True, blank=True)
    name = CharField(max_length=100, null=True, blank=True)
    timestamp = DateTimeField("timestamp", auto_now_add=True, editable=False)
    topic = CharField(max_length=100, null=True, blank=True)
    message = CharField(max_length=500)
