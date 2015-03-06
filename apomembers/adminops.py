from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.db.models import Sum
from djangoproject.apomembers.models import User, ExecBoard, ExecBoardPermission, Philanthropy,PendingPhilanthropy, DeniedPhilanthropy, PendingCommittee, DeniedCommittee, Meeting, ServiceOpp, ServiceOppGroup, EscortShift, ExecMeeting, BrotherMeeting, BrotherOfTheWeek, HazingClaims, Family, WeekdayEscortSchedule, Requirements, ProbationRequirements
from datetime import date
from functions import *
from decimal import Decimal

msgDict = {
        "isactive": "The finished semester may not be active."
        }

def main(request):
    user = getUser(request, 'admin')
    if type(user) is HttpResponseRedirect:
        return user
    t = loader.get_template('aponurho/admins.html')
    contextDict = buildDict(user)
    execMember = {}
    execObject = ExecBoard.objects.get(user=user)
    usersPerms = execObject.permissions.all()
    permissions = ExecBoardPermission.objects.all()
    for permission in permissions:
        execMember[permission.permission] = (permission in usersPerms)
    contextDict.update({
                'execmember': execMember
                })
    c = Context(contextDict)
    return HttpResponse(t.render(c))

def semesterStatistics(request):
    user = getUser(request, 'admin')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    t = loader.get_template('aponurho/admins.semesterstatistics.html')
    totalhours = SemesterRequirements.objects.filter(semester=currentSemester).aggregate(Sum('serviceTotal'))['serviceTotal__sum']
    contextDict = buildDict(user)
    contextDict.update({
                'semester': currentSemester,
                'totalhours': totalhours
                })
    c = Context(contextDict)
    return HttpResponse(t.render(c))

def approvePhil(request):
    user = getUser(request, 'philanthropy')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    requests = PendingPhilanthropy.objects.all()
    t = loader.get_template('aponurho/admins.approvephilanthropy.html')
    contextDict = buildDict(user)
    contextDict.update({
                'requests': requests
                })
    c = Context(contextDict)
    return HttpResponse(t.render(c))

def doApprovePhil(request):
    user = getUser(request, 'philanthropy')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    reqUser = User.objects.get(id=request.GET['userid'])
    request = PendingPhilanthropy.objects.get(semester=currentSemester, user=reqUser)
    request.delete()
    sReqs = SemesterRequirements.objects.get(user=reqUser, semester=currentSemester)
    pReqs = sReqs.probation
    if (pReqs is not None) and pReqs.philanthropyReq and (pReqs.philanthropy is None):
        pReqs.philanthropy = request.philanthropy
        pReqs.save()
    else:
        sReqs.philanthropy = request.philanthropy
        sReqs.save()
    return HttpResponseRedirect("/admins/approvephilanthropy")

def doDenyPhil(request):
    user = getUser(request, 'philanthropy')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    reqUser = User.objects.get(id=request.GET['userid'])
    request = PendingPhilanthropy.objects.get(semester=currentSemester, user=reqUser)
    request.delete()
    deniedPhil = DeniedPhilanthropy(user=reqUser, philanthropy=request.philanthropy, semester=currentSemester)
    deniedPhil.save()
    return HttpResponseRedirect("/admins/approvephilanthropy")

