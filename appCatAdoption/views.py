from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib import messages
import bcrypt


# Create your views here.
def index(request):
    return render(request,'index.html')

#####################################################################################
# register user
#####################################################################################

def register(request):
    # check input errors
    errors = User.objects.regEntryValidate(request.POST)
    if len(errors)>0:
        for k,eMsgs in errors.items():
            messages.error(request,eMsgs)
        return redirect('/')

    # check userExists
    errors = User.objects.regExistValidate(request.POST)
    if len(errors)>0:
        for k,eMsgs in errors.items():
            messages.error(request,eMsgs)    
        return redirect('/')
        # emailAlready = User.objects.filter(email=request.POST['email']).first()
        # if emailAlready:
        #     messages.error(request,"Email Already Exists - Please Login")
    else:
        # hash pswd
        hashedPW = bcrypt.hashpw(request.POST['pswd'].encode(),bcrypt.gensalt()).decode()
        # create user in DB
        newUser = User.objects.create(firstnm=request.POST['firstnm']
                            ,lastnm=request.POST['lastnm']
                            ,email=request.POST['email']
                            ,pswd=hashedPW)
        # save newUser in session
        request.session['currUserID'] = newUser.id
        return redirect('/success')


def login(request):
    # validate email/user exists/pswd
    errors = User.objects.loginValidate(request.POST)
    if len(errors)>0:
        for k,eMsgs in errors.items():
            messages.error(request,eMsgs)
        return redirect('/')
    
    loggedInUser = User.objects.filter(email=request.POST['email']).first()
    request.session['currUserID'] = loggedInUser.id
    return redirect('/success')


def logout(request):
    request.session.clear()
    return redirect('/')



#####################################################################################
# create cat
#####################################################################################

def new(request):
    # loading Add New page, grabbing all Traits
    context = {
        "allTraits" : Trait.objects.all()
    }
    return render(request,"new.html",context)

def create(request):
    # validate Cat data entry
    errors = Cat.objects.validate(request.POST)
    if len(errors)>0:
        for k,eMsgs in errors.items():
            messages.error(request,eMsgs)
        return redirect('/cat/new')

    # create cat in db
    currUser = User.objects.filter(id=request.session['currUserID']).first()
    newCat = Cat.objects.create(name=request.POST['name']
                                ,age=request.POST['age']
                                ,weight=request.POST['weight']
                                ,birthdate=request.POST['bdate']
                                ,bio=request.POST['bio']
                                ,profilePic=request.POST['url']
                                ,fosteredby=currUser)

    #capture traits checkbox; add to Cat (M2M)
    chbxTrait = request.POST.getlist("chbxTrait")
    if chbxTrait is not None:   # if len(chbxTrait) > 0:
        # print("~"*20)         # debug
        # print(f"chbxTrait - {chbxTrait}")        # ['2', '3', '4', '5']  
        for traitID in chbxTrait:
            pickedTrait = Trait.objects.get(id=traitID)
            newCat.traits.add(pickedTrait)

    #capture traits dropdown multiselect; add to Cat (M2M)
    drpdwnTrait = request.POST.getlist("drpdwnTrait")
    if drpdwnTrait is not None:
        # print("%"*20) 
        # print(f"drpdwnTrait - {drpdwnTrait}")
        for traitID in drpdwnTrait:
            newCat.traits.add(Trait.objects.get(id=traitID))


    #capture new traits from Other entry
    otherTrait = request.POST['otherTrait']
    #check blank/exists
    if otherTrait != "":        # if otherTrait is not None: compare/add trait
        otherTrait = otherTrait.title()
        foundTrait = Trait.objects.filter(name=otherTrait).first()
        if foundTrait == None:
            #add to Trait table
            newTrait = Trait.objects.create(name=otherTrait)
            #add to Cat
            newCat.traits.add(newTrait)
        else:
            newCat.traits.add(foundTrait)  


    return redirect(f'/cat/{newCat.id}')
    # return redirect('/success')


#####################################################################################
# show cat
#####################################################################################

