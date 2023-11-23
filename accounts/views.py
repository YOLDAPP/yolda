from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from accounts.serializers import ChangePasswordSerializer,UserSerializer,UserRegisterSerializer,UpdateUserSerializer,UserCarImageSerializer
from accounts.utils import otp_generator
from .models import User,Images
from django.contrib.auth import login
from rest_framework import permissions, generics, status
from rest_framework.authtoken.models import Token
import requests
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from rest_framework.authentication import TokenAuthentication


# User = get_user_model()

# Create your views here.

class LogoutView(APIView):
    def post(self,request,*agrs, **kwargs):
        # print(999)       #Nothing
        # try:
        #     print(request.user.auth_token)
        #     request.user.auth_token.delete()
        # except (AttributeError):
        #     pass
        logout(request)

        return Response({"success": ("Successfully logged out.")})

class GetPhoneView(APIView):
    def post(self,request,*agrs, **kwargs):
        try:
            phone_number = request.data.get('phone')

            if phone_number:
                phone = str(phone_number)
                key = otp_generator()
                otp_key = str(key)
                if User.objects.filter(phone = phone).exists():
                    user = User.objects.filter(phone = phone)[:1].get()
                    user.otp =otp_key
                    user.save()
                    msg ='User otp updated successfully'
                    status_ = status.HTTP_202_ACCEPTED
                else:
                    user = User(phone = phone,otp=otp_key)
                    user.save()
                    msg ='User created successfully'
                    status_ = status.HTTP_201_CREATED

                return Response({
                    'phone': phone,
                    'otp':otp_key,
                    'success': True,
                    'message': msg,
                    'status': status_,

                })
                
            return Response({
                    'message': 'Phone number is required',
                    'status': status.HTTP_400_BAD_REQUEST,
                })   

        except Exception as e:
            return Response({
                'message': str(e),
                'status': status.HTTP_400_BAD_REQUEST,
            })
        


class RegisterView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.validated_data['password'] =   make_password(serializer.validated_data['password'])
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'response': serializer.data,
            'scucess': True,
            'message': 'User created successfully',
            'status': status.HTTP_201_CREATED,

        })


def send_otp(phone):
    if phone:
        key = otp_generator()
        phone = str(phone)
        otp_key = str(key)

        link = 'link'#f'https://2factor.in/API/R1/?module=TRANS_SMS&apikey=7c59cf94-d129-11ec-9c12-0200cd936042&to={phone}&from=MMBook&templatename=mymedbook&var1={otp_key}&var2={otp_key}'

        result = requests.get(link, verify=False)

        return otp_key
    else:
        return False


class ValidatePhoneSendOTP(APIView):
    def post(self, request, *agrs, **kwargs):
        try:
            phone_number = request.data.get('phone')

            if phone_number:
                phone = str(phone_number)
                user = User.objects.filter(phone__iexact=phone)

                if user.exists():
                    data = user.first()
                    old_otp = data.otp
                    new_otp = send_otp(phone)
                    if old_otp:
                        data.otp = new_otp
                        data.save()
                        return Response({

                            'message': 'OTP sent successfully',
                            'status': status.HTTP_200_OK,
                        })
                    else:
                        data.otp = new_otp
                        data.save()
                        return Response({
                            'message': 'OTP sent successfully',
                            'status': status.HTTP_200_OK,
                        })

                else:
                    return Response({
                        'message': 'User not found ! please register',
                        'status': status.HTTP_404_NOT_FOUND,
                    }
                    )
            else:
                return Response({
                    'message': 'Phone number is required',
                    'status': status.HTTP_400_BAD_REQUEST,
                })
        except Exception as e:
            return Response({
                'message': str(e),
                'status': status.HTTP_400_BAD_REQUEST,
            })


# verify otp
class VerifyPhoneOTPView(APIView):
    def post(self, request, format=None):
        try:
            phone = request.data.get('phone')
            otp = request.data.get('otp')
            if phone and otp:
                user = User.objects.filter(phone__iexact=str(phone))
                if user.exists():
                    user = user.first()
                    if user.otp == otp:
                        login(request, user)
                        token, _ = Token.objects.get_or_create(user=user)
                        return Response({
                            'status': True,
                            'details': 'Login Successfully',
                            
                            'token': token.key,
                            'response': {
                                'id': user.id,
                                'email': user.email,
                                'phone': user.phone,
                                'address': user.address,
                            }
                            })
                    else:
                        return Response({'message': 'OTP does not match'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Phone or OTP is missing'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({
                'status': False,
                'message': str(e),
                'details': 'Login Failed'
            })




class UserView(APIView):
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users , many=True)
        return Response({
                            'data':serializer.data,
                            'status': True,
                            'details': 'Login Successfully',
                            })

# logout api view
class LogoutView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'status':status.HTTP_205_RESET_CONTENT})
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

class ChangePasswordView(generics.UpdateAPIView):
    authentication_classes = (TokenAuthentication, )
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

class UpdateProfileView(generics.UpdateAPIView):

    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UpdateUserSerializer

class GetUserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UpdateUserSerializer


class ImageSaveView(generics.CreateAPIView):
    queryset = Images.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserCarImageSerializer

