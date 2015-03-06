from .models import *
from django.contrib import admin

class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester', 'year', 'meetingRequirement', 'escortRequirement', 'escortMinHoursRequirement',
                    'meetingSixDate', 'active')

class PledgeClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester')

class FamilyAdmin(admin.ModelAdmin):
    list_display = ('name', 'head1', 'head2', 'selectable')

class WeekdayEscortScheduleAdmin(admin.ModelAdmin):
    list_display = ('semester', 'firstWeekSunday', 'lastDay', 'firstSunday1', 'firstMonday1', 'firstTuesday1',
                    'firstWednesday1', 'firstThursday1', 'firstSunday2', 'firstMonday2', 'firstTuesday2',
                    'firstWednesday2', 'firstThursday2', 'secondSunday1', 'secondMonday1', 'secondTuesday1',
                    'secondWednesday1', 'secondThursday1', 'secondSunday2', 'secondMonday2', 'secondTuesday2',
                    'secondWednesday2', 'secondThursday2')

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'firstName', 'lastName', 'pledgeClass', 'family')

class ExecBoardPermissionAdmin(admin.ModelAdmin):
    list_display = ('permission', 'name')

class ExecBoardAdmin(admin.ModelAdmin):
    list_display = ('position', 'user')

class EscortShiftAdmin(admin.ModelAdmin):
    list_display = ('semester', 'date', 'shift')

class MeetingAdmin(admin.ModelAdmin):
    list_display = ('semester', 'date')

class PhilanthropyAdmin(admin.ModelAdmin):
    list_display = ('semester', 'name', 'date')

class ServiceOppAdmin(admin.ModelAdmin):
    list_display = ('name', 'maxCountableGroup', 'semester', 'permanentOpp', 'permanentHours')

class ServiceHoursAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'type', 'hours')

class RequirementsAdmin(admin.ModelAdmin):
    list_display = ('user', 'semester', 'committee', 'committeeName', 'committeeHead', 'philanthropy', 'dues', 'agreement')

class SemesterRequirementsAdmin(admin.ModelAdmin):
    list_display = ('user', 'semester', 'active', 'service', 'serviceTotal', 'escortHours', 'probation')

class ProbationRequirementsAdmin(admin.ModelAdmin):
    list_display = ('committeeReq', 'philanthropyReq', 'duesReq', 'meetingReq', 'serviceReq', 'escortHoursReq', 'escortReq')

class BrotherOfTheWeekAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')

class HazingClaimsAdmin(admin.ModelAdmin):
    list_display = ('dateof', 'location', 'family', 'awareness', 'names', 'contact', 'date')

admin.site.register(Semester, SemesterAdmin)
admin.site.register(Challenge)
admin.site.register(PledgeClass, PledgeClassAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(ExecBoardPermission, ExecBoardPermissionAdmin)
admin.site.register(ExecBoard, ExecBoardAdmin)
admin.site.register(EscortShift, EscortShiftAdmin)
admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Philanthropy, PhilanthropyAdmin)
admin.site.register(ServiceOpp, ServiceOppAdmin)
admin.site.register(ServiceHours, ServiceHoursAdmin)
admin.site.register(SemesterRequirements, SemesterRequirementsAdmin)
admin.site.register(PendingCommittee)
admin.site.register(DeniedCommittee)
admin.site.register(PendingPhilanthropy)
admin.site.register(DeniedPhilanthropy)

admin.site.register(Family, FamilyAdmin)
admin.site.register(WeekdayEscortSchedule, WeekdayEscortScheduleAdmin)
admin.site.register(ProbationRequirements, ProbationRequirementsAdmin)
admin.site.register(ServiceOppGroup)
admin.site.register(BrotherOfTheWeek, BrotherOfTheWeekAdmin)
admin.site.register(HazingClaims, HazingClaimsAdmin)
