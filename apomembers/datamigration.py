import MySQLdb
from djangoproject.apomembers.models import *
from datetime import date
from djangoproject.apomembers.functions import updateService

permissionNames = [('semester', 'Change Semester'),
                    ('changeexec', 'Change Exec Board'),
                    ('escort', 'Weekend Escort'),
                    ('meetings', 'Add Meetings'),
                    ('dues', 'Set Dues'),
                    ('committee', 'Approve Committee Credit'),
                    ('philanthropy', 'Add/Approve Philanthropies'),
                    ('service', 'Add Service Opportunities'),
                    ('probation', 'Set Probation Requirements')
                    ]
execBoard = [('Webmaster', 'addufour',      [0, 1, 2, 3, 4, 6, 7, 8]),
            ('Secretary', 'kkmcginnis',     [0, 1, 2, 3, 5, 7]),
            ('President', 'jrpina',               [1, 2, 5]),
            ('Exec VP', 'klbradt',                 [2, 5]),
            ('Service VP', 'kafrazer',              [2, 5, 7]),
            ('Philanthropy VP', 'arbaum',         [2, 5, 6, 7]),
            ('VP of Membership', 'irmorrisonmonc',         [2, 5]),
            ('Social VP', 'abwhetzel',               [2, 5]),
            ('VP of ICR', 'ednovak',               [2, 5]),
            ('VP of Finance', 'jmnicol',           [2, 4, 5]),
            ('Historian', 'mkpham',               [2, 5]),
            ('Parliamentarian', 'amnagirimadugu',         [2, 5]),
            ('Standards Head', None, [8]),
            ('Escort Contact', 'jhmuirhead',         [2]),
            ('Escort Contact', None,         [2]),
            ('Escort Contact', None,       [2])
            ]
families = ['Bonobowies',
            'Corleones',
            'FILFs',
            'GDI',
            'Kennedys',
            'KGB',
            'Mayhem',
            'Ohana',
            'Orga Oglac',
            'Plastics',
            'Playmates',
            'Sigma',
            'Thundercats',
            'Tio Jesse'
            ]

def connect():
    conn = MySQLdb.connect(host="www.aponurho.org", user="aponurh1_apomain", passwd="Q9wlU4Ki", db="aponurh1_main")
    return conn

