from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Feedback

# get channels info: number, tags
@csrf_exempt
def index(request):
    body = json.loads(request.body)
    new_feedback = Feedback(**body)
    new_feedback.save()
    return HttpResponse(status=200)
