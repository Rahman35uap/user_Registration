from django.shortcuts import render,redirect
from django.http import HttpResponse

from .email_utils import sendCustomEmail

from django.core.exceptions import ValidationError
from . import models
import time
import random
import string
import re
import logging
# Create your views here.
def index(request):
    # return HttpResponse("Welcome to SIGN UP page")
    errorMsgDict = {'userNameError':'','emailError':'','passwordError':''}
    valueDict = {'userName':'','email':'','password':'','confirmPassword':''}
    return render(request,'signup/signupForm.html',{'value':valueDict,'errorMsg':errorMsgDict})

def userRegister(request):
    logger = logging.getLogger("mylogger")
    userName = request.POST.get('userName')
    email = request.POST.get('email')
    password = request.POST.get('password')
    confirmPassword = request.POST.get('confirmPassword')

    errorMsgDict = {}
    valueDict = {'userName':userName,'email':email,'password':password,'confirmPassword':confirmPassword}
    userNameVal = userNameValidation(userName)
    emailVal = emailValidation(email)
    passwordVal = passwordValidation(password,confirmPassword)
    logger.info("user validation value => " + str(userNameVal['value']) + userNameVal["msg"])
    if(not userNameVal['value']):
        errorMsgDict['userNameError'] = userNameVal['msg']
        logger.info("user validation value => " + str(userNameVal['value']) + userNameVal["msg"])
    if(not emailVal['value']):
        errorMsgDict['emailError'] = emailVal['msg']
        logger.info(emailVal["msg"])
    if(not passwordVal['value']):
        print(passwordVal["msg"])
        errorMsgDict['passwordError'] = passwordVal['msg']

    if(len(errorMsgDict) > 0):
        return render(request,'signup/signupForm.html',{'value':valueDict,'errorMsg':errorMsgDict})

    verificationCode = get_unique_code()
    try:
        registrationCandidate = models.Users.objects.get(email = email)
    except Exception:
        registrationCandidate = None
    if(registrationCandidate != None and registrationCandidate.verified):
        # User already registered and verified with this email. Error msg to view.
        logger.info("user already verified section. return to view with error msg")
        return render(request,'signup/signupForm.html',{'value':valueDict,'errorMsg':errorMsgDict,'userExists':'User with this email already registered and verified.'})
    elif(registrationCandidate != None):
        # User already registered but not verified with this email. update the row with new info and send verification code to email
        logger.info("update section")
        registrationCandidate.user_name = userName
        registrationCandidate.email = email
        registrationCandidate.password = password
        registrationCandidate.verification_code = verificationCode
        registrationCandidate.verified = 0
        targetUserId = registrationCandidate.id
        registrationCandidate.save()
    else:
        # User not exists. Create the new User
        logger.info("create new user")
        registrationCandidate = models.Users()
        registrationCandidate.user_name = userName
        registrationCandidate.email = email
        registrationCandidate.password = password
        registrationCandidate.verification_code = verificationCode
        registrationCandidate.verified = 0
        registrationCandidate.save()
        targetUserId = registrationCandidate.id

    subject = 'account verification from Auth System'
    message = 'VERIFICATION CODE => ' + verificationCode
    receiverList = ['mailfordummy0000@gmail.com',email]  # Replace with the recipient's email addresses

    sendCustomEmail(subject, message, receiverList)
    # return HttpResponse("saved id = " + str(registrationCandidate.id))
    # targetUserId = 1
    return redirect('verify_register',targetUserId)

def verifyRegister(request,id):
    context = {"id" : id}
    return render(request,'signup/verifyRegistrationCode.html',context)
def registerSuccess(request):
    userId = request.POST.get('userId')
    verificationCode = request.POST.get('emailVerificationCode')
    logger = logging.getLogger("mylogger")
    logger.info(userId)
    try:
        targetUser = models.Users.objects.get(id = userId)
    except Exception:
        targetUser = None
    if(targetUser != None):
        # verify the verification code
        if(targetUser.verification_code != verificationCode):
            # Wrong verification code
            logger.info(targetUser.user_name)
            return render(request,'signup/verifyRegistrationCode.html',{"id":userId,"errorMsg":"Wrong verification code has been given"})
    else:
        # wrong user Id given
        logger.info("NONE")
        return render(request,'signup/verifyRegistrationCode.html',{"id":userId,"errorMsg":"Wrong User ID has been given"})
    # correct verification code has given
    targetUser.verified = 1
    targetUser.save()
    return HttpResponse("Registration completed successfully")


def userNameValidation(userName):
    if(not userName):
        return {'value':False,'msg':"User name can't be empty"}
    if(len(userName) <3):
        return {'value':False,'msg':'User name should contain at least 3 characters'}
    return {'value':True,'msg':''}
def emailValidation(email):
    if(not email):
        return {'value':False,'msg':'email Address can\'t be empty'}    
    if(bool(re.search("^[\w\-\.]+@([\w-]+\.)+[\w-]{2,4}$",email))):
        return {'value':True,'msg':''}
    return {'value':False,'msg':'email Address must be valid'}
def passwordValidation(password,confirmPassword):
    if(not password):
        return {'value':False,'msg':'password can\'t be empty'}
    if(not confirmPassword):
        return {'value':False,'msg':'confirm password can\'t be empty'}
    if(password != confirmPassword):
        return {'value':False,'msg':'Password and Confirm Password must be same'}
    elif(len(password) < 8):
        return {'value':False,'msg':'Password must contain at least 8 digits'}
    else:
        capitalLetterRange = string.ascii_uppercase
        numberRange = string.digits
        letterRange = string.ascii_letters
        if(not(any(x in capitalLetterRange for x in password))):
            return {'value':False,'msg':'Password must contain at least 1 capital letter'} 
        if(not(any(x in numberRange for x in password))):
            return {'value':False,'msg':'Password must contain at least 1 number'}
        if(not(any((x not in numberRange and x not in letterRange) for x in password))):
            return {'value':False,'msg':'Password must contain at least 1 special character'}
    return {'value':True,'msg':''}


def get_random_string(length):
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    # print random string
    return result_str
def get_unique_code():
    timeStamp = str(time.time())
    timeStamp = timeStamp.replace(".",get_random_string(5))
    return get_random_string(5) + timeStamp
