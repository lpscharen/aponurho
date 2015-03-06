from django.db import models



class link_location(models.Model):
    link=models.CharField(maxlength=60)
    def __str__(self):
        return self.link
    class Admin:
        pass

class Page(models.Model):
    name=models.CharField(maxlength=20,core=True)
    description = models.TextField(null=True, blank=True)
    link_location=models.ManyToManyField(link_location,null=True, blank=True,filter_interface=True)
    def __str__(self):
        return self.name
    class Admin:
	list_display = ('name', )
        search_fields = ( 'name',)
        js = ('js/tiny_mce/tiny_mce.js'),('js/tiny_mce/textareas.js') ,
        #js = ('js/xinha/init.js'),('js/xinha/htmlarea.js'),('js/xinha/description.js'),

