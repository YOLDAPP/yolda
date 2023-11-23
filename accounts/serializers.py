import imp
from rest_framework import serializers
from .models import Role,User,Images
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .utils import otp_generator



class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields =('id','username', 'password', 'password2', 'email', 'firstname', 'lastname','phone')
        extra_kwargs = {
            "password":{"write_only":True}
        }
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phone=validated_data['phone'],
        )

        
        user.set_password(validated_data['password'])
        user.save()
        return user
        
class UserRegisterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('phone',)
        extra_kwargs = {
            'phone': {'required': True},
            'otp':{'read_only':True}
        }

    

    def create(self, validated_data):
        user = User.objects.create(
            otp = otp_generator(),
            phone=validated_data['phone'],
        )

        
        # user.set_password(validated_data['password'])
        # user.save()

        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    # old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def update(self, instance, validated_data):

        instance.set_password(validated_data['password'])
        instance.save()

        return instance
    
class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields =('path',)
    
class UpdateUserSerializer(serializers.ModelSerializer):
    car_images = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def get_car_images(self, user):
        return CarImageSerializer(Images.objects.filter(user=user), source='Images', many=True).data

    class Meta:
        model = User
        fields = ('username','role','gender','brith_date','password','password2','car','license',
                  'license_img','car_images'
                  )
        extra_kwargs = {
            'username': {'required': True},
            'role': {'required': True},
            'gender': {'required': True},
            'brith_date': {'required': True},
            'car': {'required': True},
            'license': {'required': True},
            'license_img': {'required': True},
            'car_images': {'required': True},
            
        }

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})
        return value

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError({"username": "This username is already in use."})
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs
    
    def update(self, instance, validated_data):
        instance.username = validated_data['username']
        instance.role = validated_data['role']
        instance.gender = validated_data['gender']
        instance.brith_date = validated_data['brith_date']
        instance.car = validated_data['car']
        instance.license = validated_data['license']
        instance.license_img = validated_data['license_img']
        instance.set_password(validated_data['password']) 
        instance.save()

        return instance
    
class UserCarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields =('user','type_img','path')