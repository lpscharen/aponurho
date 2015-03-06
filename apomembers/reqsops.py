from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from djangoproject.apomembers.models import User, Philanthropy, PendingPhilanthropy, DeniedPhilanthropy, PendingCommittee, DeniedCommittee, Meeting, ExecMeeting, BrotherMeeting
from functions import *

def main(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    try:
        semReqs = SemesterRequirements.objects.get(user=user, semester=currentSemester)
    except SemesterRequirements.DoesNotExist:
        return HttpResponseRedirect("/main")
    t = loader.get_template("aponurho/reqs.html")
    contextDict = buildDict(user)
    c = Context(contextDict)
    return HttpResponse(t.render(c))

def committee(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    t = loader.get_template("aponurho/reqs.committee.html")
    execBoard = ExecBoard.objects.all()
    heads = [execPosition.user for execPosition in execBoard if execPosition.user is not None and hasPermission(execPosition.user, "committee")]
    try:
        pendComm = PendingCommittee.objects.get(user=user, semester=currentSemester)
    except PendingCommittee.DoesNotExist:
        pendComm = None
    try:
        denComm = DeniedCommittee.objects.get(user=user, semester=currentSemester)
    except DeniedCommittee.DoesNotExist:
        denComm = None
    semReqs = SemesterRequirements.objects.get(user=user, semester=currentSemester)
    pReqs = semReqs.probation
    contextDict = buildDict(user)
    contextDict.update({
                'dencomm': denComm,
                'pendcomm': pendComm,
                'heads': heads,
                'semreqs': semReqs,
                'probationreqs': pReqs
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def doCommittee(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    head = User.objects.get(id=request.POST['committeehead'])
    newComm = PendingCommittee(user=user, committeeHead=head, name=request.POST['committeename'], semester=currentSemester)
    newComm.save()
    return HttpResponseRedirect("/reqs/committee")

def okDeniedCommittee(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    denComm = DeniedCommittee.objects.get(user=user, semester=currentSemester)
    denComm.delete()
    return HttpResponseRedirect("/reqs/committee")

def philanthropy(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    t = loader.get_template("aponurho/reqs.philanthropy.html")
    contextDict = buildDict(user)
    philanthropies = Philanthropy.objects.filter(semester=currentSemester)
    try:
        pendingPhil = PendingPhilanthropy.objects.get(user=user, semester=currentSemester)
    except PendingPhilanthropy.DoesNotExist:
        pendingPhil = None
    try:
        deniedPhil = DeniedPhilanthropy.objects.get(user=user, semester=currentSemester)
    except DeniedPhilanthropy.DoesNotExist:
        deniedPhil = None
    semReqs = SemesterRequirements.objects.get(user=user, semester=currentSemester)
    pReqs = semReqs.probation
    contextDict.update({
                'pendingphil': pendingPhil,
                'deniedphil': deniedPhil,
                'philanthropies': philanthropies,
                'semesterreqs': semReqs,
                'probationreqs': pReqs
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def meetings(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    t = loader.get_template("aponurho/reqs.meetings.html")
    allExecMeetings = ExecMeeting.objects.filter(semester=currentSemester)
    allBrotherMeetings = BrotherMeeting.objects.filter(semester=currentSemester)
    semreqs = SemesterRequirements.objects.get(user=user, semester=currentSemester)
    myMeetings = semreqs.meetings.all().order_by("date")
    for meeting in myMeetings:
        try:
            meeting.brothermeeting
            meeting.brother = True
        except BrotherMeeting.DoesNotExist:
            meeting.brother = False
    brotherMeetings = []
    for meeting in allBrotherMeetings:
        for myMeeting in myMeetings:
            if meeting.date == myMeeting.date:
                break
        else:
            brotherMeetings.append(meeting)
    execMeetings = []
    for meeting in allExecMeetings:
        for myMeeting in myMeetings:
            if meeting.date == myMeeting.date:
                break
        else:
            execMeetings.append(meeting)
    contextDict = buildDict(user)
    contextDict.update({
                'mymeetings': myMeetings,
                'execmeetings': execMeetings,
                'brothermeetings': brotherMeetings
                })
    c = RequestContext(request, contextDict)
    return HttpResponse(t.render(c))

def doPhilanthropy(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    phil = Philanthropy.objects.get(id=request.POST['id'])
    newPhil = PendingPhilanthropy(user=user, philanthropy=phil, semester=currentSemester)
    newPhil.save()
    return HttpResponseRedirect("/reqs/philanthropy")

def okDeniedPhilanthropy(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    deniedPhil = DeniedPhilanthropy.objects.get(user=user, semester=currentSemester)
    deniedPhil.delete()
    return HttpResponseRedirect("/reqs/philanthropy")

def cancelPendingPhilanthropy(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    pendingPhil = PendingPhilanthropy.objects.get(user=user, semester=currentSemester)
    pendingPhil.delete()
    return HttpResponseRedirect("/reqs/philanthropy")

def doAddMeeting(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    meeting = Meeting.objects.get(id=request.POST['id'])
    semreqs = SemesterRequirements.objects.get(semester=currentSemester, user=user)
    semreqs.meetings.add(meeting)
    semreqs.save()
    return HttpResponseRedirect("/reqs/meetings")

def doRemoveMeeting(request):
    user = getUser(request)
    if type(user) is HttpResponseRedirect:
        return user
    try:
        currentSemester = Semester.objects.get(active=True)
    except Semester.DoesNotExist:
        #no current semester!
        return HttpResponseRedirect("/main")
    meeting = Meeting.objects.get(id=request.GET['id'])
    semreqs = SemesterRequirements.objects.get(semester=currentSemester, user=user)
    semreqs.meetings.remove(meeting)
    semreqs.save()
    return HttpResponseRedirect("/reqs/meetings")
