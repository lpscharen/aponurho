from django.db import models
from datetime import datetime, date, timedelta

class Semester(models.Model):
    name = models.CharField(max_length=15)
    semester = models.CharField(max_length=10)
    year = models.IntegerField()
    serviceRequirement = models.IntegerField()
    meetingRequirement = models.IntegerField()
    escortRequirement = models.IntegerField()
    escortMinHoursRequirement = models.IntegerField()
    active = models.BooleanField()
    pledgeStaff = models.ManyToManyField("User", blank=True, related_name="pledgeStaff")
    standards = models.ManyToManyField("User", blank=True, related_name="standards")
    meetingSixDate = models.DateField(null=True)
	
    def __unicode__(self):
        return self.name

class Challenge(models.Model):
    key = models.CharField(max_length=16)
    ip = models.IPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

class PledgeClass(models.Model):
    name = models.CharField(max_length=16)
    semester = models.ForeignKey(Semester)

    def __unicode__(self):
        return self.name

class Family(models.Model):
    name = models.CharField(max_length=32)
    head1 = models.ForeignKey("User", blank=True, null=True, related_name="head1_user")
    head2 = models.ForeignKey("User", blank=True, null=True, related_name="head2_user")
    selectable = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    def weekdayEscortShifts(self, semester):
        """return a list of escort shifts.  empty list if anything goes wrong.
        in implementation, is actually a generator."""
        try:
            schedule = WeekdayEscortSchedule.objects.get(semester=semester)
        except:
            return
        if self not in schedule.daysAsList():
            return
        for position, tup in zip(range(0,10), schedule.daysAsListOfTuples()):
            if self in tup:
                break
        #now position is the day, kind of
        if position > 4:
            position += 2
        #now position is day offset from sunday
        day = schedule.firstWeekSunday + timedelta(position)
        while day <= schedule.lastDay:
            yield day
            day += timedelta(14)
        return


class WeekdayEscortSchedule(models.Model):
    semester = models.ForeignKey(Semester)
    firstWeekSunday = models.DateField(default=date(2000, 1, 1))
    lastDay = models.DateField(default=date(2000, 1, 1))
    firstSunday1 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="fS1")
    firstMonday1 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="fM1")
    firstTuesday1 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="fT1")
    firstWednesday1 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="fW1")
    firstThursday1 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="fR1")
    firstSunday2 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="fS2")
    firstMonday2 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="fM2")
    firstTuesday2 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="fT2")
    firstWednesday2 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="fW2")
    firstThursday2 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="fR2")
    secondSunday1 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="sS1")
    secondMonday1 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="sM1")
    secondTuesday1 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="sT1")
    secondWednesday1 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="sW1")
    secondThursday1 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="sR1")
    secondSunday2 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="sS2")
    secondMonday2 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="sM2")
    secondTuesday2 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="sT2")
    secondWednesday2 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="sW2")
    secondThursday2 = models.ForeignKey(Family, blank=True, null=True, default=None, related_name="sR2")

    def daysAsListOfTuples(self):
        return [(self.firstSunday1, self.firstSunday2),
                (self.firstMonday1, self.firstMonday2),
                (self.firstTuesday1, self.firstTuesday2),
                (self.firstWednesday1, self.firstWednesday2),
                (self.firstThursday1, self.firstThursday2),
                (self.secondSunday1, self.secondSunday2),
                (self.secondMonday1, self.secondMonday2),
                (self.secondTuesday1, self.secondTuesday2),
                (self.secondWednesday1, self.secondWednesday2),
                (self.secondThursday1, self.secondThursday2)]

    def daysAsList(self):
        return [item for l in self.daysAsListOfTuples() for item in l]

    def setByWeekDayNumber(self, week, day, number, family):
        if week == 1:
            if day == 0:
                if number == 1:
                    self.firstSunday1 = family
                elif number == 2:
                    self.firstSunday2 = family
                else:
                    raise ValueError("Number must be 1 or 2.")
            elif day == 1:
                if number == 1:
                    self.firstMonday1 = family
                elif number == 2:
                    self.firstMonday2 = family
                else:
                    raise ValueError("Number must be 1 or 2.")
            elif day == 2:
                if number == 1:
                    self.firstTuesday1 = family
                elif number == 2:
                    self.firstTuesday2 = family
                else:
                    raise ValueError("Number must be 1 or 2.")
            elif day == 3:
                if number == 1:
                    self.firstWednesday1 = family
                elif number == 2:
                    self.firstWednesday2 = family
                else:
                    raise ValueError("Number must be 1 or 2.")
            elif day == 4:
                if number == 1:
                    self.firstThursday1 = family
                elif number == 2:
                    self.firstThursday2 = family
                else:
                    raise ValueError("Number must be 1 or 2.")
            else:
                raise ValueError("Day must be in range(0,5).")
        elif week == 2:
            if day == 0:
                if number == 1:
                    self.secondSunday1 = family
                elif number == 2:
                    self.secondSunday2 = family
                else:
                    raise ValueError("Number must be 1 or 2.")
            elif day == 1:
                if number == 1:
                    self.secondMonday1 = family
                elif number == 2:
                    self.secondMonday2 = family
                else:
                    raise ValueError("Number must be 1 or 2.")
            elif day == 2:
                if number == 1:
                    self.secondTuesday1 = family
                elif number == 2:
                    self.secondTuesday2 = family
                else:
                    raise ValueError("Number must be 1 or 2.")
            elif day == 3:
                if number == 1:
                    self.secondWednesday1 = family
                elif number == 2:
                    self.secondWednesday2 = family
                else:
                    raise ValueError("Number must be 1 or 2.")
            elif day == 4:
                if number == 1:
                    self.secondThursday1 = family
                elif number == 2:
                    self.secondThursday2 = family
                else:
                    raise ValueError("Number must be 1 or 2.")
            else:
                raise ValueError("Day must be in range(0,5).")
        else:
            raise ValueError("Week must be 1 or 2.")

