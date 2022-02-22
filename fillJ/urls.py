from . import views
from django.urls import path,include


urlpatterns = [
    path('', views.main, name='main'),
    path('unsub', views.unsub,name='unsub'),
    path('test/', views.index, name='index'),
    path('getpage/<int:jorn>/<int:page>/', views.getpage, name='getpage'),
    path('getpage/<int:jorn>/', views.getpage, name='getpage'),

    path('resiveTable',views.resiveTable,name="resiveTable")
]
#Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
