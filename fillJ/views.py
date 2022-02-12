from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import os
from . import jornal
from pprint import pprint
import json
from pathlib import Path
jornalStorage=[jornal.fromFile(pat) for pat in jornal.module_dir.glob("*/*.Jornl")
# v=jornal.testt()
def main(request):
    return render(request, 'mnfl.html')

@login_required
def getpage(request,id=0):
    dates,di=v.view(id)
    context ={"dates":dates,"di":di,"discName":v.pages[id].discName}
    return render(request, 'barrak.html', context)

@login_required
def resiveTable(request):
    if request.method == "POST":
        if request.is_ajax():
            k=request.POST.dict()["table"]
            k=json.loads(k)
            pprint(k)
            v.pages[0].loadFromSite(k[0],k[1:])
            return HttpResponse("1")
