from django.urls import path,include
from . import views 
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenBlacklistView






urlpatterns = [
    path('',include('yolda.urls')),
    path('get-users',views.UserView.as_view()),
    


    ################
    ######### OTP #######
    path('login',views.GetPhoneView.as_view()),
    path('verify',views.VerifyPhoneOTPView.as_view()),
        ## org###
        path('get-login-otp-mobile-org',views.ValidatePhoneSendOTP.as_view(),name='get-login-otp-mobile'),
        #### 
    #####################

    ##########REGISTER ############
    path('logout', views.LogoutView.as_view(), name='token_blacklist'),
    path('change-password/<int:pk>', views.ChangePasswordView.as_view(), name='auth_change_password'),
    path('update-profile/<int:pk>', views.UpdateProfileView.as_view(), name='auth_update_profile'),
    path('get-profile/<int:pk>', views.GetUserProfileView.as_view(), name='get_profile'),
    path('image-save',views.ImageSaveView.as_view(),name='img_save'),
    
    ##############################
]