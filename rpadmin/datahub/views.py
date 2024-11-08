from collections import defaultdict
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, logout
from .models import *
from rest_framework.decorators import api_view
from account.models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from account.models import CustomUser, Logs

# Create your views here.

def loginUI(request, *args, **kwargs):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == "POST":
        phone = request.POST.get('phone')
        password = request.POST.get('pass')

        print(phone, password)

        user = authenticate(phone=phone, password=password)
        print(user)

        if user:
            login(request, user)

            return redirect('/')
        else:
            return redirect('login')

    return render(request, 'account/login.html')

def logOutUser(request, *args, **kwargs):

    logout(request)

    return redirect('/')

@login_required
def dashboard(request, *args, **kwargs):
    users = CustomUser.objects.filter(user_type='police')
    locations = list()
    for u in users:
        if u.lat and u.lon:
            locations.append(
                {
                    'lat': float(u.lat), 'lng': float(u.lon), 'name': u.name, 'phone': str(u.phone), 'thana': str(u.thana), 'designation': str(u.rank)
                }
            )

        context = {
            'loc': locations,
            'ln': len(locations)
        }

        print(locations)
    return render(request, 'datahub/dashboard.html', context)

# @login_required
def services(request, *args, **kwargs):
    svs = Service.objects.all()
    
    context = {
        'svs': svs
    }
    return render(request, 'datahub/services.html', context)

# @login_required
def fetchServices(request, *args, **kwargs):
    service = Service.objects.all()
    return JsonResponse({'services': list(service.values())})

@login_required
def addService(request, *args, **kwargs):
    if request.method == 'POST':
        name = request.POST.get('service')
        name_bn = request.POST.get('servicebn')
        
        svs = Service(name=name, name_bn=name_bn)
        svs.save()
        
        return redirect('/services')

    return render(request, 'datahub/addservice.html')

@login_required
def law(request, *args, **kwargs):
    l = Law.objects.first()
    
    context = {
        'l': l,
    }
    return render(request, 'datahub/law.html', context)

# @login_required
def fetchLaw(request, *args, **kwargs):
    lawPdf = Law.objects.first()

    return JsonResponse({'file': lawPdf.file.url})

# @login_required
def fetchRadio(request, *args, **kwargs):
    audio = Radio.objects.first()

    return JsonResponse({'audio': audio.file.url})

@login_required
def radio(request, *args, **kwargs):
    r = Radio.objects.first()
    
    context = {
        'r': r
    }
    return render(request, 'datahub/radio.html', context)

@login_required
def helpdesk(request, *args, **kwargs):
    hd = HelpDesk.objects.all()
    
    context = {
        'hd': hd,
    }
    
    return render(request, 'datahub/helpdesk.html', context)

# @login_required
def fetchHelpdesk(request, *args, **kwargs):
    helpdesk = HelpDesk.objects.all()
    
    return JsonResponse({'helpdesk': list(helpdesk.values())})

@login_required
def addHelpdesk(request, *args, **kwargs):
    if request.method == "POST":
        name = request.POST.get('hd')
        namebn = request.POST.get('hdbn')
        contact = request.POST.get('contact')
        
        hd = HelpDesk(name=name, name_bn=namebn, phone_number=contact)
        hd.save()
        
        return redirect('/helpdesk')
    
    return render(request, 'datahub/addhelpdesk.html')

# @login_required
def region(request, *args, **kwargs):
    reg = Region.objects.all()
    
    context = {
        'reg': reg,
    }
    return render(request, 'datahub/region.html', context)

@login_required
def addRegion(request, *args, **kwargs):
    
    if request.method == "POST":
        name = request.POST.get('region')
        namebn = request.POST.get('regionbn')
        sps = request.POST.getlist('sps')
        sds = request.POST.getlist('sdistrict')
        
        region = Region(name=name, name_bn=namebn)
        region.save()
        for i in sps:
            print(i)
            ps = PrimaryThana.objects.get(id=i)
            region.thanas.add(ps)
            
        for i in sds:
            print(i)
            ds = District.objects.get(id=i)
            region.districts.add(ds)
            
        return redirect('/region')
    
    ds = District.objects.all()
    ps = PrimaryThana.objects.all()
    
    context = {
        'ds': ds,
        'ps': ps
    }
    return render(request, 'datahub/addregion.html', context)

