"""
URL configuration for rpadmin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
import datahub.views as dv
from datahub.views import *

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('accounts/login/', loginUI, name='login'),
    path('accounts/logout', logOutUser, name='log-out'),
    path('services', services, name='services'),
    path('fetch/services/', fetchServices, name='fetchServices'),
    path('service/add', addService, name='addservice'),
    path('service/edit/<int:id>', editService, name='edit-service'),
    path('service/delete/<int:id>', deleteService, name='delete-service'),
    path('law', law, name='law'),
    path('fetch/law/', fetchLaw, name='fetchLaw'),
    path('fetch/radio/', fetchRadio, name='fetchRadio'),
    path('radio', radio, name='radio'),
    path('helpdesk', helpdesk, name='helpdesk'),
    path('fetch/helpdesk/', fetchHelpdesk, name='fetchHelpdesk'),
    path('helpdesk/add', addHelpdesk, name="addhelpdesk"),
    path('helpdesk/edit/<int:id>', editHelpdesk, name='edit-helpdesk'), 
    path('helpdesk/delete/<int:id>', deleteHelpdesk, name='delete-helpdesk'),
    path('region', region, name='region'),
    path('region/add', addRegion, name='addregion'),
    path('region/edit/<int:id>', editRegion, name='edit-region'), 
    path('region/delete/<int:id>', deleteRegion, name='delete-region'), 
    path('district', district, name='district'),
    path('district/add', addDistrict, name='adddistrict'),
    path('district/edit/<int:id>', editDistrict, name='edit-district'), 
    path('district/delete/<int:id>', deleteDistrict, name='delete-district'),
    path('ps', ps, name='ps'),
    path('ps/add', addPs, name='addps'),
    path('ps/edit/<int:id>', editPs, name='edit-ps'), 
    path('ps/delete/<int:id>', deletePS, name='delete-ps'),
    path('sps', sps, name='sps'),
    path('sps/add', addSps, name='addsps'),
    path('sps/edit/<int:id>', editSPS, name='edit-sps'), 
    path('sps/delete/<int:id>', deleteSPS, name='delete-sps'),
    path('contact', contact, name='contact'),
    path('fetch/contact/', fetchContact, name='fetchContact'),
    path('contact/add', addContact, name='addcontact'),
    path('contact/edit/<int:id>', editContact, name='edit'), 
    path('contact/delete/<int:id>', deleteContact, name='delete-contact'), 
    path('api/update-location', updateLL, name='update-location'),
    path('getagent/', getAgent, name="getagent"),
    path('law/update', updateLaw, name='update-law'),
    path('radio/update', updateRadio, name='update-radio'),
    path('photos', getPhotos, name='get-photos'),
    path('photo/add', addPhoto, name='add-photo'), 
    path('photo/update/<int:id>', updatePhoto, name='update-photo'),
    path('photo/delete/<int:id>', deletePhoto, name='delete-photo'),
    path('news', getNews, name='news'),
    path('news/add', addNews, name='add-news'),
    path('news/update/<int:id>', updateNews, name='update-news'),
    path('news/delete/<int:id>', deleteNews, name='delete-news'),
    path('police/pending/', pendingPolice, name='pending-police'),
    path('police/approve/<int:id>', approvePolice, name='approve-police'),
    path('police/active/', activePolice, name='active-police'),
    path('police/activate/<int:id>', activatePolice, name='activate-police'),
    path('police/inactive/', inactivePolice, name='inactive-police'),
    path('police/inactivate/<int:id>', inactivatePolice, name='inactivate-police'),
    path('police/location/<int:id>', policeLocation, name='policeLocation'),
    path('users', users, name='users'),
    path('logs', logs, name='logs'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)