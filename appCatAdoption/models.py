from django.db import models
import re
import bcrypt
from datetime import datetime

email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.+_-]+\.[a-zA-Z]+$') # global - share with loginValidate
class UserManager(models.Manager):
    # email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.+_-]+\.[a-zA-Z]+$') - illegal position!
    # def regValidate(self,reqpost):
    def regEntryValidate(self,reqpost):
        errors={}
        # email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.+_-]+\.[a-zA-Z]+$') - legal but cannot share
        if len(reqpost['firstnm'])<2:
            errors['firstnm'] = 'First Name: Min 2 Characters Please'
        if len(reqpost['lastnm'])<2:   
            errors['lastnm'] = 'Last Name: Min 2 Characters Please'
        if not email_regex.match(reqpost['email']):
            errors['email'] = 'Email: Missing / Wrong Format?'
        if len(reqpost['pswd']) < 8:
            errors['pswd'] = 'Password: Min 8 Characters Please'
        if reqpost['cfpswd'] != reqpost['pswd']:
            errors['cfpswd'] = 'Confirm Password: Not Matching Password'
        return errors

    def regExistValidate(self,reqpost):  
        errors={}
        emailAlready = User.objects.filter(email=reqpost['email']).first()
        if emailAlready:
            errors['email'] = "Email Already Exists - Please Login"
        return errors

    # below sub-function not working - is it possible to use a sub-function in models?
    # def emailNotFound(self,reqpost):  # return T/F
    #     emailFound = User.objects.filter(email=reqpost['email']).first()
    #     return emailFound==None

    def loginValidate(self,reqpost):
        errors={}
        if reqpost['email']=="":
            errors['email'] = 'Email: Missing at Login'
        elif not email_regex.match(reqpost['email']):
            errors['email'] = 'Email: Incorrect Format at Login'
        else:
            # check emailIsFound
            # if emailNotFound(reqpost):  ## or... emailNotFound(reqpost) == None:
            emailIsFound = User.objects.filter(email=reqpost['email']).first()
            if not emailIsFound:
                errors['emailNotFound'] = 'Email: Not Exist - Please Register'
            else:
                # check hashedpw
                # # debug
                # print("*-"*20+"\n"+userFound.firstnm)  
                # validate pswd (input pswd, db-stored pswd)
                pswdMatch = bcrypt.checkpw(reqpost['pswd'].encode(),emailIsFound.pswd.encode())
                if not pswdMatch:
                    errors['pswdNotMatch'] = "Password: Incorrect at Login"
        return errors

class User(models.Model):
    firstnm = models.CharField(max_length=50)
    lastnm = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    pswd = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

    def __repr__(self):
        return f"\nFirst: {self.firstnm}\nLast: {self.lastnm}\nEmail: {self.email}\nPswd: {self.pswd}\nCreated: {self.created_at}"

##########################################################################################################################################################################
##########################################################################################################################################################################
# python manage.py shell
# from appCatAdoption.models import *

class CatManager(models.Manager):
    def validate(self,reqpost):
        errors={}
        if len(reqpost['name'])<2:
            errors['name'] = 'Cat Name: Min 2 Characters Please'
        if reqpost['bdate']=="":   
            errors['bdate'] = 'Birthdate: Missing'
        elif datetime.strptime(reqpost['bdate'],'%Y-%m-%d') > datetime.today():
            errors['bdate'] = 'Birthdate: Why in Future?'
        if reqpost['age']=="":   
            errors['age'] = 'Age: Missing'
        if reqpost['weight']=="":   
            errors['weight'] = 'Weight: Missing'
        # if reqpost['bio']=="":   
        #     errors['bio'] = 'Bio : Missing'
        # if reqpost['url']=="":   
        #     errors['url'] = 'Profile Pic URL: Missing'
        return errors

class Trait(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return f"\nTrait: {self.name}\nId: {self.id}"


class Cat(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    weight = models.FloatField()
    birthdate = models.DateTimeField()
    bio = models.TextField(null=True)
    profilePic = models.TextField(null=True)
    isAdopted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fosteredby = models.ForeignKey(User,related_name="cats",on_delete=models.CASCADE)
    traits = models.ManyToManyField(Trait,related_name="cats")
    objects = CatManager()

    def __repr__(self):
        return f"\nCat: {self.name}\nId: {self.id}\nage: {self.age}\nbdate: {self.birthdate}\ntraits: {self.traits}\nCreated: {self.created_at}"



# python manage.py shell
# from appCatAdoption.models import *
# Trait.objects.create(name="calico")