@login_required
def district(request, *args, **kwargs):
    ds = District.objects.all()
    
    context = {
        'ds': ds
    }
        
    return render(request, 'datahub/district.html', context)

@login_required
def addDistrict(request, *args, **kwargs):
    if request.method == "POST":
        name = request.POST.get('district')
        namebn = request.POST.get('districtbn')
        
        ds = District(name=name, name_bn=namebn)
        ds.save()
        
        return redirect('/district')
    
    return render(request, 'datahub/adddistrict.html')

@login_required
def ps(request, *args, **kwargs):
    ps = PrimaryThana.objects.all()
    
    context = {
        'ps': ps
    }
    return render(request, 'datahub/ps.html', context)

@login_required
def addPs(request, *args, **kwargs):
    if request.method == "POST":
        name = request.POST.get('ps')
        namebn = request.POST.get('psbn')
        ssps = request.POST.getlist('ssps')
        print(ssps)
        
        ps = PrimaryThana(name=name, name_bn=namebn)
        ps.save()
        for i in ssps:
            print(i)
            sps = Thana.objects.get(id=i)
            ps.thanas.add(sps)
        
        
        
        return redirect('/ps')
    
    sps = Thana.objects.all()
    context = {
        'sps': sps,
    }
    return render(request, 'datahub/addps.html', context)

@login_required
def sps(request, *args, **kwargs):
    sps = Thana.objects.all()
    
    context = {
        'sps': sps
    }
    
    return render(request, 'datahub/sps.html', context)

@login_required
def addSps(request, *args, **kwargs):
    if request.method == "POST":
        name = request.POST.get('sps')
        namebn = request.POST.get('spsbn')
        
        sps = Thana(name=name, name_bn=namebn)
        sps.save()
        
        return redirect('/sps')
    
    return render(request, 'datahub/addsps.html')

@login_required
def contact(request, *args, **kwargs):
    c = Contact.objects.all()
    
    context = {
        'c': c
    }
    return render(request, 'datahub/contact.html', context)

from django.http import JsonResponse
from .models import Contact

from collections import defaultdict
from django.http import JsonResponse
from .models import Contact, Thana

# @login_required
def fetchContact(request, *args, **kwargs):
    contacts = Contact.objects.all().select_related('thana')  # Correct ForeignKey
    grouped_contacts = defaultdict(list)

    for contact in contacts:
        thana_id = contact.thana.id  # Get the ID from the thana ForeignKey
        grouped_contacts[thana_id].append({
            'id': contact.id,
            'designation': contact.designation,
            'designation_bn': contact.designation_bn,
            'phone_number': contact.phone_number,
        })

    thanas = PrimaryThana.objects.all()
    thana_contacts = {
        thana.id: {
            'name': thana.name,
            'name_bn': thana.name_bn,
            'contacts': grouped_contacts[thana.id],
        }
        for thana in thanas
    }

    return JsonResponse({'thana_contacts': list(thana_contacts.values())})


@login_required
def addContact(request, *args, **kwargs):
    if request.method == "POST":
        name = request.POST.get('od')
        namebn = request.POST.get('odbn')
        contact = request.POST.get('contact')
        sps = request.POST.get('sps')
        ps = PrimaryThana.objects.get(id=sps)
        
        c = Contact(designation=name, designation_bn=namebn, phone_number=contact, thana=ps)
        c.save()
        
        return redirect('/contact')
    
    ps = PrimaryThana.objects.all()
    
    context = {
        'ps': ps
    }
    
    return render(request, 'datahub/addcontact.html', context)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateLL(request, *args, **kwargs):

    user = None
    try:
        data = json.loads(request.body)
        user = request.user
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        if latitude and longitude:
            
            if user:
                user.lat = latitude
                user.lon = longitude
                user.save()
                return JsonResponse({'status': 'Location updated'}, status=200)
            # Process the location data, for example, save it to the database
            print(f"New Location - Latitude: {latitude}, Longitude: {longitude}")
            return JsonResponse({'status': 'Invalid User'}, status=400)
        else:
            return JsonResponse({'status': 'Missing coordinates'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'Invalid request'}, status=400)


