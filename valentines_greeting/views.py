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
            
            # Persist images as Base64 in DB (Render Free Tier Disk Workaround)
            if 'image' in request.FILES:
                import base64
                img = request.FILES['image']
                img.seek(0) # Ensure we read from the start
                encoded = base64.b64encode(img.read()).decode('utf-8')
                mime = img.content_type or 'image/jpeg'
                card.image_base64 = f"data:{mime};base64,{encoded}"
                
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
    data = get_object_or_404(Card, id=id)
    is_owner = request.user.is_authenticated and data.user_id == request.user
    
    if request.method == 'POST':
        form = Cardform(request.POST, request.FILES, instance=data)
        if form.is_valid():
            card = form.save(commit=False)
            
            # Recipient response logic
            if not is_owner:
                # Toggle based on which form was submitted
                if 'status' in request.POST:
                    card.status = True
                    card.is_rejected = False
                else: 
                    # If it was the 'No-Form' (which doesn't send 'status')
                    card.is_rejected = True
                    card.status = False
            
            # Image Persistence
            if 'image' in request.FILES:
                import base64
                img = request.FILES['image']
                img.seek(0)
                encoded = base64.b64encode(img.read()).decode('utf-8')
                mime = img.content_type or 'image/jpeg'
                card.image_base64 = f"data:{mime};base64,{encoded}"
            else:
                # Don't let an empty field overwrite existing base64
                card.image_base64 = data.image_base64

            card.save()
            messages.success(request, 'Response Recorded!' if not is_owner else 'Card Updated!')
            return redirect('card_details' if is_owner else 'home')
    else:
        form = Cardform(instance=data)
    
    template = 'card_edit_editor.html' if is_owner else 'card_update.html'
    context = {
        'title': 'Your Love Card' if not is_owner else 'Edit Card',
        'form': form,
        'data': data,
    }
    return render(request, template, context)

def card_delete(request, id):
    card = get_object_or_404(Card, id=id, user_id=request.user)  
    card.delete()
    messages.success(request, 'Card Deleted successfully!')
    return redirect('card_details')
