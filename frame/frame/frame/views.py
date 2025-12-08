from django.http import JsonResponse
from .models import Drinks
from .serializers import DrinkSerializer

def drinks_list(request):
    drinks = Drinks.objects.all()  # Changed: variable name conflicts with model name
    serializer = DrinkSerializer(drinks, many=True)
    return JsonResponse(serializer.data, safe=False)