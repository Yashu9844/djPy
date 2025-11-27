from django.http import HttpResponse



def home(request):
    return HttpResponse("Welcome to the Home Page!")
def about(request):
    return HttpResponse("This is the About Page.")
def contact(request):
    return HttpResponse("Contact us at contact@example.com")