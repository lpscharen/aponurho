from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from djangoproject.apomembers.models import User, Semester, ServiceOpp, ServiceHours, SemesterRequirements, EscortShift
from functions import getUser, buildDict, updateService
from datetime import date, datetime, timedelta
from decimal import Decimal, Inexact

messageDict = {
        "toolatesign": "That shift has already started.",
        "toolateunsign": "That shift has already started.",
        "fullshift": "That shift is full.",
        "toomanyshifts": "You can only sign up for 4 shifts."
        }

def main(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
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
    serviceOpps = ServiceOpp.objects.filter(permanentHours=False, semester=currentSemester)
    services = ServiceHours.objects.filter(user=user, type__semester=currentSemester).order_by("date")
    year = currentSemester.year
    try:
        semreqs = SemesterRequirements.objects.get(semester=currentSemester, user=user)
    except SemesterRequirements.DoesNotExist:
        return HttpResponseRedirect("/main")
    t = loader.get_template("aponurho/service.html")
    contextDict = buildDict(user)
    contextDict.update({
                'services': services,
                'serviceopps': serviceOpps,
                'year': year,
                'months': months,
                'days': range(1,32),
                'countable': semreqs.service,
                'hours': semreqs.serviceTotal
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def addService(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    sDate = date(int(request.POST['year']), int(request.POST['month']), int(request.POST['day']))
    sType = ServiceOpp.objects.get(id=request.POST['type'])
    service = ServiceHours(user=user, date=sDate, type=sType, hours=request.POST['hours'], description=request.POST['desc'])
    service.save()

    try:
        semreqs = SemesterRequirements.objects.get(semester=currentSemester, user=user)
    except SemesterRequirements.DoesNotExist:
        return HttpResponseRedirect("/main")
    a = sType.name
    if (a.encode('ascii','ignore').find("Escort") != -1) or (a.encode('ascii', 'ignore').find("escort") != -1):
        semreqs.escortHours = Decimal(str(float(semreqs.escortHours) + float(request.POST['hours'].encode('ascii','ignore'))))
        semreqs.save()
    updateService(user, currentSemester)
    return HttpResponseRedirect("/service")

def deleteService(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    service = ServiceHours.objects.get(id=request.GET['id'])
    try:
        semreqs = SemesterRequirements.objects.get(semester=currentSemester, user=user)
    except SemesterRequirements.DoesNotExist:
        return HttpResponseRedirect("/main")
    a = service.type.name
    if (a.encode('ascii', 'ignore').find("Escort") != -1) or (a.encode('ascii', 'ignore').find("escort") != -1):
        semreqs.escortHours -= Decimal(str(service.hours))
        semreqs.save()
    service.delete()
    updateService(user, currentSemester)
    return HttpResponseRedirect("/service")

def escort(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    if 'msg' in request.GET:
        message = messageDict[request.GET['msg']]
    else:
        message = None
    try:
        semreqs = SemesterRequirements.objects.get(semester=currentSemester, user=user)
    except SemesterRequirements.DoesNotExist:
        return HttpResponseRedirect("/main")
    myShifts = semreqs.escortShifts.all()
    shifts = EscortShift.objects.filter(semester=currentSemester).order_by("date", "shift")
    t = loader.get_template("aponurho/service.escort.html")
    contextDict = buildDict(user)
    contextDict.update({
                'message': message,
                'shifts': shifts,
                'myshifts': myShifts
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def addEscort(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    semreqs = SemesterRequirements.objects.get(user=user, semester=currentSemester)
    if semreqs.escortShifts.all().count() >= 4:
        return HttpResponseRedirect("/service/escortsignup?msg=toomanyshifts")
    shift = EscortShift.objects.get(id=request.GET['id'])
    if shift.semesterrequirements_set.all().count() >= 6:
        return HttpResponseRedirect("/service/escortsignup?msg=fullshift")
    if shift.time() + timedelta(hours=24) < datetime.now():
        return HttpResponseRedirect("/service/escortsignup?msg=toolatesign")
    semreqs.escortShifts.add(shift)
    #semreqs.escortHours = semreqs.escortHours + Decimal('2.5')
    semreqs.escortHours = Decimal(str(float(semreqs.escortHours) + 2.5))
    semreqs.save()
    updateService(user, currentSemester)
    return HttpResponseRedirect("/service/escortsignup")

def deleteEscort(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    semreqs = SemesterRequirements.objects.get(user=user, semester=currentSemester)
    shift = EscortShift.objects.get(id=request.GET['id'])
    if shift.time() + timedelta(hours=24) < datetime.now():
        return HttpResponseRedirect("/service/escortsignup?msg=toolateunsign")
    #semreqs.escortHours = semreqs.escortHours - Decimal('2.5')
    semreqs.escortHours = Decimal(str(float(semreqs.escortHours) - 2.5))
    semreqs.escortShifts.remove(shift)
    semreqs.save()
    updateService(user, currentSemester)
    return HttpResponseRedirect("/service/escortsignup")

def escortRoster(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")

    shifts = EscortShift.objects.filter(semester=currentSemester).order_by("date", "shift")
    hiddenShifts = [shift for shift in shifts if shift.time() + timedelta(hours=24) < datetime.now()]
    visibleShifts = [shift for shift in shifts if shift.time() + timedelta(hours=24) >= datetime.now()]

    t = loader.get_template("aponurho/service.escortroster.html")
    contextDict = buildDict(user)
    contextDict.update({
                'hiddenshifts': hiddenShifts,
                'visibleshifts': visibleShifts,
                'all': ('all' in request.GET)
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def escortMain(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    t = loader.get_template("aponurho/service.escortmain.html")
    contextDict = buildDict(user)
    c = Context(contextDict)
    return HttpResponse(t.render(c))

def float_to_decimal(f):
    "Convert a floating point number to a Decimal with no loss of information"
    n, d = f.as_integer_ratio()
    numerator, denominator = Decimal(n), Decimal(d)
    ctx = Context(prec=60)
    result = ctx.divide(numerator, denominator)
    while ctx.flags[Inexact]:
        ctx.flags[Inexact] = False
        ctx.prec *= 2
        result = ctx.divide(numerator, denominator)
    return result
