from . import views
from django.urls import path,include


urlpatterns = [
path('', views.main, name='main'),
    path('getpage/', views.getpage, name='getpage'),
    path('getpage/<int:id>/', views.getpage, name='getpage'),

    path('resiveTable',views.resiveTable,name="resiveTable")
]
#Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
