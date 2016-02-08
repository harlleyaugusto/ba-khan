# -*- encoding: utf-8 -*-
# -*- coding: utf-8 -*-
from django.shortcuts import render,HttpResponseRedirect,render_to_response, redirect, HttpResponse
from django.template.context import RequestContext
from bakhanapp.forms import AssesmentConfigForm,AssesmentForm
from django.contrib.auth import  login,authenticate,logout
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import auth
from django.db.models import Count

from django import template
from bakhanapp.models import Assesment_Skill
from bakhanapp.models import Administrator
from bakhanapp.models import Teacher

register = template.Library()

import json

# Create your views here.
@login_required()
def getAdministrators(request):
    print "###############################################################################"
    print request.user.email
    teacher = Teacher.objects.get(email=request.user.email)
    administrators = Administrator.objects.filter(id_institution=teacher.id_institution_id).order_by('name')
    print administrators
    return render_to_response('administrators.html', {'administrators': administrators}, context_instance=RequestContext(request))

@login_required()
def saveAdministrator(request):
    print "##################################  GUARDANDO  ##########################################"
    user = Teacher.objects.get(email=request.user.email) #el usuario que está logueado
    if request.is_ajax():
        if request.method == 'POST':
            json_str = json.loads(request.body)
            print "##################################  json_str  ##########################################"
            print json_str

            try:
                admin = Administrator.objects.get(kaid_administrator=json_str["adminName"])
                print "existe admin"
                if (json_str["adminPhone"]):
                    admin.phone=json_str["adminPhone"]
                else:
                    admin.phone=None
                if (json_str["adminEmail"]):
                    admin.email=json_str["adminEmail"]
                else:
                    admin.email=""
                admin.id_institution_id = user.id_institution_id
                admin.save()
                return HttpResponse("Cambios guardados correctamente")
            except:
                if (json_str["adminName"]):
                    admin = Administrator(name=json_str["adminName"])
                    if (json_str["adminPhone"]):
                        admin.phone=json_str["adminPhone"]
                    else:
                        admin.phone=None
                    if (json_str["adminEmail"]):
                        admin.email=json_str["adminEmail"]
                    else:
                        admin.email=""
                    admin.id_institution_id = user.id_institution_id
                    admin.kaid_administrator = json_str["adminName"]
                    admin.save()
                    return HttpResponse("Nuevo Administrador guardado correctamente")
                else:
                    return HttpResponse("Error al guardar")


    return HttpResponse("Error")

@login_required()
def deleteAdministrator(request):
    if request.is_ajax():
        if request.method == 'POST':
            json_str = json.loads(request.body)
            print "##################################  json_str  ##########################################"
            print json_str

            try:
                admin = Administrator.objects.get(kaid_administrator=json_str["adminName"])
                admin.delete()
                return HttpResponse("Administrador eliminado correctamente")
            except:
                return HttpResponse("Error")
    return HttpResponse("Error")