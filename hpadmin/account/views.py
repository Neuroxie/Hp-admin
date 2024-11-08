from datetime import timedelta
import json
from django.contrib.auth import authenticate,login
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from .models import CustomUser, Logs
from .utils import send_verification_email
from .token_generator import account_activation_token
from .decorators import user_type_required
from django.contrib.sessions.models import Session
from django.utils.timezone import now

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str 
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_POST

from django.utils import timezone
from datahub.models import Gallary, Ticket, Document
import firebase_admin
from firebase_admin import credentials, messaging
import string,random
from phonenumber_field.phonenumber import PhoneNumber
from django.db.models.functions import Cast
from django.db.models import CharField
from django.core.serializers.json import DjangoJSONEncoder

User = get_user_model()

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def register_normal_user(request):
    if request.method == 'POST':
        data = request.data
        email = request.data.get('email', '').strip().lower() if data.get('email') else ''
        phone = request.data.get('phone', '').strip().lower() if data.get('phone') else ''
        
        # Check if user already exists
        if email and  CustomUser.objects.filter(email=email).exists():
            return Response({'error': 'A user with this email already exists.'}, status=HTTP_400_BAD_REQUEST)
        elif CustomUser.objects.filter(phone=phone).exists():
            return Response({'error': 'A user with this phone no already exists.'}, status=HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create_user(
            email= None if email=="" else email,
            name=data['name'],
            phone=data['phone'],
            user_type='normal',
            password=data['password']
        )

        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.is_active = True  # Set user as inactive until email verification
        user.save()

        # Send Email Verification
        send_verification_email(user)

        return Response({'message': 'Please confirm your email to complete registration'}, status=HTTP_201_CREATED)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def register_police_user(request):
    if request.method == 'POST':
        data = request.data
        print(data)
        email = request.data.get('email', '').strip().lower() if data.get('email') else ''
        phone = request.data.get('phone', '').strip().lower() if data.get('phone') else ''
        bp = request.data.get('bp_no', '').strip().lower() if data.get('bp_no') else ''

        # Check if user already exists
        if email and  CustomUser.objects.filter(email=email).exists():
            return Response({'error': 'A user with this email already exists.'}, status=HTTP_400_BAD_REQUEST)
        elif CustomUser.objects.filter(phone=phone).exists():
            return Response({'error': 'A user with this phone no already exists.'}, status=HTTP_400_BAD_REQUEST)
        elif bp and CustomUser.objects.filter(bp=bp).exists():
            return Response({'error': 'This Bangladesh police no already exists.'}, status=HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.create_user(
            email=None if email=="" else email,
            name=data['name'],
            phone=data['phone'],
            bp=data['bp_no'],
            user_type='police',
            password=data['password']
        )
        user.is_active = False  # Set user as inactive until email verification
        user.save()

        # Send Email Verification
        send_verification_email(user)

        return Response({'message': 'Please confirm your email to complete registration'}, status=HTTP_201_CREATED)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def login_normal_user(request):
    phone = request.data.get('phone', '').strip().lower()

    password = request.data.get('password')

    isNormal = CustomUser.objects.filter(phone=phone,user_type='normal')

    if not isNormal:
        return Response({'error': 'This is not a user account!'}, status=HTTP_400_BAD_REQUEST)
    else:
        email = isNormal[0].email
    
    user = authenticate(phone=phone, password=password, user_type='normal')

    inActiveUsers = CustomUser.objects.filter(phone=phone, is_active=False)
    if inActiveUsers.exists():
        return Response({'error': 'Please verify your email before logging in.'}, status=HTTP_400_BAD_REQUEST)
    
    if user is None:
        return Response({'error': 'Invalid Credentials'}, status=HTTP_400_BAD_REQUEST)
    
    Token.objects.filter(user=user).delete()
    
    token,_ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def login_police_user(request):
    phone = request.data.get('phone', '').strip().lower()

    password = request.data.get('password')

    isPolice = CustomUser.objects.filter(phone=phone,user_type='police')
    print(isPolice,phone)
    if not isPolice:
        return Response({'error': 'This is not a police account!'}, status=HTTP_400_BAD_REQUEST)
    else:
        email = isPolice[0].email
    
    user = authenticate(phone=phone, password=password, user_type='police')

    inActiveUsers = CustomUser.objects.filter(phone=phone, is_active=False)
    if inActiveUsers.exists():
        return Response({'error': "Your account isn't verified yet."}, status=HTTP_400_BAD_REQUEST)
    
    if user is None:
        return Response({'error': 'Invalid Credentials'}, status=HTTP_400_BAD_REQUEST)
    
    Token.objects.filter(user=user).delete()
    
    token,_ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=HTTP_200_OK)

def check_token(request):
    token = request.META.get('HTTP_AUTHORIZATION', '').split('Token ')[-1]
    # print(token)
    existing = Token.objects.filter(key=token).exists()

    if existing:
        return JsonResponse({'is_valid': True}, status=200)
    else:
        return JsonResponse({'is_valid': False}, status=401)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_device_token(request):
    # Load JSON data from the request body
    data = json.loads(request.body)
    device_token = data.get('device_token')

    if not device_token:
        return JsonResponse({'error': 'device_token is required'}, status=400)

    user = request.user
    # Update the device token for the authenticated user
    user.device_token = device_token
    user.save()

    return JsonResponse({'success': 'FCM token updated successfully'}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_type_required('normal')
def normal_user_route(request):
    return Response({'message': 'Welcome, Normal User!'}, status=HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_type_required('police')
def police_user_route(request):
    return Response({'message': 'Welcome, Police User!'}, status=HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        context = {'message': 'Thank you for confirming your email!'}
        return render(request, 'account/activation_success.html', context)
    else:
        context = {'message': 'Activation link is invalid!'}
        return render(request, 'account/activation_failed.html', context)


@csrf_exempt
@require_POST
def send_otp(request):
    data = json.loads(request.body)
    email = data.get('email')
    
    User = get_user_model()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    otp = user.generate_otp()
    send_mail(
        'Your OTP Code',
        f'Your OTP code is: {otp}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    
    return JsonResponse({'message': 'OTP sent successfully'}, status=200)

@csrf_exempt
@require_POST
def verify_otp(request):
    data = json.loads(request.body)
    email = data.get('email')
    otp = data.get('otp')
    
    User = get_user_model()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    if user.otp != otp or user.otp_expires_at < timezone.now():
        return JsonResponse({'error': 'Invalid or expired OTP'}, status=400)
    
    # user.otp = None
    # user.otp_expires_at = None
    user.save()
    
    return JsonResponse({'message': 'OTP verified successfully'}, status=200)
@csrf_exempt
@require_POST
def reset_password(request):
    data = json.loads(request.body)
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')
    
    User = get_user_model()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    if user.otp is not None and user.otp_expires_at >= timezone.now() and user.otp == otp:
        user.set_password(new_password)
        user.otp = None
        user.otp_expires_at = None
        user.save()
        return JsonResponse({'message': 'Password reset successfully'}, status=200)
    else:
        return JsonResponse({'error': 'OTP invalid or expired'}, status=400)

# API Calls 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getName(request):
    return Response({'name': request.user.name,"email":request.user.email}, status=HTTP_200_OK)


# Initialize the app with your Firebase credentials
cred = credentials.Certificate("config/adminsdk.json")
firebase_admin.initialize_app(cred)

def send_sos_notification(tokenID,channelID,police,user,latitude,longitude,PFCM,UFCM,distance):
    message_title = "SOS Call"
    message_body = f"Incoming SOS call from {user.name}"
    
    # Create a message
    message = messaging.Message(
        # notification=messaging.Notification(
        #     # title=message_title,
        #     # body=message_body,
        # ),
        data={
            "type": "sos_call",
            "channelId": channelID,
            "lat": str(latitude),
            "lon": str(longitude),
            "plat": str(police.lat),
            "plon": str(police.lon),
            "distance": str("{:.2f}".format(distance)),
            "PFCM": PFCM,
            "UFCM":UFCM
        },
        token=tokenID
    )
    # Send the message
    # response = messaging.send(message)
    # return response
    try:
        response = messaging.send(message)
        return response
    except messaging.UnregisteredError as e:
        # Handle the token being unregistered (e.g., remove from database)
        print("Unregistered token:", e)
        return e

def debugView(request):
    # send_sos_notification()
    user = CustomUser.objects.get(email="police@gmail.com")
    channel_id = user.email
    device_token = user.device_token
    send_sos_notification(device_token,channel_id)
    return JsonResponse({'message': 'Hello, world!'}, status=200)

from django.db.models import F, Func, Value
from django.db.models import FloatField
from math import radians, cos, sin, sqrt, atan2
from geopy.distance import geodesic

def haversine(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # print('h1', lon1, lat1, lon2, lat2)

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    # print('c', c*r)
    return c * r

def find_nearest_users(my_lat, my_lon):
    # Get all users
    users = CustomUser.objects.all()

    # Annotate each user with distance using Haversine formula
    users_with_distance = []
    for user in users:
        if user.lat and user.lon and user.is_on_duty and user.device_token and user.user_type == "police":
            distance = haversine(my_lat, my_lon, float(user.lat), float(user.lon))
            users_with_distance.append({
                'user': user,
                'distance': distance
            })

    # Sort users based on distance and get the top 5 nearest users
    nearest_users = sorted(users_with_distance, key=lambda x: x['distance'])
    
    if len(nearest_users)>=2:
        return nearest_users[:2]
    elif len(nearest_users)==1:
        return [nearest_users[0]]
    
    # if len(nearest_users) > 5:
    #     return nearest_users[:5]
    
    return None

def find_that_nearest_user_distance(my_lat, my_lon,PFCM):
    # Get all users
    user = CustomUser.objects.filter(device_token=PFCM)
    if not user:
        return None
    else:
        user = user[0]
    # print(my_lat)
    # print(my_lon)
    # print(user)
    # print(user.lat,user.lon)
    # Annotate each user with distance using Haversine formula
    if user.lat and user.lon and user.is_on_duty and user.device_token and user.user_type == "police":
        return haversine(my_lat, my_lon, float(user.lat), float(user.lon))
    else:
        return None


def generate_channel_id(length=12):
    characters = string.ascii_letters + string.digits
    channel_id = ''.join(random.choice(characters) for _ in range(length))
    return channel_id

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_channel_id(request):
    data = json.loads(request.body)
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    latitude = float(latitude)
    longitude = float(longitude)
    if not latitude or not longitude:
        return JsonResponse({'error': 'Latitude and longitude are required.'}, status=400)

    policeDICT = find_nearest_users(latitude, longitude)
    # print(policeDICT)
    if policeDICT:
        if len(policeDICT)==1:
            police = policeDICT[0]['user']
            second_police = None
            policeDistance = policeDICT[0]['distance']
        else:
            police =  policeDICT[0]['user']  
            policeDistance = policeDICT[0]['distance']
            second_police = policeDICT[1]['user']
        channel_id = generate_channel_id()
        # channel_id = police.email
        device_token = police.device_token
        PFCM = police.device_token
        UFCM = request.user.device_token
        response = send_sos_notification(device_token,channel_id,police,request.user,latitude,longitude,PFCM,UFCM,policeDistance)

        sp_dt = second_police
        # print("--------------------------"*10)
        # print(response)
        Logs.objects.create(
            user=request.user,
            police=police,
            time=timezone.now(),
            user_lat=str(latitude),
            user_lon=str(longitude),
            police_lat=police.lat,
            police_lon=police.lon
        )
        print({
            'channel_id': channel_id,
            'lat':str(latitude),
            'lon':str(longitude),
            'plat':str(police.lat),
            'plon':str(police.lon),
            'PFCM':PFCM,
            'UFCM':UFCM,
            'pname':police.name,
            'distance':str("{:.2f}".format(policeDistance)),
            'pass':second_police.device_token if sp_dt else "NA"
        })
        return JsonResponse({
            'channel_id': channel_id,
            'lat':str(latitude),
            'lon':str(longitude),
            'plat':str(police.lat),
            'plon':str(police.lon),
            'PFCM':PFCM,
            'UFCM':UFCM,
            'pname':police.name,
            'distance':str("{:.2f}".format(policeDistance)),
            'second_police_dt':second_police.device_token if sp_dt else "NA"
        })
    
    return JsonResponse({'status': 'No user found'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def second_police_call(request):
    print("SECOND CALL")
    data = json.loads(request.body)
    PFCM = data.get('PFCM')
    UFCM = data.get('UFCM')

    latitude = data.get('latitude')
    longitude = data.get('longitude')

    policeDistance = find_that_nearest_user_distance(float(latitude), float(longitude),PFCM)
    police = CustomUser.objects.filter(device_token=PFCM)[0]
    channel_id = generate_channel_id()
    send_sos_notification(PFCM,channel_id,police,request.user,latitude,longitude,PFCM,UFCM,policeDistance)
    Logs.objects.create(
            user=request.user,
            police=police,
            time=timezone.now(),
            user_lat=str(latitude),
            user_lon=str(longitude),
            police_lat=police.lat,
            police_lon=police.lon
        )
    print({
            'channel_id': channel_id,
            'lat':str(latitude),
            'lon':str(longitude),
            'plat':str(police.lat),
            'plon':str(police.lon),
            'PFCM':PFCM,
            'UFCM':UFCM,
            'pname':police.name,
            'distance':str("{:.2f}".format(policeDistance)),
            'pass':"NA"
        })
    return JsonResponse({
            'channel_id': channel_id,
            'lat':str(latitude),
            'lon':str(longitude),
            'plat':str(police.lat),
            'plon':str(police.lon),
            'PFCM':PFCM,
            'UFCM':UFCM,
            'pname':police.name,
            'distance':str("{:.2f}".format(policeDistance)),
            'second_police_dt':"NA"
    })

def leave_channel(tokenID):
    message_title = "SOS Call Cancelled"
    message_body = f"Call Cancelled"
    
    # Create a message
    message = messaging.Message(
        notification=messaging.Notification(
            title=message_title,
            body=message_body,
        ),
        data={
            "type": "call_ended",
        },
        token=tokenID
    )
    
    response = messaging.send(message)
    return response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def call_ended(request):
    data = json.loads(request.body)
    PFCM = data.get('PFCM')
    UFCM = data.get('UFCM')

    leave_channel(PFCM)
    leave_channel(UFCM)

    return JsonResponse({"status":"call cancelled"},status=200)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_logs(request):
    user = request.user
    logs = Logs.objects.filter(user=user).order_by('-time').values(
        'id', 'police__name', 'police__phone', 'time', 'user_lat', 'user_lon', 'police_lat', 'police_lon', 'status'
    )

    logs_list = list(logs)
    
    # Convert phone numbers to string
    for log in logs_list:
        police_phone = log.get('police__phone')
        if isinstance(police_phone, PhoneNumber):
            log['police__phone'] = str(police_phone)  # Convert to string

    return JsonResponse(logs_list, safe=False, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_police_logs(request):
    user = request.user
    logs = Logs.objects.filter(police=user).order_by('-time').annotate(
        user__phone=Cast('user__phone', CharField())
    ).values(
        'id', 'user__name', 'user__phone', 'time', 'user_lat', 'user_lon', 'police_lat', 'police_lon', 'status'
    )

    print(logs)
    return JsonResponse(list(logs), safe=False, status=200, encoder=DjangoJSONEncoder)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_duty_status(request):
    user = request.user
    if user:
        status = user.is_on_duty
        # print('Status.......', status)
        return JsonResponse({'status': status}, status=200)
        
    return JsonResponse({'message': 'No user found!'}, status=400)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_duty_status(request):
    user = request.user
    if user:
        data = json.loads(request.body)
        status = data.get('on_duty')
        user.is_on_duty = status
        user.save()
        return JsonResponse({'status': status}, status=200)
    return JsonResponse({'message': 'No user found!'}, status=400)

@api_view(['get'])
@permission_classes([IsAuthenticated])
def getSettings(request, *args, **kwargs):
    user = request.user
    return Response({'rank': user.rank, 'bp': user.bp, 'thana': user.thana, 'profile_picture': None if not user.profile_picture else user.profile_picture.url, 'name': user.name,"email":"" if user.email==None else user.email, 'phone':str(user.phone), 'dob': str(user.dob), 'address': user.address, 'nid': user.nid, 'district': user.district, 'profession': user.profession}, status=HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateSettings(request):
    try:
        user = request.user
        data = request.data
        print(data)
        phone = data.get('phone')
        email = data.get('email')
        doesExist = CustomUser.objects.filter(phone=phone).first()
        if email and  CustomUser.objects.filter(email=email).exists() and user.email != email:
            return Response({'error': 'A user with this email already exists.'}, status=HTTP_400_BAD_REQUEST)
        elif CustomUser.objects.filter(phone=phone).exists() and user.phone != phone:
            return Response({'error': 'A user with this phone no already exists.'}, status=HTTP_400_BAD_REQUEST)
        elif doesExist and phone!=str(doesExist.phone):
            print('lol error here')
            return Response({'message': 'Phone no already exist!'}, status=400)
        elif user:
            status = data.get('on_duty')
            user.name = data.get('name')
            if email: 
                user.email = data.get('email')
            user.phone = data.get('phone')
            if data.get('dob') and data.get('dob') != 'None':
                user.dob = data.get('dob')
            user.address = data.get('address')
            user.nid = data.get('nid')
            user.district = data.get('district')
            user.profession = data.get('profession')

            if data.get('password'):
                user.set_password(data.get('password'))

            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']

            try:
                if data.get('thana'):
                    user.thana = data.get('thana')

                if data.get('rank') :
                    user.rank = data.get('rank')

                if data.get('bp'):
                    user.bp = data.get('bp')
            except:
                pass

            user.save()
        return Response({'message': 'Settings updated Successfully!'}, status=HTTP_200_OK)        
    except Exception as e:
        print(e)
        return Response({'message': 'Failed to update Settings!'}, status=400)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProfilePicture(request):
    try:
        user = request.user
        profile_picture = user.profile_picture
        if profile_picture:
            profile_picture_url = request.build_absolute_uri(profile_picture.url)
            print(profile_picture_url)
            return Response({'profile_picture_url': profile_picture_url})
        else:
            return Response({'profile_picture_url': None})
    except:
        return Response({'profile_picture_url': None})

@api_view(['GET'])  # Change to POST if you're updating the log
@permission_classes([IsAuthenticated])
def updateLog(request, status, id):
    try:
        log = Logs.objects.get(id=id)
        if status == "accept":
            log.status = 'Accepted'
            log.save()
            return Response({'message': 'Log Updated'}, status=200)
        elif status == "reject":
            log.status = 'Rejected'
            log.save()
            return Response({'message': 'Log Updated'}, status=200)
        elif status == "complete":
            log.status = 'Completed'
            log.save()
            return Response({'message': 'Log Updated'}, status=200)
        else:
            return Response({'message': 'Invalid status provided!'}, status=400)
    except Logs.DoesNotExist:
        return Response({'message': 'Log not found!'}, status=404)
    except Exception as e:
        return Response({'message': str(e)}, status=500)
        
@api_view(['GET'])  # Change to POST if you're updating the log
@permission_classes([IsAuthenticated])
def getGallary(request, *args, **kwargs):
    gallary = Gallary.objects.all()
    
    # Create a list of image URLs
    imglist = [i.image.url for i in gallary]
    # Return a JSON response
    return JsonResponse({'images': imglist}, safe=False)

from datahub.models import News
@api_view(['GET'])  # Change to POST if you're updating the log
@permission_classes([IsAuthenticated])
def getNews(request, *args, **kwargs):
    news = News.objects.all().order_by('-updated_at')[:3]
    
    news_data = [
        {
            "title": news.title,
            "url": news.url,
            "thumbnail": news.thumbnail.url,  # Include other fields as needed
            "updated_at": news.updated_at,
        }
        for news in news
    ]
    # print(news_data)
    return JsonResponse({'news': news_data}, safe=False)

@api_view(['GET'])  # Change to POST if you're updating the log
@permission_classes([IsAuthenticated])
def allNews(request, *args, **kwargs):
    news = News.objects.all().order_by('-updated_at')
    
    news_data = [
        {
            "title": news.title,
            "url": news.url,
            "thumbnail": news.thumbnail.url,  # Include other fields as needed
            "updated_at": news.updated_at,
        }
        for news in news
    ]
    # print(news_data)
    return JsonResponse({'news': news_data}, safe=False)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_complaint(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        documents = request.FILES.getlist('attachments[]')

        # Basic validation
        if not subject or not message:
            return JsonResponse({'error': 'Subject and message must be filled.'}, status=400)

        # Create a new Ticket instance
        ticket = Ticket(user=request.user, subject=subject, message=message)
        ticket.save()  # Save the ticket first

        # Handle file uploads
        for document in documents:
            Document.objects.create(ticket=ticket, file=document)

        return JsonResponse({'success': 'Complaint submitted successfully.'}, status=200)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

