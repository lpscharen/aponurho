from djangoproject.apomembers.models import User, Challenge, PledgeClass, Semester, SemesterRequirements, ExecBoard, Philanthropy, ExecBoardPermission, ServiceHours, Family, ServiceOpp
from django.http import HttpResponse, HttpResponseRedirect
from datetime import date
from operator import itemgetter
from decimal import Decimal

def getUser(request, permissionName=None):
    if 'key' not in request.COOKIES:
        return HttpResponseRedirect("/login")
    try:
        user = User.objects.get(sessionID=request.COOKIES['key'])
    except User.DoesNotExist:
        return HttpResponseRedirect("/login?msg=notloggedin")
    if permissionName == 'admin':
        if not buildDict(user)['isadmin']:
            return HttpResponseRedirect("/main")
    elif permissionName is not None and not hasPermission(user, permissionName):
        return HttpResponseRedirect("/main")
    return user

def buildDict(user):
    isAdmin = ExecBoard.objects.filter(user=user).exists()
    return {'userobj': user,
        'isadmin': isAdmin
        }

def hasPermission(user, permissionName):
    permission = ExecBoardPermission.objects.get(permission=permissionName)
    execMember = ExecBoard.objects.get(user=user)
    return (permission in execMember.permissions.all())

def updateService(user, currentSemester):
    try:
        semreqs = SemesterRequirements.objects.get(user=user, semester=currentSemester)
    except:
        return
    numShifts = semreqs.escortShifts.all().count()
    escortServiceOpp = ServiceOpp.objects.get(semester=currentSemester, permanentOpp=True, permanentHours=True)
    try:
        escortService = ServiceHours.objects.get(user=user, type=escortServiceOpp)
        if numShifts == 0:
            escortService.delete()
    except ServiceHours.DoesNotExist:
        escortService = ServiceHours(type=escortServiceOpp, user=user, description="")
    if numShifts > 0:
        escortService.hours = str(numShifts * 2.5)
        firstShift = semreqs.escortShifts.order_by("date")[0]
        escortService.date = firstShift.date
        escortService.save()
    services = ServiceHours.objects.filter(user=user, type__semester=currentSemester)
    oppGroups = {}
    total = 0
    for service in services:
        total += service.hours
        if service.type.maxCountableGroup in oppGroups:
            oppGroups[service.type.maxCountableGroup] += service.hours
        else:
            oppGroups[service.type.maxCountableGroup] = service.hours
    countable = sum([min(oppGroup.maxCountable if oppGroup is not None else 10000, oppGroups[oppGroup]) for oppGroup in oppGroups])
    semreqs.service = Decimal(str(countable))
    semreqs.serviceTotal = Decimal(str(total))
    semreqs.save()

def calcProbSemReqs(probreqs, semreqs):
    """returns tuple of (probreqs, semreqs)
    reqs contain the requirement fields:
    committeeReqP (bool)
    philanthropyReqP (bool)
    duesReqP (bool)
    meetingReqP (int)
    serviceReqP (int)
    escortReqP (int)
    and the fill fields:
    committeeP (bool)
    philanthropyP (bool)
    duesP (bool)
    meetingP (int)
    serviceP (int)
    escortP (int)
    unless they are None going in"""
    if probreqs is None:
        retProb = None
    else:
        retProb = probreqs
        retProb.committeeReqP = probreqs.committeeReq
        retProb.philanthropyReqP = probreqs.philanthropyReq
        retProb.duesReqP = probreqs.duesReq
        retProb.meetingReqP = probreqs.meetingReq
        retProb.serviceReqP = probreqs.serviceReq
        retProb.escortHoursReqP = probreqs.escortHoursReq
        retProb.escortReqP = probreqs.escortReq

        retProb.committeeP = retProb.committee
        retProb.philanthropyP = (retProb.philanthropy is not None)
        retProb.duesP = retProb.dues > 0
        if semreqs is None:
            retProb.meetingP = 0
            retProb.serviceP = 0
            retProb.escortHoursP = 0
            retProb.escortP = 0
        else:
            retProb.meetingP = semreqs.meetings.count() if semreqs.meetings.count() < retProb.meetingReqP else retProb.meetingReqP
            retProb.serviceP = semreqs.service if semreqs.service < retProb.serviceReqP else retProb.serviceReqP
            retProb.escortHoursP = semreqs.escortHours if semreqs.escortHours < retProb.escortHoursReqP else retProb.escortHoursReqP
            retProb.escortP = semreqs.escortShifts.count() if semreqs.escortShifts.count() < retProb.escortReqP else retProb.escortReqP
    if semreqs is None:
        retSem = None
    else:
        retSem = semreqs
        retSem.committeeReqP = True
        retSem.philanthropyReqP = True
        retSem.duesReqP = True
        retSem.meetingReqP = semreqs.semester.meetingRequirement
        retSem.serviceReqP = semreqs.semester.serviceRequirement
        retSem.escortHoursReqP = semreqs.semester.escortMinHoursRequirement
        retSem.escortReqP = semreqs.semester.escortRequirement

        retSem.committeeP = retSem.committee
        retSem.philanthropyP = (retSem.philanthropy is not None)
        retSem.duesP = retSem.dues > 0
        if probreqs is None:
            retSem.meetingP = retSem.meetings.count()
            retSem.serviceP = retSem.service
            retSem.escortHoursP = retSem.escortHours
            retSem.escortP = retSem.escortShifts.count()
        else:
            retSem.meetingP = semreqs.meetings.count() - retProb.meetingReqP if semreqs.meetings.count() > retProb.meetingReqP else 0
            retSem.serviceP = semreqs.service - retProb.serviceReqP if semreqs.service > retProb.serviceReqP else 0
            retSem.escortHoursP = semreqs.escortHours - retProb.escortHoursReqP if semreqs.escortHours > retProb.escortHoursReqP else 0
            retSem.escortP = semreqs.escortShifts.count() - retProb.escortReqP if semreqs.escortShifts.count() > retProb.escortReqP else 0
    return (retProb, retSem)

def specFamWEscort(user, semester):
    retArr = []
    if user in semester.pledgeStaff.all():
        fam = Family.objects.get(name="Pledge Staff")
        retArr += [{'date': d, 'name': "%s Escort" % fam.name} for d in fam.weekdayEscortShifts(semester) if d >= date.today()]
    if user in semester.standards.all():
        fam = Family.objects.get(name="Standards")
        retArr += [{'date': d, 'name': "%s Escort" % fam.name} for d in fam.weekdayEscortShifts(semester) if d >= date.today()]
    if buildDict(user)['isadmin']:
        fam = Family.objects.get(name="Exec Board")
        retArr += [{'date': d, 'name': "%s Escort" % fam.name} for d in fam.weekdayEscortShifts(semester) if d >= date.today()]
    print retArr
    return sorted(retArr, key=itemgetter('date'))
