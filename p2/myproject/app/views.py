from django.shortcuts import render, get_object_or_404
from .models import Chai
from .forms import ChaiVarityForm
from django.shortcuts import  get_object_or_404
# Create your views here.
def alliswell(request):
    chais = Chai.objects.all()
    return render(request, 'chai/all_chai.html', {'chais': chais})

def chaihome(request):
    return render(request, 'chai/chaihome.html')

def chai_detail(request, chai_id):
    chai = get_object_or_404(Chai, id=chai_id)
    return render(request, 'chai/chai_detail.html', {'chai': chai})

def chai_detail(request, chai_id):
    chai = get_object_or_404(Chai, pk=chai_id)
    return render(request, 'chai/chai_detail.html', {'chai': chai})

def chai_stores(request):
    stores = None

    if request.method == 'POST':
        form  = ChaiVarityForm(request.POST)
        if form.is_valid():
            selected_chai = form.cleaned_data['chai_varity']
            stores = selected_chai.stores.filter(chai_varieties = selected_chai)



    return render(request, 'chai/chai_stores.html',{'stores':stores } , {'form':form})