class User(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    email = models.EmailField()
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20)
    pledgeClass = models.ForeignKey(PledgeClass)
    family = models.ForeignKey(Family, blank=True, null=True)
    csu = models.IntegerField()
    major1 = models.CharField(max_length=25)
    major2 = models.CharField(max_length=25)
    gradYear = models.IntegerField()
    gradSemester = models.IntegerField()
    joinSemester = models.ForeignKey(Semester)
    birthday = models.DateField()
    cellPhone = models.CharField(max_length=15)
    campusAddress1 = models.CharField(max_length=40)
    campusAddress2 = models.CharField(max_length=40)
    permanentPhone = models.CharField(max_length=15)
    permanentAddress1 = models.CharField(max_length=40)
    permanentAddress2 = models.CharField(max_length=40)
    escortTrained = models.BooleanField(default=False)
    sessionID = models.CharField(max_length=32, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.firstName, self.lastName)

    def isalum(self):
        recentSemester = Semester.objects.order_by('-year', 'semester')[0]
        if self.gradYear < recentSemester.year:
            return True
        elif self.gradYear == recentSemester.year:
            if self.gradSemester == 1:
                return False
            elif recentSemester.semester == 'Fall':
                return True
            else:
                return False
        else:
            return False

    def name(self):
        return "%s %s" % (self.firstName, self.lastName)

class ExecBoardPermission(models.Model):
    permission = models.CharField(max_length=32)
    name = models.CharField(max_length=32)

    def __unicode__(self):
        return self.name

class ExecBoard(models.Model):
    position = models.CharField(max_length=32)
    user = models.ForeignKey(User, blank=True, null=True)
    permissions = models.ManyToManyField(ExecBoardPermission, blank=True)

    def __unicode__(self):
        return "%s - %s" % (self.position, unicode(self.user))

