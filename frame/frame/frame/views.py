from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Drinks
from .serializers import DrinkSerializer

@api_view(['GET'])
def drinks_list(request):
    drinks = Drinks.objects.all()  # Changed: variable name conflicts with model name
    serializer = DrinkSerializer(drinks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET','PUT','DELETE'])
def drink_detail(request, pk):
    detail_drink = Drinks.objects.get(pk=pk)

    if request.method == 'GET':
        serializer = DrinkSerializer(detail_drink)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == 'PUT':
        serializer = DrinkSerializer(detail_drink, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        detail_drink.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

@api_view(['POST'])
def drink_create(request):
    if request.method == 'POST':
        serializer = DrinkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)