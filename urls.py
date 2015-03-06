from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from djangoproject.apomembers.urls import urlpatterns as apomemberspatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^djangoproject/', include('djangoproject.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'', include(apomemberspatterns)),
    # (r'^login$', 'djangoproject.apomembers.loginops.login'),
    (r'^logout$', 'djangoproject.apomembers.loginops.logout'),
    (r'^dologin$', 'djangoproject.apomembers.loginops.dologin'),
    (r'^(.*\.js)$', 'djangoproject.apomembers.static.js'),
    (r'^createaccount$', 'djangoproject.apomembers.loginops.createaccount'),
    (r'^docreateaccount$', 'djangoproject.apomembers.loginops.docreateaccount'),
    (r'^main$', 'djangoproject.apomembers.mainops.main'),
    (r'^resetpassword$', 'djangoproject.apomembers.mainops.resetPassword'),
    (r'^doresetpassword$', 'djangoproject.apomembers.mainops.doResetPassword'),
    (r'^unregister$', 'djangoproject.apomembers.mainops.unregister'),
    (r'^changeactive$', 'djangoproject.apomembers.mainops.changeActive'),
    (r'^enroll$', 'djangoproject.apomembers.mainops.enroll'),
    (r'^editprofile$', 'djangoproject.apomembers.mainops.editprofile'),
    (r'^doeditprofile$', 'djangoproject.apomembers.mainops.doeditprofile'),
    (r'^changepassword$', 'djangoproject.apomembers.mainops.changepassword'),
    (r'^contact$', 'djangoproject.apomembers.mainops.contact'),
    (r'^doContact$', 'djangoproject.apomembers.mainops.doContact'),
    (r'^service$', 'djangoproject.apomembers.serviceops.main'),
    (r'^service/escortsignup$', 'djangoproject.apomembers.serviceops.escort'),
    (r'^service/escort$', 'djangoproject.apomembers.serviceops.escortMain'),
    (r'^service/addescort$', 'djangoproject.apomembers.serviceops.addEscort'),
    (r'^service/deleteescort$', 'djangoproject.apomembers.serviceops.deleteEscort'),
    (r'^service/escortroster$', 'djangoproject.apomembers.serviceops.escortRoster'),
    (r'^addservice$', 'djangoproject.apomembers.serviceops.addService'),
    (r'^deleteservice$', 'djangoproject.apomembers.serviceops.deleteService'),
    (r'^reqs$', 'djangoproject.apomembers.reqsops.main'),
    (r'^reqs/committee$', 'djangoproject.apomembers.reqsops.committee'),
    (r'^reqs/docommittee$', 'djangoproject.apomembers.reqsops.doCommittee'),
    (r'^reqs/okdeniedcommittee$', 'djangoproject.apomembers.reqsops.okDeniedCommittee'),
    (r'^reqs/philanthropy$', 'djangoproject.apomembers.reqsops.philanthropy'),
    (r'^reqs/dophilanthropy$', 'djangoproject.apomembers.reqsops.doPhilanthropy'),
    (r'^reqs/okdeniedphilanthropy$', 'djangoproject.apomembers.reqsops.okDeniedPhilanthropy'),
    (r'^reqs/cancelpendingphilanthropy$', 'djangoproject.apomembers.reqsops.cancelPendingPhilanthropy'),
    (r'^reqs/meetings$', 'djangoproject.apomembers.reqsops.meetings'),
    (r'^reqs/doaddmeeting$', 'djangoproject.apomembers.reqsops.doAddMeeting'),
    (r'^reqs/doremovemeeting$', 'djangoproject.apomembers.reqsops.doRemoveMeeting'),
    (r'^admins$', 'djangoproject.apomembers.adminops.main'),
    (r'^admins/semesterstats$', 'djangoproject.apomembers.adminops.semesterStatistics'),
    (r'^admins/approvephilanthropy$', 'djangoproject.apomembers.adminops.approvePhil'),
    (r'^admins/addphilanthropy$', 'djangoproject.apomembers.adminops.addPhil'),
    (r'^admins/committee$', 'djangoproject.apomembers.adminops.committee'),
    (r'^admins/meetings$', 'djangoproject.apomembers.adminops.meetings'),
    (r'^admins/dues$', 'djangoproject.apomembers.adminops.dues'),
    (r'^admins/service$', 'djangoproject.apomembers.adminops.service'),
    (r'^admins/escort$', 'djangoproject.apomembers.adminops.escort'),
    (r'^admins/escorttraining$', 'djangoproject.apomembers.adminops.escortTraining'),
    (r'^admins/escortfix$', 'djangoproject.apomembers.adminops.escortFix'),
    (r'^admins/escortfixfinal$', 'djangoproject.apomembers.adminops.escortFixFinal'),
    (r'^admins/weekdayescort$', 'djangoproject.apomembers.adminops.weekdayEscort'),
    (r'^admins/specfams$', 'djangoproject.apomembers.adminops.specFams'),
    (r'^admins/execboard$', 'djangoproject.apomembers.adminops.execboard'),
    (r'^admins/pledgeclass$', 'djangoproject.apomembers.adminops.pledgeClass'),
    (r'^admins/probationsemesters$', 'djangoproject.apomembers.adminops.probationSemesters'),
    (r'^admins/probationusers$', 'djangoproject.apomembers.adminops.probationUsers'),
    (r'^admins/probation$', 'djangoproject.apomembers.adminops.probation'),
    (r'^admins/doprobation$', 'djangoproject.apomembers.adminops.doProbation'),
    (r'^admins/semester$', 'djangoproject.apomembers.adminops.semester'),
    (r'^admins/roster$', 'djangoproject.apomembers.adminops.roster'),
    (r'^admins/rostercontents/(.*)$', 'djangoproject.apomembers.adminops.rosterContents'),
    (r'^admins/info$', 'djangoproject.apomembers.adminops.info'),
    (r'^admins/card$', 'djangoproject.apomembers.adminops.card'),
    (r'^admins/familyroster$', 'djangoproject.apomembers.adminops.familyRoster'),
    (r'^admins/familyrostercontents/(.*)$', 'djangoproject.apomembers.adminops.familyRosterContents'),
    (r'^admins/doaddphilanthropy$', 'djangoproject.apomembers.adminops.doAddPhil'),
    (r'^admins/doremovephilanthropy$', 'djangoproject.apomembers.adminops.doRemovePhil'),
    (r'^admins/doapprovephilanthropy$', 'djangoproject.apomembers.adminops.doApprovePhil'),
    (r'^admins/dodenyphilanthropy$', 'djangoproject.apomembers.adminops.doDenyPhil'),
    (r'^admins/approvecommittee$', 'djangoproject.apomembers.adminops.doApproveCommittee'),
    (r'^admins/denycommittee$', 'djangoproject.apomembers.adminops.doDenyCommittee'),
    (r'^admins/doaddmeeting$', 'djangoproject.apomembers.adminops.doAddMeeting'),
    (r'^admins/doremovemeeting$', 'djangoproject.apomembers.adminops.doRemoveMeeting'),
    (r'^admins/setdues$', 'djangoproject.apomembers.adminops.setDues'),
    (r'^admins/addservice$', 'djangoproject.apomembers.adminops.addService'),
    (r'^admins/deleteservice$', 'djangoproject.apomembers.adminops.deleteService'),
    (r'^admins/addescort$', 'djangoproject.apomembers.adminops.addEscort'),
    (r'^admins/deleteescort$', 'djangoproject.apomembers.adminops.deleteEscort'),
    (r'^admins/changepermissions$', 'djangoproject.apomembers.adminops.changePermissions'),
    (r'^admins/changeexec$', 'djangoproject.apomembers.adminops.changeExec'),
    (r'^admins/addpledgeclass$', 'djangoproject.apomembers.adminops.addPledgeClass'),
    (r'^admins/endsemester$', 'djangoproject.apomembers.adminops.endSemester'),
    (r'^admins/setactivesemester$', 'djangoproject.apomembers.adminops.setActiveSemester'),
    (r'^admins/addsemester$', 'djangoproject.apomembers.adminops.addSemester'),
    (r'^admins/addtraining$', 'djangoproject.apomembers.adminops.addTraining'),
    (r'^admins/setfamilyhead$', 'djangoproject.apomembers.adminops.setFamilyHead'),
    (r'^admins/setweekdayescort$', 'djangoproject.apomembers.adminops.setWeekdayEscort'),
    (r'^admins/addtospecfam$', 'djangoproject.apomembers.adminops.addToSpecFam'),
    (r'^admins/removefromspecfam$', 'djangoproject.apomembers.adminops.removeFromSpecFam'),
    (r'^$', redirect_to, {'url': '/main'}),
    (r'^login.php$', redirect_to, {'url': '/main'}),
    (r'^main.php$', redirect_to, {'url': '/main'}),
)