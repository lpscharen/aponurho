from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.db.models import Sum
from django.core.mail import send_mail
from models import User, Challenge, PledgeClass, Semester, SemesterRequirements, ExecBoard, Philanthropy, Family, ProbationRequirements,BrotherOfTheWeek, HazingClaims
import random, hashlib
from datetime import datetime, date, timedelta
from functions import *
from loginops import randomkey
from operator import itemgetter

msgdict = {
        "pswdnomatch": "The new and repeated passwords do not match.",
        "badpswd": "Your old password is incorrect.",
        "pswdchanged": "Your password has been changed.",
        "alreadyassoc": "You can only go associate once.",
        "noemail": "An account with that email has not been registered."
        }

def main(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        currentSemester = None

    if 'msg' in request.GET:
        message = msgdict[request.GET['msg']]
    else:
        message = None

    upcomingEvents = []
    currentProbationReqs, currentSemesterReqs = (None, None)
    if currentSemester is not None:
        wEscort = []
        if user.family is not None:
            wEscort += [{'date': d, 'name': "%s Family Escort" % user.family.name} for d in user.family.weekdayEscortShifts(currentSemester) if d >= date.today()]
        wEscort += specFamWEscort(user, currentSemester)
        upcomingEvents += sorted(wEscort, key=itemgetter('date'))[0:2]
        try:
            currentSemesterReqs = SemesterRequirements.objects.get(semester=currentSemester, user=user)
            if currentSemesterReqs.escortHours is None:
                currentSemesterReqs.escortHours = 0
        except SemesterRequirements.DoesNotExist:
            currentSemesterReqs = None
        try:
            currentProbationReqs = ProbationRequirements.objects.get(semester=currentSemester, user=user)
        except ProbationRequirements.DoesNotExist:
            currentProbationReqs = None
        totalHours = SemesterRequirements.objects.filter(semester=currentSemester).aggregate(Sum('serviceTotal'))['serviceTotal__sum']
        if totalHours is None:
            totalHours = 0
        upPhil = list(Philanthropy.objects.filter(semester=currentSemester, date__gte=date.today()))
        upcomingEvents += [{'date': phil.date, 'name': phil.name} for phil in upPhil]
        if currentSemesterReqs is not None:
            upEscorts = list(currentSemesterReqs.escortShifts.filter(date__gte=date.today()))
            upcomingEvents += [{'date': esc.date, 'name': "Weekend Escort"} for esc in upEscorts]
        canRegister = date.today() < currentSemester.meetingSixDate + timedelta(days=1)
    else:
        currentSemesterReqs = None
        totalHours = 0
        canRegister = False
    currentProbationReqs, currentSemesterReqs = calcProbSemReqs(currentProbationReqs, currentSemesterReqs)
    upcomingEvents.sort(key=lambda x: x['date'])

    if currentSemesterReqs is not None and currentSemesterReqs.escortHours is None:
        currentSemesterReqs.escortHours = 0
        currentSemesterReqs.save()

    t = loader.get_template('aponurho/main.html')
    contextDict = buildDict(user)
    contextDict.update({
                'currentsemester': currentSemester,
                'semreqs': currentSemesterReqs,
				'canRegister': canRegister,
                'probreqs': currentProbationReqs,
                'totalhours': totalHours,
                'upcomingevents': upcomingEvents[:],
                'message': message
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def doResetPassword(request):
    try:
        user = User.objects.get(email=request.GET['email'])
    except User.DoesNotExist:
        return HttpResponseRedirect("/resetpassword?msg=noemail")
    #newpswd = randomkey(10)
    newpswd = user.email
    hashedpswd = hashlib.md5(newpswd).hexdigest()
    user.password = hashedpswd
    #user.password = newpswd
    user.save()

    to_email = user.email
    from_email = "donotreply@aponurho.org"
    body = "Your new password is %s.  Please log in and change it to something more memorable." % newpswd
    subject = 'APO OCS Password Reset'

    send_mail(subject, body, from_email, [to_email], fail_silently=True)
    
    return HttpResponseRedirect("/login?msg=newpswd")

def resetPassword(request):
    if 'msg' in request.GET:
        message = msgdict[request.GET['msg']]
    else:
        message = None
    t = loader.get_template('aponurho/resetpassword.html')
    contextDict = {}
    contextDict.update({
	        'message': message
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def enroll(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    semester = Semester.objects.get(name=request.POST['semestername'])
    if not semester.active:
        return HttpResponseRedirect("/main")
    semreqs = SemesterRequirements(semester=semester, user=user)
    if request.POST['status'] == 'active':
        semreqs.active = 1
    elif request.POST['status'] == 'associate':
        semreqs.active = 0
        assoc = SemesterRequirements.objects.filter(user=user, active=0)
        if assoc.count() > 0:
            return HttpResponseRedirect("/main?msg=alreadyassoc")
    elif request.POST['status'] == 'abroad':
        semreqs.active = 2
    else:
        return HttpResponseRedirect("/main")
    semreqs.save()
    try:
        prob = ProbationRequirements.objects.get(user=user, semester=semester)
        semreqs.probation = prob
        semreqs.save()
    except ProbationRequirements.DoesNotExist:
        pass
    updateService(user, semester)
    return HttpResponseRedirect("/main")

def unregister(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        return HttpResponseRedirect("/main")
    if request.GET['sure'] == '1':
        semreqs = SemesterRequirements.objects.get(semester=currentSemester, user=user)
        semreqs.delete()
        return HttpResponseRedirect("/main")
    t = loader.get_template('aponurho/unregister.html')
    contextDict = buildDict(user)
    contextDict.update({
                })
    c = Context(contextDict)
    return HttpResponse(t.render(c))

def changeActive(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        return HttpResponseRedirect("/main")
    semreqs = SemesterRequirements.objects.get(semester=currentSemester, user=user)
    if semreqs.active == 0:
        semreqs.active = 1
    elif semreqs.active == 1:
        semreqs.active = 0
        assoc = SemesterRequirements.objects.filter(user=user, active=0)
        if assoc.count() > 0:
            return HttpResponseRedirect("/main?msg=alreadyassoc")
    semreqs.save()
    return HttpResponseRedirect("/main")

def editprofile(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    message = ""
    if 'msg' in request.GET:
        message = msgdict[request.GET['msg']]
    families = Family.objects.filter(selectable=True)
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
    t = loader.get_template('aponurho/editprofile.html')
    contextDict = buildDict(user)
    contextDict.update({
            'months': months,
            'days': range(1, 32),
            'years': range(1980, 2001),
            'message': message,
            'families': families
            })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def doeditprofile(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    user.email = request.POST['email']
    if request.POST['family'] == "":
        user.family = None
    else:
        user.family = Family.objects.get(id=request.POST['family'])
    user.csu = request.POST['csu']
    user.major1 = request.POST['major1']
    user.major2 = request.POST['major2']
    user.gradYear = request.POST['gradyear']
    user.gradSemester = request.POST['gradsemester']
    birthday = date(int(request.POST['year']), int(request.POST['month']), int(request.POST['day']))
    user.birthday = birthday
    user.cellPhone = request.POST['cellphone']
    user.campusAddress1 = request.POST['campusaddress1']
    user.campusAddress2 = request.POST['campusaddress2']
    user.permanentPhone = request.POST['permphone']
    user.permanentAddress1 = request.POST['permaddress1']
    user.permanentAddress2 = request.POST['permaddress2']
    user.save()
    return HttpResponseRedirect("/editprofile")

def changepassword(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    if request.POST['oldpassword'] != user.password:
        return HttpResponseRedirect("/editprofile?msg=badpswd")
    if request.POST['newpassword'] != request.POST['repeatpassword']:
        return HttpResponseRedirect("/editprofile?msg=pswdnomatch")
    user.password = request.POST['newpassword']
    user.save()
    return HttpResponseRedirect("/editprofile?msg=pswdchanged")

def contact(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    execMembers = ExecBoard.objects.filter(user__isnull=False)
    t = loader.get_template('aponurho/contact.html')
    contextDict = buildDict(user)
    contextDict.update({
                'execmembers': execMembers
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def doContact(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    to_user = User.objects.get(id=request.POST['userid'])

    to_email = to_user.email
    #changed from user to to_user in order to make comments anonymous
    from_email = to_user.email
    body = request.POST['comment']
    subject = 'Contact from OCS'

    send_mail(subject, body, from_email, [to_email], fail_silently=True)

    return HttpResponseRedirect('/contact')
    
def submitBrother(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    t = loader.get_template('aponurho/submitbrother.html')
    contextDict = buildDict(user)
    contextDict.update({
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def doSubmitBrother(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    brotheroftheweek = BrotherOfTheWeek(name = request.POST["name"], description = request.POST["description"])
    brotheroftheweek.save()
    return HttpResponseRedirect('/main')

def submitHazing(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    t = loader.get_template('aponurho/submithazing.html')
    contextDict = buildDict(user)
    contextDict.update({
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def doSubmitHazing(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    hazingclaim= HazingClaims(dateof = request.POST["dateof"], location = request.POST["location"], family = request.POST["family"], description = request.POST["description"], awareness = request.POST["awareness"], names = request.POST["names"], additional = request.POST["additional"], contact = request.POST["contact"])
    hazingclaim.save()
    return HttpResponseRedirect('/main')