from django.db.models import F, Func, Value
from django.db.models import FloatField
from math import radians, cos, sin, sqrt, atan2
from geopy.distance import geodesic

# Haversine formula to calculate distance between two lat/lon points
@login_required
def haversine(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    print('h1', lon1, lat1, lon2, lat2)

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    print('c', c*r)
    return c * r

@login_required
def find_nearest_users(my_lat, my_lon):
    # Get all users
    users = CustomUser.objects.all()
    print('user', users)

    # Annotate each user with distance using Haversine formula
    users_with_distance = []
    for user in users:
        print("---users up ----------")
        if user.lat and user.lon and user.device_token and user.user_type=="police":
            print("logic ------- call",user.name)
            distance = haversine(my_lat, my_lon, float(user.lat), float(user.lon))
            users_with_distance.append({
                'user': user,
                'distance': distance
            })

    # Sort users based on distance and get the top 5 nearest users
    nearest_users = sorted(users_with_distance, key=lambda x: x['distance'])
    
    if nearest_users:
        return nearest_users[0]
    
    # if len(nearest_users) > 5:
    #     return nearest_users[:5]
    
    return None
from django.core import serializers
@csrf_exempt
@authentication_classes([])
@login_required
def getAgent(request, *args, **kwargs):
    if request.method == "POST":
        user = None
        try:
            data = json.loads(request.body)
            latitude = data.get('latitiude')
            longitude = data.get('longitude')
            latitude = float(latitude)
            longitude = float(longitude)
            
            print(latitude, longitude)
            
            if latitude and longitude:
                res = find_nearest_users(latitude, longitude)
                print('Final output => ', res)
                if res:
                    print(res['user'].email)
                    return JsonResponse({'email': res['user'].email, 'distance': str(round(res['distance'], 2)) + ' km'}, status=200)
                return JsonResponse({'status': 'No officer found nearby'}, status=200)
            else:
                return JsonResponse({'status': 'Missing coordinates'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'Invalid request'}, status=400)
    

@login_required
def deleteService(request, id):
    e = Service.objects.get(id=id)
    e.delete()

    return redirect('services')

@login_required
def deleteHelpdesk(request, id):
    e = HelpDesk.objects.get(id=id)
    e.delete()

    return redirect('helpdesk')

@login_required
def deleteDistrict(request, id):
    e = District.objects.get(id=id)
    e.delete()

    return redirect('district')

@login_required
def deleteSPS(request, id):
    e = Thana.objects.get(id=id)
    e.delete()

    return redirect('sps')

@login_required
def deletePS(request, id):
    e = PrimaryThana.objects.get(id=id)
    e.delete()

    return redirect('ps')

@login_required
def deleteRegion(request, id):
    e = Region.objects.get(id=id)
    e.delete()

    return redirect('region')

@login_required
def deleteContact(request, id):
    e = Contact.objects.get(id=id)
    e.delete()

    return redirect('contact')


@login_required
def editService(request, id):
    e = Service.objects.get(id=id)

    if request.method == 'POST':
        s = request.POST.get('service')
        sbn = request.POST.get('servicebn')

        e.name = s
        e.name_bn = sbn
        e.save()

        return redirect('services')

    context = {
        'e': e,
    }

    return render(request, 'datahub/editservice.html', context)

@login_required
def editHelpdesk(request, id):
    e = HelpDesk.objects.get(id=id)

    if request.method == 'POST':
        s = request.POST.get('hd')
        sbn = request.POST.get('hdbn')
        c = request.POST.get('contact')

        e.name = s
        e.name_bn = sbn
        e.phone_number = c
        e.save()

        return redirect('helpdesk')

    context = {
        'e': e,
    }

    return render(request, 'datahub/edithelpdesk.html', context)

@login_required
def editDistrict(request, id):
    e = District.objects.get(id=id)

    if request.method == 'POST':
        s = request.POST.get('district')
        sbn = request.POST.get('districtbn')

        e.name = s
        e.name_bn = sbn
        e.save()

        return redirect('district')

    context = {
        'e': e,
    }

    return render(request, 'datahub/editdistrict.html', context)

@login_required
def editSPS(request, id):
    e = Thana.objects.get(id=id)

    if request.method == 'POST':
        s = request.POST.get('sps')
        sbn = request.POST.get('spsbn')

        e.name = s
        e.name_bn = sbn
        e.save()

        return redirect('sps')

    context = {
        'e': e,
    }

    return render(request, 'datahub/editsps.html', context)

@login_required
def editPs(request, id):
    e = PrimaryThana.objects.get(id=id)

    if request.method == "POST":
        s = request.POST.get('ps')
        sbn = request.POST.get('psbn')
        ssps = request.POST.getlist('ssps')
        print(ssps)
        e.name = s
        e.name_bn = sbn
        e.thanas.clear()
        e.save()

        for i in ssps:
            print(i)
            sps = Thana.objects.get(id=i)
            print(sps)
            e.thanas.add(sps) 
        
        return redirect('ps')
            
    sps = Thana.objects.all()
    context = {
        'sps': sps,
        'e': e
    }
    return render(request, 'datahub/editps.html', context)


@login_required
def editRegion(request, id):
    e = Region.objects.get(id=id)

    if request.method == "POST":
        s = request.POST.get('region')
        sbn = request.POST.get('regionbn')
        sps = request.POST.getlist('sps')
        sds = request.POST.getlist('sdistrict')
        
        e.name = s
        e.name_bn = sbn
        e.districts.clear()
        e.thanas.clear()
        e.save()
        for i in sps:
            print(i)
            ps = PrimaryThana.objects.get(id=i)
            e.thanas.add(ps)
            
        for i in sds:
            print(i)
            ds = District.objects.get(id=i)
            e.districts.add(ds)
            
        return redirect('/region')
    
    ds = District.objects.all()
    ps = PrimaryThana.objects.all()
    
    context = {
        'ds': ds,
        'ps': ps,
        'e': e,
    }
    return render(request, 'datahub/editregion.html', context)

@login_required
def editContact(request, id):
    e = Contact.objects.get(id=id)

    if request.method == "POST":
        s = request.POST.get('od')
        sbn = request.POST.get('odbn')
        c = request.POST.get('contact')
        sps = request.POST.get('sps')
        ps = PrimaryThana.objects.get(id=sps)
        
        e.designation = s
        e.designation_bn = sbn
        e.phone_number = c
        e.thana = ps
        e.save()
        
        return redirect('/contact')
    
    ps = PrimaryThana.objects.all()
    
    context = {
        'ps': ps,
        'e': e,
    }
    
    return render(request, 'datahub/editcontact.html', context)

@login_required
def updateLaw(request, *args, **kwargs):
    e = Law.objects.all().first()

    if request.method == "POST":
        s = request.FILES.get('file')

        e.file = s
        e.save()

        return redirect('law')
    
    return render(request, 'datahub/editlaw.html')


@login_required
def updateRadio(request, *args, **kwargs):
    e = Radio.objects.all().first()

    if request.method == "POST":
        s = request.FILES.get('file')

        e.file = s
        e.save()

        return redirect('radio')
    
    return render(request, 'datahub/editradio.html')

@login_required
def getPhotos(request, *args, **kwargs):
    l = Gallary.objects.all()

    context = {
        'photos': l
    }

    return render(request, 'datahub/photo.html', context)

@login_required
def addPhoto(request, *args, **kwargs):

    if request.method == "POST":
        s = request.FILES.get('file')

        e = Gallary(image=s, title='photo', title_bn='photo')
        e.save()

        return redirect('/photos')

    return render(request, 'datahub/addphoto.html')

@login_required
def updatePhoto(request, id):
    e = Gallary.objects.get(id=id)

    if request.method == "POST":
        s = request.FILES.get('file')

        e.image = s
        e.save()

        return redirect('/photos')
    
    context = {
        'e': e
    }

    return render(request, 'datahub/editphoto.html', context)

@login_required
def deletePhoto(request, id):
    e = Gallary.objects.get(id=id)

    e.delete()

    return redirect('/photos')

@login_required
def getNews(request, *args, **kwargs):
    l = News.objects.all()

    context = {

        'news': l
    }

    return render(request, 'datahub/news.html', context)


@login_required
def deleteNews(request, id):
    e = News.objects.get(id=id)

    e.delete()

    return redirect('/news')


@login_required
def addNews(request, *args, **kwargs):

    if request.method == "POST":
        s = request.POST.get('title')
        sbn = request.POST.get('titlebn')
        u = request.POST.get('url')
        t = request.FILES.get('file')

        n = News(title=s, title_bn=sbn, url=u, thumbnail=t)
        n.save()

        return redirect('/news')

    return render(request, 'datahub/addnews.html')

@login_required
def updateNews(request, id):
    e = News.objects.get(id=id)

    if request.method == "POST":
        s = request.POST.get('title')
        sbn = request.POST.get('titlebn')
        u = request.POST.get('url')
        t = request.FILES.get('file')

        e.title = s
        e.title_bn = sbn
        e.url = u

        if t:
            e.thumbnail = t
        e.save()

        return redirect('/news')
    
    context = {
        'e': e
    }

    return render(request, 'datahub/editnews.html', context)

@login_required
def users(request, *args, **kwargs):
    user = CustomUser.objects.filter(user_type='normal')

    context = {
        'police': user
    }

    return render(request, 'datahub/users.html', context)

@login_required
def pendingPolice(request, *args, **kwargs):
    user = CustomUser.objects.filter(user_type='police', is_staff=False)

    context = {
        'police': user
    }

    return render(request, 'datahub/pendingpolice.html', context)

@login_required
def approvePolice(request, id):
    user = CustomUser.objects.get(id=id)
    user.is_staff = True
    user.is_active = True
    user.save()

    return redirect('/police/active/')

@login_required
def activePolice(request, *args, **kwargs):
    user = CustomUser.objects.filter(user_type='police', is_active=True, is_staff=True)

    context = {
        'police': user
    }

    return render(request, 'datahub/activepolice.html', context)

@login_required
def activatePolice(request, id):
    user = CustomUser.objects.get(id=id)
    user.is_active = True
    user.save()

    return redirect('/police/active/')

@login_required
def inactivePolice(request, *args, **kwargs):
    user = CustomUser.objects.filter(user_type='police', is_active=False)

    context = {
        'police': user
    }

    return render(request, 'datahub/inactivepolice.html', context)

@login_required
def inactivatePolice(request, id):
    user = CustomUser.objects.get(id=id)
    user.is_active = False
    user.save()

    return redirect('/police/inactive/')

@login_required
def policeLocation(request, id):
    user = CustomUser.objects.get(id=id)
    
    context = {
        'name': user.name,
        'lat': float(user.lat),
        'lng': float(user.lon),
        'phone': str(user.phone),
        'thana': user.thana,
        'des': user.rank
    }

    return render(request, 'datahub/plocation.html', context)

@login_required
def logs(request, *args, **kwargs):
    lgs = Logs.objects.all()

    context = {
        'logs': lgs
    }

    return render(request, 'datahub/logs.html', context)