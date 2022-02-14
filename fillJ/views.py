from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import os
from . import jornal
from pprint import pprint
import json
from pathlib import Path
jornalStorage=[jornal.Journal.fromFile(pat) for pat in jornal.module_dir.glob("*.Jornl")]
pprint(jornalStorage)

def main(request):
    return render(request, 'mnfl.html',{"jornalStorage":{i:el.groupname for i,el in enumerate(jornalStorage)} })

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required
def getpage(request,jorn,page=None):
    if page ==None:
        return render(request, 'pageslist.html',{"Pages":{i:el.discName for i,el in enumerate(jornalStorage[jorn].pages)}  })
    dates,di=jornalStorage[jorn].view(page)
    context = {"dates":dates,"di":di,"discName":jornalStorage[jorn].pages[page].discName}
    return render(request, 'barrak.html', context)

@login_required
def resiveTable(request):
    if request.method == "POST":
        if is_ajax(request):
            table=request.POST.dict()["table"]
            jorn,page =[int(i) for i in request.POST.dict()["params"].split("/")[-3:-1]]
            table=json.loads(table)
            jornalStorage[jorn].pages[page].loadFromSite(table[0],table[1:])
            jornalStorage[jorn].saveToFile()
            return HttpResponse("1")
