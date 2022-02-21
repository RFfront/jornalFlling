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
sio = socketio.Server(async_mode=async_mode,ping_interval=300)
thread = "None"
def jornalStorage():
    return [jornal.Journal.fromFile(pat) for pat in jornal.module_dir.glob("*.Jornl")]
pprint(jornalStorage())

def main(request):
    return render(request, 'mnfl.html',{"jornalStorage":{i:el.groupname for i,el in enumerate(jornalStorage())} })

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required
def getpage(request,jorn,page=None):
    # current_user = request.user
    # print(current_user)
    joSto=jornalStorage()
    if page ==None:
        return render(request, 'pageslist.html',{"Pages":{i:el.discName for i,el in enumerate(joSto[jorn].pages)}  })
    dates,di=joSto[jorn].view(page)
    context = {"dates":dates,"di":di,"discName":joSto[jorn].pages[page].discName}
    return render(request, 'barrak.html', context)

@login_required
def resiveTable(request):
    if request.method == "POST":
        if is_ajax(request):
            jorn,page =json.loads(request.POST.dict()["params"])
            loc=getloc()
            if loc.get(request.POST.dict()["sid"],None) == [jorn,page]:
                table=request.POST.dict()["table"]
                table=json.loads(table)
                joSto=jornalStorage()

                joSto[jorn].pages[page].loadFromSite(table[0],table[1:])
                joSto[jorn].saveToFile()
                return HttpResponse(1)
            else:
                sio.emit('server_alert',
                 'Кто-то другой уже изменяет эту страницу, подождите.',
                  room=request.POST.dict()["sid"])

                return HttpResponse(0)

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
        sio.emit('server_response', {'data': 'Server generated event'},
                 namespace='/test')
def getloc()->dict:
    dt=0
    with open("_.loc","r",encoding="utf-8")as f:
        dt=json.load(f)
    return dt

def writeToloc(sid,lock):
    dt=0
    with open("_.loc","r",encoding="utf-8")as f:
        dt=json.load(f)
    if lock not in dt.values():
        dt[sid]=lock
        with open("_.loc","w",encoding="utf-8")as f:
            json.dump(dt, f,ensure_ascii=False)
def delFrloc(sid):
    dt=0
    with open("_.loc","r",encoding="utf-8")as f:
        dt=json.load(f)
    if dt.pop(sid,None)!=None:
        # dt[sid]=lock
        with open("_.loc","w",encoding="utf-8")as f:
            json.dump(dt, f,ensure_ascii=False)
@sio.event
def broadcastToServer(sid, message):
    if "lock" in message:
        # print(get_current_user())
        writeToloc(sid, message["lock"])
    print(sid,message)
    # sio.emit('server_response', {'data': message['data']+sid}, room=sid)


@sio.event
def broadcastToAll(sid, message):
    sio.emit('server_response', {'data': message['data']})

@sio.event
def disconnect_request(sid):
    sio.disconnect(sid)


@sio.event
def connect(sid, environ):
    print(f"\n{sid} Connected\n",)

    sio.emit('sendSid', {'sid':sid}, room=sid)


@sio.event
def disconnect(sid):
    delFrloc(sid)
    sio.emit('updateConnect')
    print(sid,'\nClient disconnected\n')

# @sio.event
# def join(sid, message):
#     sio.enter_room(sid, message['room'])
#     sio.emit('server_response', {'data': 'Entered room: ' + message['room']},
#              room=sid)
#
#
# @sio.event
# def leave(sid, message):
#     sio.leave_room(sid, message['room'])
#     sio.emit('server_response', {'data': 'Left room: ' + message['room']},
#              room=sid)
#
#
# @sio.event
# def close_room(sid, message):
#     sio.emit('server_response',
#              {'data': 'Room ' + message['room'] + ' is closing.'},
#              room=message['room'])
#     sio.close_room(message['room'])
#
#
# @sio.event
# def my_room_event(sid, message):
#     sio.emit('server_response', {'data': message['data']}, room=message['room'])
#