def main():
    """
    Notes: exec_board and exec_board_permissions need
    to be transferred by hand.  Make use of the permissions
    listed in "~/django-apps/aponurho/apomembers/permissions".
    """
    conn = connect()
    cursor = conn.cursor()
    numRows = cursor.execute("SELECT * FROM semesters")
    semesters = []
    pledgeStaffFam = Family(name="Pledge Staff", selectable=False)
    pledgeStaffFam.save()
    execFam = Family(name="Exec Board", selectable=False)
    execFam.save()
    standardsFam = Family(name="Standards", selectable=False)
    standardsFam.save()
    for family in families:
        newFamily = Family(name=family, head1=None, head2=None)
        newFamily.save()
    for x in range(numRows):
        semester = cursor.fetchone()
        name = "%s %s" % (semester[2], semester[3])
        newSemester = Semester(name=name, semester=semester[2], year=semester[3], serviceRequirement=semester[4], meetingRequirement=semester[5], escortRequirement=semester[6], active=(semester[7] == 1))
        newSemester.save()
        newEscortSchedule = WeekdayEscortSchedule(semester=newSemester, firstWeekSunday=date(newSemester.year, 1, 1), lastDay=date(newSemester.year, 1, 1))
        newEscortSchedule.save()
        newSemester.oldName = semester[1]
        newSemester.oldId = semester[0]
        semesters += [newSemester]
    numRows = cursor.execute("SELECT * FROM pledge_classes")
    for x in range(numRows):
        pClass = cursor.fetchone()
        newClass = PledgeClass(name=pClass[0], semester=semesters[0])
        newClass.save()
    numRows = cursor.execute("SELECT * FROM users")
    users = []
    for x in range(numRows):
        user = cursor.fetchone()
        pClass = PledgeClass.objects.get(name=user[6])
        joinSem = None
        for semester in semesters:
            if semester.oldId == user[13]:
                joinSem = semester
                break
        try:
            fam = Family.objects.get(name=user[7])
        except:
            fam = None
        newUser = User(username=user[1], password=user[2], email=user[3], firstName=user[4], lastName=user[5], pledgeClass=pClass, family=fam, csu=user[8], major1=user[9], major2=user[10], gradYear=user[11], gradSemester=user[12], joinSemester=joinSem, birthday=user[14], cellPhone=user[15], campusAddress1=user[16], campusAddress2=user[17], permanentPhone=user[18], permanentAddress1=user[19], permanentAddress2=user[20], sessionID="")
        newUser.save()
        newUser.oldId = user[0]
        users += [newUser]
    for semester in semesters:
        numRows = cursor.execute("SELECT * FROM %s_philanthropy" % semester.oldName)
        phils = []
        for x in range(numRows):
            phil = cursor.fetchone()
            if phil[2] == None:
                myDate = date(2009, 12, 31)
            else:
                myDate = phil[2]
            newPhil = Philanthropy(semester=semester, name=phil[1], date=myDate)
            newPhil.save()
            newPhil.oldId = phil[0]
            phils += [newPhil]
        numRows = cursor.execute("SELECT * FROM %s" % semester.oldName)
        semreqs = []
        for x in range(numRows):
            semreq = cursor.fetchone()
            me = None
            for user in users:
                if user.oldId == semreq[0]:
                    me = user
                    break
            head = None
            if semreq[5] != 0:
                for user in users:
                    if user.oldId == semreq[5]:
                        head = user
                        break
            myPhil = None
            if semreq[10] != 0:
                for phil in phils:
                    if phil.name == semreq[11]:
                        myPhil = phil
                        break
            newSemreq = SemesterRequirements(semester=semester, user=me, active=semreq[1], dues=semreq[2], committee=(semreq[3] == 1), committeeName=semreq[4], committeeHead=user, service=semreq[7], serviceTotal=semreq[8], philanthropy=myPhil)
            newSemreq.save()
            newSemreq.oldId = semreq[0]
            semreqs += [newSemreq]
        numRows = cursor.execute("SELECT * FROM %s_escort" % semester.oldName)
        for x in range(numRows):
            escort = cursor.fetchone()
            newEscort1 = EscortShift(semester=semester, date=escort[0], shift=False)
            newEscort2 = EscortShift(semester=semester, date=escort[0], shift=True)
            newEscort1.save()
            newEscort2.save()
        numRows = cursor.execute("SELECT * FROM %s_meetings" % semester.oldName)
        for x in range(numRows):
            meeting = cursor.fetchone()
            newMeeting = BrotherMeeting(semester=semester, date=meeting[0])
            newMeeting.save()
        numRows = cursor.execute("SELECT * FROM %s_service_opps" % semester.oldName)
        opps = []
        for x in range(numRows):
            opp = cursor.fetchone()
            if opp[2] != -1:
                newOppGroup = ServiceOppGroup(maxCountable=opp[2])
                newOppGroup.save()
            else:
                newOppGroup = None
            if opp[1] == "Weekday Escort" or opp[1] == "Escort":
                newOpp2 = ServiceOpp(name="Weekend Escort", maxCountableGroup=newOppGroup, semester=semester)
                newOpp2.save()
                opps += [newOpp2]
            newOpp = ServiceOpp(name=opp[1], maxCountableGroup=newOppGroup, semester=semester)
            newOpp.save()
            newOpp.oldId = opp[0]
            opps += [newOpp]
        numRows = cursor.execute("SELECT * FROM %s_service_hours" % semester.oldName)
        sum = 0
        for x in range(numRows):
            service = cursor.fetchone()
            for user in users:
                if service[1] == user.oldId:
                    break
            else:
                print "User id %s not found (service)." % service[1]
                continue
            try:
                SemesterRequirements.objects.get(user=user, semester=semester)
            except SemesterRequirements.DoesNotExist:
                print "User's semreqs (id %s) not found (service)." % service[1]
            for opp in opps:
                if opp.name == service[3]:
                    break
            else:
                print "Service project %s not found." % service[3]
                continue
            newService = ServiceHours(user=user, date=service[2], type=opp, hours=service[4], description=service[5])
            sum += service[4]
            newService.save()
        print "Total hours for %s: %s" % (semester.oldName, sum)
        numRows = cursor.execute("SELECT * FROM %s_escort_signup" % semester.oldName)
        for x in range(numRows):
            signup = cursor.fetchone()
            for semreq in semreqs:
                if semreq.oldId == signup[1]:
                    break
            else:
                print "User id %s not found (escort)." % signup[1]
                continue
            shift = EscortShift.objects.get(date=signup[2], shift=(signup[3] == 1))
            semreq.escortShifts.add(shift)
            semreq.save()
        numRows = cursor.execute("SELECT * FROM %s_meetings_attended" % semester.oldName)
        for x in range(numRows):
            signup = cursor.fetchone()
            for semreq in semreqs:
                if semreq.oldId == signup[1]:
                    break
            else:
                print "User id %s not found (meeting)." % signup[1]
                continue
            meeting = Meeting.objects.get(date=signup[2])
            semreq.meetings.add(meeting)
            semreq.save()
        for user in User.objects.all():
            updateService(user, semester)
    permissions = []
    for perm in permissionNames:
        newPerm = ExecBoardPermission(permission=perm[0], name=perm[1])
        newPerm.save()
        permissions += [newPerm]
    for member in execBoard:
        if member[1] is None:
            user = None
        else:
            user = User.objects.get(username=member[1])
        newMember = ExecBoard(position=member[0], user=user)
        newMember.save()
        for perm in member[2]:
            newMember.permissions.add(permissions[perm])
        newMember.save()
    conn.close()

if __name__ == "__main__":
    main()
