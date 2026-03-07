from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Card
from .forms import Cardform

# Create your views here.

def home(request):
    
    context = {
        'title' : 'Welcome To Home Page'
    }
    
    return render(request,'home.html', context)


@login_required
def create_card(request):
    
    if request.method == 'POST':
        form = Cardform(request.POST, request.FILES)
        if form.is_valid():
            card = form.save(commit=False)
            
            # Render Free Tier Workaround: Save the image file as a Base64 string directly in PostgreSQL
            # This makes the image completely permanent even if the server restarts!
            if 'image' in request.FILES:
                import base64
                image_file = request.FILES['image']
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                mime_type = image_file.content_type
                card.image_base64 = f"data:{mime_type};base64,{encoded_string}"
                
            card.save()
            messages.success(request, 'Card created successfully!')
            return redirect('card_details')  

    else:
        form = Cardform(initial={'user_id':request.user})

    context = {
        'title': 'Welcome To Greeting Creation Page',
        'form': form,
    }
    
    return render(request, 'card_create.html', context)




@login_required
def card_details(request):
    # Retrieve all cards associated with the logged-in user
    data = Card.objects.filter(user_id=request.user)  
    
    context = {
        'title': 'Card Details Page',
        'datas': data,
    }
    return render(request, 'card_details.html', context)



def card_update (request,id):
    try:
        data = Card.objects.get(id=id)

    except:
        return HttpResponse('data not found')
    if request.method == 'POST':
        form = Cardform(request.POST, request.FILES, instance=data)
        if form.is_valid():
            card = form.save(commit=False)
            if 'image' in request.FILES:
                import base64
                image_file = request.FILES['image']
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                mime_type = image_file.content_type
                card.image_base64 = f"data:{mime_type};base64,{encoded_string}"
            card.save()

            messages.success(request, 'Card Updated successfully!')
            return redirect('card_details')
    else:
        form=Cardform(instance=data)
    context = {
        'title':'Your Love Card',
        'form':form,
        'data': data,
    }
    return render(request,'card_update.html',context)

def card_delete(request, id):
    card = get_object_or_404(Card, id=id, user_id=request.user)  
    card.delete()
    messages.success(request, 'Card Deleted successfully!')
    return redirect('card_details')
