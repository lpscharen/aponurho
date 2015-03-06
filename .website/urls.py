from django.conf.urls.defaults import *

urlpatterns = patterns('', 
  
  (r'^pages/(?P<page>\w+)/$', 'djangoproject.website.views.page'),
  (r'^contact_us' ,  'djangoproject.website.views.contact_us'),    
  (r'^' ,  'djangoproject.website.views.index'),

  #(r'^login', 'login'),
)
