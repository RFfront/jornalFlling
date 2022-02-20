from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import os
from . import jornal
from pprint import pprint
import json
from pathlib import Path
async_mode = "threading"

import os

from django.http import HttpResponse
import socketio

basedir = os.path.dirname(os.path.realpath(__file__))
sio = socketio.Server(async_mode=async_mode)
thread = "None"
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

def index(request):
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)
    return HttpResponse(render(request, "soctest.html"))


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        sio.sleep(10)
        count += 1
        sio.emit('my_response', {'data': 'Server generated event'},
                 namespace='/test')


@sio.event
def my_event(sid, message):
    sio.emit('my_response', {'data': message['data']}, room=sid)


@sio.event
def my_broadcast_event(sid, message):
    sio.emit('my_response', {'data': message['data']})


@sio.event
def join(sid, message):
    sio.enter_room(sid, message['room'])
    sio.emit('my_response', {'data': 'Entered room: ' + message['room']},
             room=sid)


@sio.event
def leave(sid, message):
    sio.leave_room(sid, message['room'])
    sio.emit('my_response', {'data': 'Left room: ' + message['room']},
             room=sid)


@sio.event
def close_room(sid, message):
    sio.emit('my_response',
             {'data': 'Room ' + message['room'] + ' is closing.'},
             room=message['room'])
    sio.close_room(message['room'])


@sio.event
def my_room_event(sid, message):
    sio.emit('my_response', {'data': message['data']}, room=message['room'])


@sio.event
def disconnect_request(sid):
    sio.disconnect(sid)


@sio.event
def connect(sid, environ):
    sio.emit('my_response', {'data': 'Connected', 'count': 0}, room=sid)


@sio.event
def disconnect(sid):
    print('Client disconnected')
