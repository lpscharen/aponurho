from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from models import User, Challenge, PledgeClass, Semester, Family
import random, hashlib
from datetime import date
from functions import *

msgdict = {
    'error': 'Something went wrong.  Try again.',
    'notloggedin': 'You must be logged in to access that.',
    'loggedout': 'You have been logged out.',
    'badinfo': 'Username or password is wrong.',
    'newpswd': 'A new password has been sent to your email.'
    }

def randomkey(length=32):
    random.seed()
    valid_chars = "".join([chr(x) for x in range(ord('a'), ord('z')) + range(ord('A'), ord('Z')) + range(ord('0'), ord('9'))])
    return "".join([random.choice(valid_chars) for x in range(length)])

def logout(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    user.sessionID = ""
    user.save()
    response = HttpResponseRedirect("/login?msg=loggedout")
    response.delete_cookie('key')
    return response

def login(request):
    if 'key' in request.COOKIES:
        try:
            user = User.objects.get(sessionID=request.COOKIES['key'])
            return HttpResponseRedirect("/main")
        except User.DoesNotExist:
            pass
    rkey = randomkey()
    key = Challenge(key=rkey, ip=request.META['REMOTE_ADDR'])
    key.save()
    message = ""
    if 'msg' in request.GET:
        message = msgdict[request.GET['msg']]
    t = loader.get_template('aponurho/login.html')
    c = RequestContext(request, {
            'challenge': rkey,
            'message': message
            })
    return HttpResponse(t.render(c))

def dologin(request):
    try:
        user = User.objects.get(username=request.POST['username'])
    except User.DoesNotExist:
        return HttpResponseRedirect("/login?msg=badinfo")
    if hashlib.md5(user.password + request.POST['challenge']).hexdigest() == request.POST['hashedpswd']:
        try:
            challenge = Challenge.objects.get(key=request.POST['challenge'])
        except Challenge.DoesNotExist:
            return HttpResponseRedirect("/login?msg=error")
        challenge.delete()
        response = HttpResponseRedirect("/main")
        rkey = randomkey()
        response.set_cookie('key', rkey)
        user.sessionID = rkey
        user.save()
        return response
    else:
        return HttpResponseRedirect("/login?msg=badinfo")

def createaccount(request):
    months = [(1,"January"),
        (2,"February"),
        (3,"March"),
        (4,"April"),
        (5,"May"),
        (6,"June"),
        (7,"July"),
        (8,"August"),
        (9,"September"),
        (10,"October"),
        (11,"November"),
        (12,"December")]
    message = ""
    families = Family.objects.filter(selectable=True)
    if 'msg' in request.GET:
        message = msgdict[request.GET['msg']]
    t = loader.get_template('aponurho/createaccount.html')
    c = RequestContext(request, {'message': message,
            'months': months,
            'days': range(1, 32),
            'years': range(1980, 2001),
            'pledgeclasses': PledgeClass.objects.all(),
            'families': families
            })
    return HttpResponse(t.render(c))

def docreateaccount(request):
    if User.objects.filter(username=request.POST['username']).exists():
        return HttpResponseRedirect("/createaccount?msg=nameinuse")
    elif request.POST['hashedpswd1'] != request.POST['hashedpswd2']:
        return HttpResponseRedirect("/createaccount?msg=pswdnomatch")
    elif request.POST['email1'] != request.POST['email2']:
        return HttpResponseRedirect("/createaccount?msg=emailnomatch")
    birthday = date(int(request.POST['year']), int(request.POST['month']), int(request.POST['day']))
    joinsemester = Semester.objects.get(active=True)
    pledgeclass = PledgeClass.objects.get(name=request.POST['pledgeclass'])
    if request.POST['family'] == "":
        fam = None
    else:
        fam = Family.objects.get(id=request.POST['family'])
    newuser = User(username=request.POST['username'], email=request.POST['email1'], password=request.POST['hashedpswd1'], firstName=request.POST['firstname'], lastName=request.POST['lastname'], pledgeClass=pledgeclass, family=fam, csu=request.POST['csu'], major1=request.POST['major1'], major2=request.POST['major2'], gradYear=request.POST['gradyear'], gradSemester=request.POST['gradsemester'], birthday=birthday, cellPhone=request.POST['cellphone'], campusAddress1=request.POST['campusaddress1'], campusAddress2=request.POST['campusaddress2'], permanentPhone=request.POST['permphone'], permanentAddress1=request.POST['permaddress1'], permanentAddress2=request.POST['permaddress2'], joinSemester=joinsemester, sessionID="")
    newuser.save()
    return HttpResponseRedirect("/login")
