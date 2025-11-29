from django.shortcuts import render

# Create your views here.
def alliswell(request):
    return render(request, 'chai/all_chai.html')

def chaihome(request):
    return render(request, 'chai/chaihome.html')