class EscortShift(models.Model):
    semester = models.ForeignKey(Semester)
    date = models.DateField()
    shift = models.BooleanField()
    
    def time(self):
        if self.shift:
            time = datetime(self.date.year, self.date.month, self.date.day, 23, 30)
        else:
            time = datetime(self.date.year, self.date.month, self.date.day, 21, 0)
        return time

class Meeting(models.Model):
    semester = models.ForeignKey(Semester)
    date = models.DateField()

class BrotherMeeting(Meeting):
    pass

class ExecMeeting(Meeting):
    pass

class Philanthropy(models.Model):
    semester = models.ForeignKey(Semester)
    name = models.CharField(max_length=32)
    date = models.DateField()

    def __unicode__(self):
        return self.name

class ServiceOppGroup(models.Model):
    maxCountable = models.DecimalField(max_digits=4, decimal_places=1)
    
    def __unicode__(self):
        return str(self.maxCountable)
	#return '%s-%s-%s' % (self.serviceopp_set.all()[0].name, self.serviceopp_set.count(), self.serviceopp_set.all()[0].semester.name)

class ServiceOpp(models.Model):
    name = models.CharField(max_length=32)
    maxCountableGroup = models.ForeignKey(ServiceOppGroup, null=True)
    semester = models.ForeignKey(Semester)
    permanentOpp = models.BooleanField(default=False)
    permanentHours = models.BooleanField(default=False)
    """NOTE: code in functions.updateService is dependent on only weekend
    escort having both permanentOpp and permanentHours be True"""

    def __unicode__(self):
        return '%s-%s' % (self.name, self.semester.name)

class ServiceHours(models.Model):
    user = models.ForeignKey(User)
    date = models.DateField()
    type = models.ForeignKey(ServiceOpp)
    hours = models.DecimalField(max_digits=4, decimal_places=1)
    description = models.CharField(max_length=64)

class Requirements(models.Model):
    user = models.ForeignKey(User)
    semester = models.ForeignKey(Semester)
    committee = models.BooleanField(default=False)
    committeeName = models.CharField(max_length=32, default="", blank=True)
    committeeHead = models.ForeignKey(User, related_name="committeeheaded_set", null=True, blank=True)
    philanthropy = models.ForeignKey(Philanthropy, null=True, blank=True)
    dues = models.IntegerField(default=0)
    agreement = models.IntegerField(default=0)

