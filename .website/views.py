from djangoproject.website.models import *

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, RequestContext


CONFIG={}

def getnavigation():
    links=link_location.objects.select_related()
    return links

from django.views.generic import list_detail
def index(request):
    'start page'
    links=link_location.objects.select_related()
    return list_detail.object_list(request, links,
    allow_empty=True,
    template_name='index.html')
    
def page(request,page=''):
    'page content'
    links=link_location.objects.select_related()
    page_c=Page.objects.get(name=page)
    return list_detail.object_list(request, links,
    extra_context = {
                   'page':page_c,
                    },
    allow_empty=True,
    template_name='page.html')





from django import forms
from django.core import validators
class ContactManipulator(forms.Manipulator):
    def __init__(self):
        self.fields = (
            forms.EmailField(field_name="your email", is_required=True),
            forms.TextField(field_name="name", length=25, maxlength=200, is_required=True),
            forms.LargeTextField(field_name="message", is_required=True),
        )
        

def contact_us(request):
    from djangoproject.settings import ADMINS
    manipulator = ContactManipulator()
    email_to=ADMINS[0][1]
    if request.POST:
        new_data = request.POST.copy()
        errors = manipulator.get_validation_errors(new_data)
        if not errors:
            manipulator.do_html2python(new_data)

            # Send e-mail using new_data here...
            from django.core.mail import send_mail, BadHeaderError
            try:
                subject='djangoproject message from  %s' % new_data['name']
                from_email=new_data['your email']
                message=new_data['message']
                send_mail(subject, message, from_email,[email_to], fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            nav=getnavigation()
            return list_detail.object_list(request, nav,template_name='contact_us_thanks.html')
    else:
        errors = new_data = {}
    nav=getnavigation()
    form = forms.FormWrapper(manipulator, new_data, errors)
    return list_detail.object_list(request, nav,template_name='contact_form.html',extra_context ={'form': form})


