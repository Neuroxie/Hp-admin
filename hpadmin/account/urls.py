from django.urls import path
from .views import check_token, debugView, get_police_logs, get_user_logs, login_normal_user, login_police_user, register_normal_user, register_police_user, normal_user_route, police_user_route, activate, reset_password, send_otp, update_device_token, verify_otp, get_duty_status, update_duty_status
from .views import getName,get_channel_id,call_ended,second_police_call, updateSettings, updateLog, getSettings, getGallary, getNews, submit_complaint, allNews,getProfilePicture
from datahub.views import loginUI

urlpatterns = [
    path('register/normal/', register_normal_user, name='register_normal_user'),
    path('register/police/', register_police_user, name='register_police_user'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    # path('login/', login_user, name='login'),
    path('login_as_normal/', login_normal_user, name='login-normal'),
    path('login_as_police/', login_police_user, name='login-police'),
    path('protected/normal/', normal_user_route, name='normal_user_route'),
    path('protected/police/', police_user_route, name='police_user_route'),

    path('check_token/', check_token, name='check_token'),

    path('pr/send_otp/', send_otp, name='send_otp'),
    path('pr/verify_otp/', verify_otp, name='verify_otp'),
    path('pr/reset_password/', reset_password, name='reset_password'),
    path('api/log/<str:status>/<int:id>', updateLog, name='update-log'),
    path('api/get_name/', getName, name='get_name'),
    path('update_device_token/', update_device_token, name='update_device_token'),
    path('get_channel_id/', get_channel_id, name='get_channel_id'),
    path('second_police_call/', second_police_call, name='second_police_call'),
    path('debug/', debugView, name='debugView'),
    path('api/settings/', getSettings, name='getSettings'),
    path('api/updateSettings/', updateSettings, name='update-settings'),
    path('logs/user/', get_user_logs, name='user-logs'),
    path('logs/police/', get_police_logs, name='police-logs'),
    path('api/get_duty_status', get_duty_status, name='get-duty-status'),
    path('api/update_duty_status', update_duty_status, name='update-duty-status'),
    path('call_ended/', call_ended, name='call_ended'),
    path('api/gallary/', getGallary, name='gallary-list'),
    path('api/news/', getNews, name='get-news'),
    path('api/allnews/', allNews, name='all-news'),
    path('api/complain/', submit_complaint, name='submit_complaint'),
    path('api/get_profile_picture/', getProfilePicture, name='getProfilePicture'),
]
