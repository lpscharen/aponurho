from django.http import HttpResponse
from django.template import Context, loader
from PIL import Image

def css(request, cssfile):
    t = loader.get_template('aponurho/' + cssfile)
    c = Context({})
    return HttpResponse(t.render(c), mimetype='text/css')

def js(request, jsfile):
    t = loader.get_template('aponurho/' + jsfile)
    c = Context({})
    return HttpResponse(t.render(c), mimetype='application/javascript')

def blank(request):
    return HttpResponse('')