class SemesterRequirements(Requirements):
    active = models.IntegerField()
    meetings = models.ManyToManyField(Meeting, blank=True)
    service = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    serviceTotal = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    escortHours = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    escortShifts = models.ManyToManyField(EscortShift, blank=True)
    probation = models.ForeignKey("ProbationRequirements", blank=True, null=True)
    
    def __unicode__(self):
        return "%s: %s" % (self.user.name(), self.semester.name)

    def remainingRequirements(self):
        """returns a dictionary of all requirements,
        or None if they're all done"""
        reqs = {
            'philanthropy': 0,
            'committee': 0,
            'dues': 0,
            'service': 0,
            'escort': 0,
            'escortHours': 0,
            'meetings': 0
            }
        if self.dues == 0:
            reqs['dues'] += 1
        if self.active == 1:
            if self.philanthropy is None:
                reqs['philanthropy'] += 1
            if not self.committee:
                reqs['committee'] += 1
            if self.probation is None:
                if self.service < self.semester.serviceRequirement:
                    reqs['service'] = self.semester.serviceRequirement - self.service
                if self.escortHours < self.semester.escortMinHoursRequirement:
                    reqs['escortHours'] = self.semester.escortMinHoursRequirement - self.escortHours
                if self.meetings.count() < self.semester.meetingRequirement:
                    reqs['meetings'] = self.semester.meetingRequirement - self.meetings.count()
                if self.escortShifts.count() < self.semester.escortRequirement:
                    reqs['escort'] = self.semester.escortRequirement - self.escortShifts.count()
            else:
                if self.probation.philanthropyReq and self.probation.philanthropy is None:
                    reqs['philanthropy'] += 1
                if self.probation.committeeReq and not self.probation.committee:
                    reqs['committee'] += 1
                if self.probation.duesReq and self.probation.dues == 0:
                    reqs['dues'] += 1
                if self.service < self.semester.serviceRequirement + self.probation.serviceReq:
                    reqs['service'] = self.semester.serviceRequirement + self.probation.serviceReq - self.service
                if self.escortHours < self.semester.escortMinHoursRequirement + self.probation.escortHoursReq:
                    reqs['escortHours'] = self.semester.escortMinHoursRequirement + self.probation.escortHoursReq - self.escortHours
                if self.meetings.count() < self.semester.meetingRequirement + self.probation.meetingReq:
                    reqs['meetings'] = self.semester.meetingRequirement + self.probation.meetingReq - self.meetings.count()
                if self.escortShifts.count() < self.semester.escortRequirement + self.probation.escortReq:
                    reqs['escort'] = self.semester.escortRequirement + self.probation.escortReq - self.escortShifts.count()
        else:
            if self.probation is not None:
                if self.probation.philanthropyReq and self.probation.philanthropy is None:
                    reqs['philanthropy'] += 1
                if self.probation.committeeReq and not self.probation.committee:
                    reqs['committee'] += 1
                if self.probation.duesReq and self.probation.dues == 0:
                    reqs['dues'] += 1
                if self.service < self.probation.serviceReq:
                    reqs['service'] = self.probation.serviceReq - self.service
                if self.escortHours < self.probation.escortHoursReq:
                    reqs['escortHours'] = self.probation.escortHoursReq - self.escortHours
                if self.meetings.count() < self.probation.meetingReq:
                    reqs['meetings'] = self.probation.meetingReq - self.meetings.count()
                if self.escortShifts.count() < self.probation.escortReq:
                    reqs['escort'] = self.probation.escortReq - self.escortShifts.count()
        for req, rem in reqs.items():
            if rem > 0:
                return reqs
        return None

class ProbationRequirements(Requirements):
    """Note: semester points to the semester that holds its requirements,
    not the semester that it applies to.  Use its semreqs semester for
    the semester it applies to."""
    committeeReq = models.BooleanField()
    philanthropyReq = models.BooleanField()
    duesReq = models.BooleanField()
    meetingReq = models.IntegerField()
    serviceReq = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    escortHoursReq = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    escortReq = models.IntegerField()

    def __unicode__(self):
        return "%s: %s" % (self.user.name(), self.semester.name)

class PendingCommittee(models.Model):
    user = models.ForeignKey(User)
    committeeHead = models.ForeignKey(User, related_name="committeeheadedpending_set")
    name = models.CharField(max_length=32)
    semester = models.ForeignKey(Semester)

class DeniedCommittee(models.Model):
    user = models.ForeignKey(User)
    committeeHead = models.ForeignKey(User, related_name="committeeheadeddeleted_set")
    name = models.CharField(max_length=32)
    semester = models.ForeignKey(Semester)

class PendingPhilanthropy(models.Model):
    user = models.ForeignKey(User)
    philanthropy = models.ForeignKey(Philanthropy)
    semester = models.ForeignKey(Semester)
    
    def __unicode__(self):
        return "%s: %s (%s)" % (self.user, self.philanthropy.name, str(self.semester))

class DeniedPhilanthropy(models.Model):
    user = models.ForeignKey(User)
    philanthropy = models.ForeignKey(Philanthropy)
    semester = models.ForeignKey(Semester)

class BrotherOfTheWeek(models.Model):
    name = models.CharField(max_length = 40)
    description = models.TextField()
    date = models.DateField(auto_now_add = True)
    
class HazingClaims(models.Model):
    dateof = models.TextField()
    location = models.TextField()
    family = models.TextField()
    description = models.TextField()
    awareness = models.TextField()
    names = models.TextField()
    additional = models.TextField()
    contact = models.TextField()
    date = models.DateField(auto_now_add = True)
   