def success(request):
    currUserID = request.session.get('currUserID')
    if currUserID is None:
        messages.error(request,'Please Register or Login')
        return redirect('/')
    else:
        adoptedCat = Cat.objects.filter(isAdopted=True)
        notAdoptedCat = Cat.objects.filter(isAdopted=False)
        context = {
            'currUser': User.objects.get(id=currUserID),
            'adoptedCat' : adoptedCat,
            'notAdoptedCat' : notAdoptedCat
        }
        return render(request,"successDashbd.html",context)


def show(request, id):
    currUserID = request.session.get('currUserID')
    if currUserID is None:
        messages.error(request,'Please Register or Login')
        return redirect('/')
    else:
        showCat = Cat.objects.filter(id=id).first()
        context = {
            'currUser': User.objects.get(id=currUserID),
            'cat' : showCat
            # 'catTraits': cat.traits.all() - M2M cat-traits - redundant here
                # <p>traits:</p>
                    # <ul>
                    #     {% for trait in catraits %}
                    #     <li>{{trait}}</li>
                    #     {% endfor %}
                    # </ul>
        }
        return render(request,"show.html",context)


def toggle(request, id):
    toggleCat = Cat.objects.filter(id=id).first()
    toggleCat.isAdopted = not toggleCat.isAdopted
    toggleCat.save()
    return redirect('/success')


def displayTraits(request):
    context = {
        'traits': Trait.objects.all()
    }
    return render(request,"traits.html",context)


#####################################################################################
# udpate cat
#####################################################################################

def edit(request, id):
    context = {
        'cat' : Cat.objects.filter(id=id).first(),
        "allTraits" : Trait.objects.all()
    }
    return render(request,"edit.html", context)


def update(request, id):
    # validate Cat data entry
    errors = Cat.objects.validate(request.POST)
    if len(errors)>0:
        for k,eMsgs in errors.items():
            messages.error(request,eMsgs)
        # return redirect(f"/cat/request.POST['id']")
        return redirect(f"/cat/{id}")

    # updateCat = Cat.objects.filter(id=request.POST['id']).first() -- use id fr. route, dont need this
    updateCat = Cat.objects.filter(id=id).first()
    updateCat.name = request.POST['name']
    updateCat.age = request.POST['age']
    updateCat.weight = request.POST['weight']
    updateCat.birthdate = request.POST['bdate']
    updateCat.bio = request.POST['bio']
    updateCat.profilePic = request.POST['url']
    updateCat.save()                            


    # update traits
    existTraits = updateCat.traits.all()    # Trait obj
    print(existTraits)
    chbxTrait = request.POST.getlist("chbxTrait")   # Trait ID List - checkbox
    # chbxTrait = request.POST.getlist("drpdwnTrait")   # Trait ID List - multiSelect (same logic below)


    # delete trait 
    for exTrait in existTraits:  
        # print(f"exTrait - {exTrait.id}")
        # print(f"chbxTrait -  {chbxTrait}")
        if str(exTrait.id) not in chbxTrait:
            updateCat.traits.remove(exTrait)
            # print(f"removed - {exTrait.id} {exTrait.name}")
        # else:
        #     print(f"keep - {exTrait.id} {exTrait.name}")

    # add trait 
    for traitID in chbxTrait:
        foundCkTrait = updateCat.traits.filter(id=traitID).first()
        if foundCkTrait == None:
            updateCat.traits.add(Trait.objects.get(id=traitID))
            print(f"add - {traitID}")
        else:
            print(f"found/did not add - {traitID}")


    # capture new traits from Other entry
    otherTrait = request.POST['otherTrait']
    # check blank/exists
    if otherTrait != "":        # if otherTrait is not None: compare/add trait
        otherTrait = otherTrait.title()
        foundTrait = Trait.objects.filter(name=otherTrait).first()
        if foundTrait == None:
            #add to Trait table
            newTrait = Trait.objects.create(name=otherTrait)
            #add to Cat
            updateCat.traits.add(newTrait)
        else:
            updateCat.traits.add(foundTrait)  

    updateCat.save() 
    return redirect(f'/cat/{updateCat.id}')


def destroy(request, id):
    cat = Cat.objects.filter(id=id).first()
    cat.delete()
    return redirect('/success')