def addPhil(request):
    user = getUser(request, 'philanthropy')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
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
    philanthropies = Philanthropy.objects.filter(semester=currentSemester)
    t = loader.get_template('aponurho/admins.addphilanthropy.html')
    contextDict = buildDict(user)
    contextDict.update({
                'months': months,
                'days': range(1, 32),
                'year': currentSemester.year,
                'philanthropies': philanthropies
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def doAddPhil(request):
    user = getUser(request, 'philanthropy')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    pDate = date(int(request.POST['year']), int(request.POST['month']), int(request.POST['day']))
    newPhil = Philanthropy(semester=currentSemester, name=request.POST['name'], date=pDate)
    newPhil.save()
    return HttpResponseRedirect("/admins/addphilanthropy")

def doRemovePhil(request):
    user = getUser(request, 'philanthropy')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    phil = Philanthropy.objects.get(id=request.GET['id']) 
    if phil.semester != currentSemester:
        return HttpResponseRedirect("/admins/addphilanthropy")
    phil.delete()
    return HttpResponseRedirect("/admins/addphilanthropy")

def committee(request):
    user = getUser(request, 'committee')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    requests = PendingCommittee.objects.filter(committeeHead=user)
    t = loader.get_template('aponurho/admins.committee.html')
    contextDict = buildDict(user)
    contextDict.update({
                'requests': requests
                })
    c = Context(contextDict)
    return HttpResponse(t.render(c))

def doApproveCommittee(request):
    user = getUser(request, 'committee')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    reqUser = User.objects.get(id=request.GET['userid'])
    request = PendingCommittee.objects.get(semester=currentSemester, user=reqUser)
    request.delete()
    sReqs = SemesterRequirements.objects.get(user=reqUser, semester=currentSemester)
    pReqs = sReqs.probation
    if (pReqs is not None) and pReqs.committeeReq and (not pReqs.committee):
        pReqs.committee = True
        pReqs.committeeName = request.name
        pReqs.committeeHead = user
        pReqs.save()
    else:
        sReqs.committee = True
        sReqs.committeeName = request.name
        sReqs.committeeHead = user
        sReqs.save()
    return HttpResponseRedirect("/admins/committee")

def doDenyCommittee(request):
    user = getUser(request, 'committee')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    reqUser = User.objects.get(id=request.GET['userid'])
    request = PendingCommittee.objects.get(semester=currentSemester, user=reqUser)
    request.delete()
    deniedPhil = DeniedCommittee(user=reqUser, name=request.name, committeeHead=request.committeeHead, semester=currentSemester)
    deniedPhil.save()
    return HttpResponseRedirect("/admins/committee")

def meetings(request):
    user = getUser(request, 'meetings')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
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
    meetings = Meeting.objects.filter(semester=currentSemester).order_by("date")
    for meeting in meetings:
        try:
            meeting.brothermeeting
            meeting.brother = True
        except BrotherMeeting.DoesNotExist:
            meeting.brother = False
    t = loader.get_template('aponurho/admins.meetings.html')
    contextDict = buildDict(user)
    contextDict.update({
                'months': months,
                'days': range(1, 32),
                'year': currentSemester.year,
                'meetings': meetings
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def doAddMeeting(request):
    user = getUser(request, 'meetings')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    pDate = date(int(request.POST['year']), int(request.POST['month']), int(request.POST['day']))
    if request.POST['type'] == 'exec':
        newMeeting = ExecMeeting(semester=currentSemester, date=pDate)
    elif request.POST['type'] == 'brother':
        newMeeting = BrotherMeeting(semester=currentSemester, date=pDate)
    else:
        return HttpResponseRedirect("/admins/meetings")
    newMeeting.save()
    return HttpResponseRedirect("/admins/meetings")

def doRemoveMeeting(request):
    user = getUser(request, 'meetings')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    meeting = Meeting.objects.get(id=request.GET['id']) 
    if meeting.semester != currentSemester:
        return HttpResponseRedirect("/admins/meetings")
    meeting.delete()
    return HttpResponseRedirect("/admins/meetings")

def dues(request):
    user = getUser(request, 'dues')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    t = loader.get_template('aponurho/admins.dues.html')
    contextDict = buildDict(user)
    semreqs = SemesterRequirements.objects.filter(semester=currentSemester).order_by("user__lastName")
    contextDict.update({
                'semreqs': semreqs
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def setDues(request):
    user = getUser(request, 'dues')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    semreqs = SemesterRequirements.objects.filter(semester=currentSemester)
    for semreq in semreqs:
        if '%s' % semreq.id in request.POST:
            semreq.dues = 1
        elif '%s-N' % semreq.id in request.POST:
            semreq.dues = 2
        else:
            semreq.dues = 0
        semreq.save()
        preq = semreq.probation
        if preq is not None:
            if '%s-P' % semreq.id in request.POST:
                preq.dues = 1
            else:
                preq.dues = 0
            preq.save()
    return HttpResponseRedirect("/admins/dues")

def service(request):
    user = getUser(request, 'service')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    services = ServiceOpp.objects.filter(semester=currentSemester)
    t = loader.get_template('aponurho/admins.service.html')
    contextDict = buildDict(user)
    contextDict.update({
                'services': services
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def addService(request):
    user = getUser(request, 'service')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    if request.POST['maxhours'] == "":
        maxCountableGroup = None
    else:
        maxCountableGroup = ServiceOppGroup(maxCountable=request.POST['maxhours'])
        maxCountableGroup.save()
    newService = ServiceOpp(name=request.POST['name'], maxCountableGroup=maxCountableGroup, semester=currentSemester)
    newService.save()
    return HttpResponseRedirect("/admins/service")

def deleteService(request):
    user = getUser(request, 'service')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    service = ServiceOpp.objects.get(id=request.GET['id'])
    if not service.permanentOpp:
        service.delete()
        if service.maxCountableGroup is not None:
            try:
                ServiceOpp.objects.get(maxCountableGroup=service.maxCountableGroup)
            except ServiceOpp.DoesNotExist:
                service.maxCountableGroup.delete()
    return HttpResponseRedirect("/admins/service")

def escort(request):
    user = getUser(request, 'escort')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
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
    shifts = EscortShift.objects.filter(semester=currentSemester).order_by("date", "shift")
    t = loader.get_template('aponurho/admins.escort.html')
    contextDict = buildDict(user)
    contextDict.update({
                'months': months,
                'days': range(1,32),
                'year': currentSemester.year,
                'shifts': shifts
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def addEscort(request):
    user = getUser(request, 'escort')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    eDate = date(int(request.POST['year']), int(request.POST['month']), int(request.POST['day']))
    try:
        sameDate = EscortShift.objects.filter(date=eDate)
    except EscortShift.DoesNotExist:
        sameDate = None
    if sameDate is None or len(sameDate) == 0:
        shift1 = EscortShift(semester=currentSemester, date=eDate, shift=False)
        shift2 = EscortShift(semester=currentSemester, date=eDate, shift=True)
        shift1.save()
        shift2.save()
    return HttpResponseRedirect("/admins/escort")

def deleteEscort(request):
    user = getUser(request, 'escort')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    shift = EscortShift.objects.get(id=request.GET['id'])
    shift.delete()
    return HttpResponseRedirect("/admins/escort")

def execboard(request):
    user = getUser(request, 'admin') #changeexec
    if type(user) is HttpResponseRedirect:
        return user
    permissions = ExecBoardPermission.objects.all()
    positions = ExecBoard.objects.all()
    t = loader.get_template('aponurho/admins.execboard.html')
    contextDict = buildDict(user)
    contextDict.update({
                'positions': positions,
                'permissions': permissions
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def changePermissions(request):
    user = getUser(request, 'admin') #changeexec
    if type(user) is HttpResponseRedirect:
        return user
    positions = ExecBoard.objects.all()
    permissions = ExecBoardPermission.objects.all()
    for position in positions:
        for permission in permissions:
            if "%s-%s" % (permission.id, position.id) in request.POST:
                if permission not in position.permissions.all():
                    position.permissions.add(permission)
            else:
                if permission in position.permissions.all():
                    position.permissions.remove(permission)
    return HttpResponseRedirect("/admins/execboard")

def changeExec(request):
    user = getUser(request, 'admin') #changeexec
    if type(user) is HttpResponseRedirect:
        return user
    positions = ExecBoard.objects.all()
    for position in positions:
        if request.POST[str(position.id)] != "":
            if request.POST[str(position.id)] == "none":
                position.user = None
                position.save()
            try:
                newMember = User.objects.get(username=request.POST[str(position.id)])
            except User.DoesNotExist:
                continue
            position.user = newMember
            position.save()
    return HttpResponseRedirect("/admins/execboard")

def pledgeClass(request):
    user = getUser(request, 'pledgeclass')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    classes = PledgeClass.objects.all()
    try:
        currentClass = PledgeClass.objects.get(semester=currentSemester)
    except PledgeClass.DoesNotExist:
        currentClass = None
    t = loader.get_template('aponurho/admins.pledgeclass.html')
    contextDict = buildDict(user)
    contextDict.update({
                'classes': classes,
                'currentclass': currentClass
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def addPledgeClass(request):
    user = getUser(request, 'pledgeclass')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    newClass = PledgeClass(semester=currentSemester, name=request.POST['classname'])
    newClass.save()
    return HttpResponseRedirect("/admins/pledgeclass")

def semester(request):
    user = getUser(request, 'semester')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        currentSemester = None
    semesters = Semester.objects.all().order_by("-year", "semester")
    t = loader.get_template('aponurho/admins.semester.html')
    contextDict = buildDict(user)
    contextDict.update({
                'semesters': semesters,
                'activesemester': currentSemester
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def endSemester(request):
    user = getUser(request, 'semester')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins/semester")
    currentSemester.active = False
    currentSemester.save()
    return HttpResponseRedirect("/admins/semester")

def setActiveSemester(request):
    user = getUser(request, 'semester')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        semester = Semester.objects.get(id=request.POST['id'])
        semester.active = True
        semester.save()
    return HttpResponseRedirect("/admins/semester")

def addSemester(request):
    user = getUser(request, 'semester')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        currentSemester = None
    name = "%s %s" % (request.POST['semester'], request.POST['year'])
    dateRaw = request.POST['meetingSixDate'].split('/')
    meetingSixDate = date(int(dateRaw[2]), int(dateRaw[0]), int(dateRaw[1])) #date takes year, month, day
    semester = Semester(name=name, semester=request.POST['semester'], year=int(request.POST['year']), serviceRequirement=int(request.POST['service']), meetingRequirement=int(request.POST['meetings']), escortRequirement=int(request.POST['escort']), escortMinHoursRequirement=int(request.POST['escort_hours']), meetingSixDate=meetingSixDate, active=False)
    semester.save()
    weekdayEscortSchedule = WeekdayEscortSchedule(semester=semester, firstWeekSunday=date(semester.year, 1, 1), lastDay=date(semester.year, 1, 1))
    weekdayEscortSchedule.save()
    #the following is deprecated as there is no longer a max on escort hours
    #escortGroup = ServiceOppGroup(maxCountable="12.5")
    #escortGroup.save()
	
    #weekdayEscort = ServiceOpp(name="Weekday Escort", maxCountableGroup=escortGroup, semester=semester, permanentOpp=True)
    #weekdayEscort.save()
    #weekendEscort = ServiceOpp(name="Weekend Escort", maxCountableGroup=escortGroup, semester=semester, permanentOpp=True, permanentHours=True)
    #weekendEscort.save()
    weekdayEscort = ServiceOpp(name="Weekday Escort", semester=semester, permanentOpp=True)
    weekdayEscort.save()
    weekendEscort = ServiceOpp(name="Weekend Escort", semester=semester, permanentOpp=True, permanentHours=True)
    weekendEscort.save()
    return HttpResponseRedirect("/admins/semester")

userData = [("Pledge Class", "pledgeClass"),
            ("Email Address", "email"),
            ("Graduation Date", "gradYear"),
            ("Family", "family"),
            ("CSU", "csu"),
            ("Cell Phone", "cellPhone"),
            ("Major(s)", "majors"),
            ("Birthday", "birthday"),
            ("Escort Trained", "escortTrained")
            ]
semesterData = [("Active", "active"),
            ("Dues", "dues"),
            ("Committee Credit", "committee"),
            ("Meetings", "meetings"),
            ("Service", "service"),
            ("Service Total", "serviceTotal"),
            ("Philanthropy", "philanthropy"),
            ("Weekend Escort", "escort")
            ]
nameData = [("Last Name", "lastName"),
            ("First Name", "firstName")
            ]
def roster(request):
    user = getUser(request, 'admin')
    if type(user) is HttpResponseRedirect:
        return user
    contextDict = buildDict(user)
    semesters = Semester.objects.all().order_by('-year', 'semester')
    order = ["lastName", "firstName"] + [d[1] for d in userData + semesterData]
    t = loader.get_template('aponurho/admins.roster.html')
    contextDict = buildDict(user)
    contextDict.update({
                'userdata': userData,
                'semesterdata': semesterData,
                'semesters': semesters,
                'order': order,
                'orderby': "lastName"
                })
    c = Context(contextDict)
    return HttpResponse(t.render(c))

def getCell(user, colName):
    if colName == "dues":
        if user.semreqs is not None:
            return "Done" if user.semreqs.dues > 0 else "Not Done"
        else:
            return "NR"
    elif colName == "active":
        if user.semreqs is not None:
            return "Active" if user.semreqs.active == 1 else ("Associate" if user.semreqs.active == 0 else "Abroad")
        else:
            return "NR"
    elif colName == "committee":
        if user.semreqs is not None:
            return "Done" if user.semreqs.committee else "Not Done"
        else:
            return "NR"
    elif colName == "meetings":
        if user.semreqs is not None:
            return user.semreqs.meetings.count()
        else:
            return "NR"
    elif colName == "philanthropy":
        if user.semreqs is not None:
            return user.semreqs.philanthropy if user.semreqs.philanthropy else "Not Done"
        else:
            return "NR"
    elif colName == "escort":
        if user.semreqs is not None:
            return user.semreqs.escortShifts.count()
        else:
            return "NR"
    elif colName == "majors":
        if user.major2 == "":
            return user.major1
        else:
            return "%s, %s" % (user.major1, user.major2)
    elif colName == "family":
        if user.family == None:
            return None
        else:
            return user.family.name
    elif colName == "lastName":
        return {'contents': user.lastName,
                'link': "info?id=%s" % user.id}
    else:
        try:
            return user.__getattribute__(colName)
        except AttributeError:
            if user.semreqs is not None:
                try:
                    return user.semreqs.__getattribute__(colName)
                except AttributeError:
                    return None
            else:
                return "NR"

def getOrderByUser(colName):
    userAttrs = User.__doc__.replace("User(", "").replace(")", "").split(", ")

    if colName in userAttrs:
        orderBy = colName
        orderedInDB = True
    elif colName == "pledgeClass":
        orderBy = "pledgeClass__id"
        orderedInDB = True
    elif colName == "majors":
        orderBy = "major1"
        orderedInDB = True
    elif colName == "family":
        orderBy = "family__name"
        orderedInDB = True
    else:
        orderBy = "lastName"
        orderedInDB = False
    return (orderBy, orderedInDB)

def manualOrderUser(userList, colName):
    cmpFnct = None
    if colName == "dues":
        cmpFnct = lambda x, y: cmp(x.semreqs.dues, y.semreqs.dues) if x.semreqs is not None and y.semreqs is not None else ((0 if x.semreqs is None else 1) if y.semreqs is None else -1)
    elif colName == "active":
        cmpFnct = lambda x, y: cmp(x.semreqs.active, y.semreqs.active) if x.semreqs is not None and y.semreqs is not None else ((0 if x.semreqs is None else 1) if y.semreqs is None else -1)
    elif colName == "committee":
        cmpFnct = lambda x, y: cmp(x.semreqs.committee, y.semreqs.committee) if x.semreqs is not None and y.semreqs is not None else ((0 if x.semreqs is None else 1) if y.semreqs is None else -1)
    elif colName == "meetings":
        cmpFnct = lambda x, y: cmp(x.semreqs.meetings.count(), y.semreqs.meetings.count()) if x.semreqs is not None and y.semreqs is not None else ((0 if x.semreqs is None else 1) if y.semreqs is None else -1)
    elif colName == "service":
        cmpFnct = lambda x, y: cmp(x.semreqs.service, y.semreqs.service) if x.semreqs is not None and y.semreqs is not None else ((0 if x.semreqs is None else 1) if y.semreqs is None else -1)
    elif colName == "philanthropy":
        cmpFnct = lambda x, y: (cmp(x.semreqs.philanthropy.name, y.semreqs.philanthropy.name) if x.semreqs.philanthropy is not None and y.semreqs.philanthropy is not None else ((0 if x.semreqs.philanthropy is None else 1) if y.semreqs.philanthropy is None else -1)) if x.semreqs is not None and y.semreqs is not None else ((0 if x.semreqs is None else 1) if y.semreqs is None else -1)
    elif colName == "escort":
        cmpFnct = lambda x, y: cmp(x.semreqs.escortShifts.count(), y.semreqs.escortShifts.count()) if x.semreqs is not None and y.semreqs is not None else ((0 if x.semreqs is None else 1) if y.semreqs is None else -1)

    if cmpFnct is not None:
        return sorted(userList, cmp=cmpFnct)
    else:
        return userList

def getOrderBySemreqs(colName):
    userAttrs = User.__doc__.replace("User(", "").replace(")", "").split(", ")
    semreqsAttrs = SemesterRequirements.__doc__.replace("SemesterRequirements(", "").replace(")", "").split(", ")

    if colName in userAttrs:
        orderBy = "user__%s" % colName
        orderedInDB = True
    elif colName in semreqsAttrs:
        orderBy = colName
        orderedInDB = True
    elif colName == "pledgeClass":
        orderBy = "user__pledgeClass__id"
        orderedInDB = True
    elif colName == "majors":
        orderBy = "user__major1"
        orderedInDB = True
    elif colName == "family":
        orderBy = "user__family__name"
        orderedInDB = True
    else:
        orderBy = "user__lastName"
        orderedInDB = False
    return (orderBy, orderedInDB)

def manualOrderSemreqs(userList, colName):
    cmpFnct = None

    if colName == "meetings":
        cmpFnct = lambda x,y: cmp(x.semreqs.meetings.count(), y.semreqs.meetings.count())
    elif colName == "philanthropy":
        cmpFnct = lambda x,y: cmp(x.semreqs.philanthropy.name, y.semreqs.philanthropy.name) if x.semreqs.philanthropy is not None and y.semreqs.philanthropy is not None else ((0 if x.semreqs.philanthropy is None else 1) if y.semreqs.philanthropy is None else -1)
    elif colName == "escort":
        cmpFnct = lambda x,y: cmp(x.semreqs.escortShifts.count(), y.semreqs.escortShifts.count())

    if cmpFnct is not None:
        return sorted(userList, cmp=cmpFnct)
    else:
        return userList

def rosterContents(request, rosterType):
    user = getUser(request, 'admin')
    if type(user) is HttpResponseRedirect:
        return user
    t = loader.get_template('aponurho/admins.html')
    contextDict = buildDict(user)
    mainDict = {}
    for tl in [userData, semesterData, nameData]:
        for d in tl:
            mainDict[d[1]] = d[0]

    headers = request.GET['order'].split(",")
    present = request.GET['present'].split(",")
    headers = [x for x in headers if x in present]

    data = []
    if rosterType == "roster":
        orderBy, orderedInDB = getOrderByUser(request.GET['orderby'])
        rUser = True
        rSemreqs = False
        userList = [x for x in User.objects.all().order_by(orderBy, "lastName", "firstName") if not x.isalum()]
        sem = Semester.objects.order_by("-year", "semester")[0]
    elif rosterType == "ghost":
        orderBy, orderedInDB = getOrderByUser(request.GET['orderby'])
        rUser = True
        rSemreqs = False
        tmpUserList = [x for x in User.objects.all().order_by(orderBy, "lastName", "firstName") if not x.isalum()]
        sem = Semester.objects.order_by("-year", "semester")[0]
        userList = []
        for user in tmpUserList:
            try:
                SemesterRequirements.objects.get(semester=sem, user=user)
            except SemesterRequirements.DoesNotExist:
                userList.append(user)
    else:
        orderBy, orderedInDB = getOrderBySemreqs(request.GET['orderby'])
        rUser = False
        rSemreqs = True
        try:
            semId = int(rosterType)
        except ValueError:
            #there's a problem - should probably do something about it
            return HttpResponse("")
        sem = Semester.objects.get(id=semId)
        userList = [x.user for x in SemesterRequirements.objects.filter(semester=sem).order_by(orderBy, "user__lastName", "user__firstName")]

    for user in userList:
        reqss = user.requirements_set.filter(semester=sem)
        user.semreqs = None
        for reqs in reqss:
            try:
                user.semreqs = reqs.semesterrequirements
            except SemesterRequirements.DoesNotExist:
                pass

    if not orderedInDB:
        if rUser:
            userList = manualOrderUser(userList, request.GET['orderby'])
        else:
            userList = manualOrderSemreqs(userList, request.GET['orderby'])
    if request.GET['reverse']:
        print "reverse"
        userList = list(reversed(userList))

    count = 1
    for user in userList:
        myData = [count]
        count += 1
        for col in headers:
            myData += [getCell(user, col)]
        data += [myData]

    headers = [(x, mainDict[x]) for x in headers]

    t = loader.get_template('aponurho/admins.rostercontents.html')
    contextDict = buildDict(user)
    contextDict.update({
                'headers': headers,
                'data': data,
                'orderby': request.GET['orderby']
                })
    c = Context(contextDict)
    return HttpResponse(t.render(c))

def escortTraining(request):
    user = getUser(request, 'escort')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    untrained = User.objects.filter(escortTrained=False).order_by('lastName')
    untrained = [tUser for tUser in untrained if not user.isalum()]
    t = loader.get_template('aponurho/admins.escorttraining.html')
    contextDict = buildDict(user)
    contextDict.update({
                'untrained': untrained
                })
    c = Context(contextDict)
    return HttpResponse(t.render(c))

def addTraining(request):
    user = getUser(request, 'escort')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
       return HttpResponseRedirect("/admins")
    user = User.objects.get(id=request.GET['userid'])
    user.escortTrained = True
    user.save()
    return HttpResponseRedirect("/admins/escorttraining")

def info(request):
    user = getUser(request, 'admin')
    if type(user) is HttpResponseRedirect:
        return user
    thisUser = User.objects.get(id=request.GET['id'])
    semreqss = SemesterRequirements.objects.filter(user=thisUser).order_by("-semester__id")
    t = loader.get_template('aponurho/admins.info.html')
    contextDict = buildDict(user)
    contextDict.update({
                'thisuser': thisUser,
                'semreqss': semreqss
                })
    c = Context(contextDict)
    return HttpResponse(t.render(c))

def card(request):
    user = getUser(request, 'admin')
    if type(user) is HttpResponseRedirect:
        return user
    semreqs = SemesterRequirements.objects.get(id=request.GET['id'])
    probreqs = semreqs.probation
    probreqs, semreqs = calcProbSemReqs(probreqs, semreqs)
    t = loader.get_template('aponurho/admins.card.html')
    contextDict = buildDict(user)
    contextDict.update({
                'semreqs': semreqs,
                'probreqs': probreqs
                })
    c = Context(contextDict)
    return HttpResponse(t.render(c))

def familyRoster(request):
    user = getUser(request, 'admin')
    if type(user) is HttpResponseRedirect:
        return user
	
    families = Family.objects.filter(selectable=True)
    familyId = '0'
    if 'familyid' in request.GET:
        familyId = request.GET['familyid']
    t = loader.get_template('aponurho/admins.familyroster.html')
    contextDict = buildDict(user)
    contextDict.update({
                'families': families,
                'familyid': int(familyId)
                })
    c = Context(contextDict)
    return HttpResponse(t.render(c))

family_headers = [
                'lastName',
                'firstName',
                'email'
                ]
def familyRosterContents(request, familyId):
    user = getUser(request, 'admin')
    if type(user) is HttpResponseRedirect:
        return user

    mainDict = {}
    for tl in [userData, semesterData, nameData]:
        for d in tl:
            mainDict[d[1]] = d[0]

    headers = family_headers
    family = Family.objects.get(id=familyId)
    userList = [x for x in User.objects.filter(family=family).order_by("lastName", "firstName") if not x.isalum()]
    sem = Semester.objects.order_by("-year", "semester")[0]

    for user in userList:
        try:
            reqss = user.requirements_set.filter(semester=sem)
            for reqs in reqss:
		try:
		    user.semreqs = reqs.semesterrequirements
		    break
		except SemesterRequirements.DoesNotExist:
		    pass
        except SemesterRequirements.DoesNotExist:
            user.semreqs = None

    count = 1
    data = []
    for user in userList:
        myData = [count]
        count += 1
        for col in headers:
            myData += [getCell(user, col)]
        data += [myData]

    headers = [(x, mainDict[x]) for x in headers]

    t = loader.get_template('aponurho/admins.familyrostercontents.html')
    contextDict = buildDict(user)
    contextDict.update({
                'headers': headers,
                'data': data,
                'family': family,
                'users': userList
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def setFamilyHead(request):
    user = getUser(request, 'admin')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
       return HttpResponseRedirect("/admins")
    family = Family.objects.get(id=request.POST['familyid'])
    newHead = User.objects.get(id=request.POST['userid'])
    if request.POST['head'] == '1':
        family.head1 = newHead
    elif request.POST['head'] == '2':
        family.head2 = newHead
    family.save()
    return HttpResponseRedirect("/admins/familyroster?familyid=%s" % request.POST['familyid'])

def escortFix(request):
    user = getUser(request, 'escort')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    contextDict = buildDict(user)
    if 'userid' in request.POST:
        targetUser = User.objects.get(id=request.POST['userid'])
        semreqs = SemesterRequirements.objects.get(user=targetUser, semester=currentSemester)
        t = loader.get_template('aponurho/admins.escortfixdate.html')
        canPull = semreqs.escortShifts.order_by('date')
        canPush = [x for x in EscortShift.objects.filter(semester=currentSemester).order_by('date') if x not in canPull]
        contextDict.update({
                    'canpull': canPull,
                    'canpush': canPush,
                    'userid': request.POST['userid']
                    })
    else:
        t = loader.get_template('aponurho/admins.escortfixname.html')
        users = [x.user for x in SemesterRequirements.objects.filter(semester=currentSemester)]
        users.sort(cmp=lambda x,y:cmp(x.lastName, y.lastName))
        contextDict.update({
                    'users': users
                    })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def escortFixFinal(request):
    user = getUser(request, 'escort')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    targetUser = User.objects.get(id=request.POST['userid'])
    semreqs = SemesterRequirements.objects.get(user=targetUser, semester=currentSemester)
    shift = EscortShift.objects.get(id=request.POST['shiftid'])
    if request.POST['type'] == 'push':
        semreqs.escortHours = Decimal(str(float(semreqs.escortHours) + 2.5))
        semreqs.service = Decimal(str(float(semreqs.service) + 2.5))
        semreqs.serviceTotal = Decimal(str(float(semreqs.serviceTotal) + 2.5))
        semreqs.escortShifts.add(shift)
    elif request.POST['type'] == 'pull':
        semreqs.escortHours = Decimal(str(float(semreqs.escortHours) - 2.5))
        semreqs.service = Decimal(str(float(semreqs.service) - 2.5))
        semreqs.serviceTotal = Decimal(str(float(semreqs.serviceTotal) - 2.5))
        semreqs.escortShifts.remove(shift)
    semreqs.save()
    return HttpResponseRedirect("/admins/escortfix")

def weekdayEscort(request):
    user = getUser(request, 'escort')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    escortDays = [(1, 0, "First Sunday"),
                (1, 1, "First Monday"),
                (1, 2, "First Tuesday"),
                (1, 3, "First Wednesday"),
                (1, 4, "First Thursday"),
                (2, 0, "Second Sunday"),
                (2, 1, "Second Monday"),
                (2, 2, "Second Tuesday"),
                (2, 3, "Second Wednesday"),
                (2, 4, "Second Thursday")]
    currentSchedule = WeekdayEscortSchedule.objects.get(semester=currentSemester)
    escortDays = zip(escortDays, currentSchedule.daysAsListOfTuples())
    months = [(1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December")]
    families = Family.objects.all()
    t = loader.get_template('aponurho/admins.weekdayescort.html')
    contextDict = buildDict(user)
    contextDict.update({
                'months': months,
                'days': range(1, 32),
                'year': currentSemester.year,
                'families': families,
                'escortdays': escortDays,
                'date1': currentSchedule.firstWeekSunday,
                'date2': currentSchedule.lastDay
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def specFams(request):
    user = getUser(request, 'escort')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    users = [x for x in User.objects.all().order_by('lastName') if not x.isalum()]
    t = loader.get_template('aponurho/admins.specfams.html')
    contextDict = buildDict(user)
    contextDict.update({
                'standards': currentSemester.standards.all(),
                'pledgestaff': currentSemester.pledgeStaff.all(),
                'users': users
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def addToSpecFam(request):
    user = getUser(request, 'escort')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    tUser = User.objects.get(id=request.POST['userid'])
    if request.POST['fam'] == 'standards':
        currentSemester.standards.add(tUser)
    elif request.POST['fam'] == 'pledgeStaff':
        currentSemester.pledgeStaff.add(tUser)
    currentSemester.save()
    return HttpResponseRedirect("/admins/specfams")

def removeFromSpecFam(request):
    user = getUser(request, 'escort')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    tUser = User.objects.get(id=request.GET['userid'])
    if request.GET['fam'] == 'standards':
        currentSemester.standards.remove(tUser)
    elif request.GET['fam'] == 'pledgeStaff':
        currentSemester.pledgeStaff.remove(tUser)
    currentSemester.save()
    return HttpResponseRedirect("/admins/specfams")

def setWeekdayEscort(request):
    user = getUser(request, 'escort')
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/admins")
    schedule = WeekdayEscortSchedule.objects.get(semester=currentSemester)
    schedule.firstWeekSunday = date(int(request.POST['year1']), int(request.POST['month1']), int(request.POST['day1']))
    schedule.lastDay = date(int(request.POST['year2']), int(request.POST['month2']), int(request.POST['day2']))
    for week in range(1, 3):
        for day in range(0, 5):
            for number in range(1, 3):
                if request.POST['family-%s-%s-%s' % (week, day, number)] == '-1':
                    continue
                family = Family.objects.get(id=request.POST['family-%s-%s-%s' % (week, day, number)])
                schedule.setByWeekDayNumber(week, day, number, family)
    schedule.save()
    return HttpResponseRedirect("/admins/weekdayescort")

def probationSemesters(request):
    user = getUser(request, 'probation')
    if type(user) is HttpResponseRedirect:
        return user
    message = None
    if 'msg' in request.GET:
        message = msgDict[request.GET['msg']]
    semesters = Semester.objects.all().order_by("-id")
    t = loader.get_template('aponurho/admins.probationsemesters.html')
    contextDict = buildDict(user)
    contextDict.update({
                'semesters': semesters,
                'message': message
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def probationUsers(request):
    user = getUser(request, 'probation')
    if type(user) is HttpResponseRedirect:
        return user
    message = None
    if 'msg' in request.GET:
        message = msgDict[request.GET['msg']]
    sem = Semester.objects.get(id=request.GET['sem1'])
    sem2 = Semester.objects.get(id=request.GET['sem2'])
    if sem.active:
        return HttpResponseRedirect("/admins/probationsemesters?msg=isactive")
    tmpGhosts = [x for x in User.objects.all().order_by("lastName", "firstName") if not x.isalum() and x.pledgeClass.semester != sem]
    tmpGhosts2 = []
    for tmpGhost in tmpGhosts:
        try:
            SemesterRequirements.objects.get(semester=sem, user=tmpGhost)
        except SemesterRequirements.DoesNotExist:
            tmpGhosts2.append(tmpGhost)

    tmpProbUsers = [x.user for x in SemesterRequirements.objects.filter(semester=sem).order_by("user__lastName", "user__firstName") if x.remainingRequirements() is not None]

    ghosts = []
    for tmpGhost in tmpGhosts2:
        try:
            ProbationRequirements.objects.get(semester=sem2, user=tmpGhost)
        except ProbationRequirements.DoesNotExist:
            ghosts.append(tmpGhost)

    probUsers = []
    onProbUsers = []
    for tmpGhost in tmpProbUsers:
        try:
            ProbationRequirements.objects.get(semester=sem2, user=tmpGhost)
            onProbUsers.append(tmpGhost)
        except ProbationRequirements.DoesNotExist:
            probUsers.append(tmpGhost)

    t = loader.get_template('aponurho/admins.probationusers.html')
    contextDict = buildDict(user)
    contextDict.update({
                'message': message,
                'sem1': request.GET['sem1'],
                'sem2': request.GET['sem2'],
                'ghosts': ghosts,
                'probusers': probUsers,
                'onprobusers': onProbUsers
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def probation(request):
    user = getUser(request, 'probation')
    if type(user) is HttpResponseRedirect:
        return user
    message = None
    if 'msg' in request.GET:
        message = msgDict[request.GET['msg']]

    sem = Semester.objects.get(id=request.GET['sem1'])
    sem2 = Semester.objects.get(id=request.GET['sem2'])

    thisUser = User.objects.get(id=request.GET['userid'])
    id = -1
    try:
        probreqs = ProbationRequirements.objects.get(semester=sem2, user=thisUser)
        reqs = {'philanthropy': 1 if probreqs.philanthropyReq else 0,
                'committee': 1 if probreqs.committeeReq else 0,
                'dues': 1 if probreqs.duesReq else 0,
                'service': probreqs.serviceReq,
                'escort': probreqs.escortReq,
                'meetings': probreqs.meetingReq
                }
        id = probreqs.id
        try:
            semreqs = SemesterRequirements.objects.get(semester=sem, user=thisUser)
        except SemesterRequirements.DoesNotExist:
            semreqs = None
    except ProbationRequirements.DoesNotExist:
        try:
            semreqs = SemesterRequirements.objects.get(semester=sem, user=thisUser)
            reqs = semreqs.remainingRequirements()
        except SemesterRequirements.DoesNotExist:
            semreqs = None
            reqs = {
                'philanthropy': 1,
                'committee': 1,
                'dues': 1,
                'service': sem.serviceRequirement,
                'escortHours': sem.escortMinHoursRequirement,
                'escort': sem.escortRequirement,
                'meetings': sem.meetingRequirement
                }

    t = loader.get_template('aponurho/admins.probation.html')
    contextDict = buildDict(user)
    contextDict.update({
                'message': message,
                'reqs': reqs,
                'id': id,
                'sem1': request.GET['sem1'],
                'sem2': request.GET['sem2'],
                'userid': request.GET['userid'],
                'semreqs': semreqs,
                'thisuser': thisUser
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def deleteProbation(request):
    user = getUser(request, 'probation')
    if type(user) is HttpResponseRedirect:
        return user

    prob = ProbationRequirements.objects.get(id=request.GET['id'])
    try:
        semreqs = SemesterRequirements.objects.get(probation=prob)
        semreqs.probation = None
        semreqs.save()
    except SemesterRequirements.DoesNotExist:
        pass
    prob.delete()
    return HttpResponseRedirect("/admins/probationusers?sem1=%s&sem2=%s" % (request.GET['sem1'], request.GET['sem2']))

def doProbation(request):
    user = getUser(request, 'probation')
    if type(user) is HttpResponseRedirect:
        return user
    sem = Semester.objects.get(id=request.GET['sem1'])
    sem2 = Semester.objects.get(id=request.GET['sem2'])
    thisUser = User.objects.get(id=request.GET['userid'])
    
    try:
        prob = ProbationRequirements.objects.get(semester=sem2, user=thisUser)
        prob.committeeReq = (request.GET['committee'] == '1')
        prob.philanthropyReq = (request.GET['philanthropy'] == '1')
        prob.duesReq = (request.GET['dues'] == '1')
        prob.meetingReq = request.GET['meetings']
        prob.serviceReq = request.GET['service']
        prob.escortHoursReq = request.GET['escortHours']
        prob.escortReq = request.GET['escort']
        prob.save()
    except ProbationRequirements.DoesNotExist:
        prob = ProbationRequirements(user=thisUser, semester=sem2, committeeReq=(request.GET['committee'] == '1'), philanthropyReq=(request.GET['philanthropy'] == '1'), duesReq=(request.GET['dues'] == '1'), meetingReq=request.GET['meetings'], serviceReq=request.GET['service'], escortHoursReq=request.GET['escortHours'], escortReq=request.GET['escort'])
        prob.save()

    try:
        semreqs = SemesterRequirements.objects.get(user=thisUser, semester=sem2)
        semreqs.probation = prob
        semreqs.save()
    except SemesterRequirements.DoesNotExist:
        pass

    return HttpResponseRedirect("/admins/probationusers?sem1=%s&sem2=%s" % (request.GET['sem1'], request.GET['sem2']))
    
def brotherOfTheWeek(request):
    user = getUser(request, 'brotheroftheweek')
    if type(user) is HttpResponseRedirect:
        return user
    brothers = BrotherOfTheWeek.objects.all()
    t = loader.get_template('aponurho/admins.brotheroftheweek.html')
    contextDict = buildDict(user)
    contextDict.update({
        'brothers': brothers})
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))
    
def removeBrotherOfTheWeek(request):
    user = getUser(request, 'brotheroftheweek')
    if type(user) is HttpResponseRedirect:
        return user
    brother = BrotherOfTheWeek.objects.get(id=request.GET['id'])
    brother.delete()
    return HttpResponseRedirect("/admins/brotheroftheweek")

def hazingClaim(request):
    user = getUser(request, 'hazing')
    if type(user) is HttpResponseRedirect:
        return user
    hazings = HazingClaims.objects.all()
    t = loader.get_template('aponurho/admins.hazingclaim.html')
    contextDict = buildDict(user)
    contextDict.update({
        'hazings': hazings})
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))
    
def removeHazingClaim(request):
    user = getUser(request, 'hazing')
    if type(user) is HttpResponseRedirect:
        return user
    hazing = HazingClaims.objects.get(id=request.GET['id'])
    hazing.delete()
    return HttpResponseRedirect("/admins/hazingclaim")
