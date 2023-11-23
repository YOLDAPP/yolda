from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator

# Create your models here.
class Role(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, is_staff=False, is_active=True, is_admin=False, is_driver=False, is_user=True):
        if not phone:
            raise ValueError('users must have a phone number')
        if not password:
            raise ValueError('user must have a password')

        user_obj = self.model(
            phone=phone
        )
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.active = is_active
        user_obj.admin = is_admin
        user_obj.doctor = is_driver
        user_obj.user = is_user

        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, phone, password=None):
        user = self.create_user(
            phone,
            password=password,
            is_staff=True,

        )
        return user

    def create_superuser(self, phone, password=None):
        user = self.create_user(
            phone,
            password=password,
            is_staff=True,
            is_admin=True,


        )
        return user
GENDER =(
    (1,"MALE"),
    (2,"FEMALE")
)

TOIFA =(
    (1,"A"),
    (2,"B"),
    (3,"D"),
    (4,"C"),
    (5,"BE"),
    (6,"CE"),
    (7,"DE"),
)
class User(AbstractBaseUser):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=15, unique=True)
    firstname = models.CharField(max_length=50, blank=True, null=True)
    username = models.CharField(max_length=50, blank=True, null=True)
    lastname = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(max_length=500, blank=True, null=True)
    image = models.ImageField(upload_to="images/", blank=True, null=True)
    first_login = models.BooleanField(default=False)
    otp = models.CharField(max_length=9, blank=True, null=True)
    email = models.EmailField(max_length =50,blank=True,null=True )
    logged = models.BooleanField(default=False, help_text='If otp verification got successful')
    count = models.IntegerField(default=0, help_text='Number of otp sent')
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    brith_date = models.CharField(max_length=30,blank=True,null=True)
    role = models.ForeignKey(Role,on_delete=models.CASCADE,blank=True,null=True)
    gender = models.SmallIntegerField(choices=GENDER,blank=True,null=True)
    car = models.ForeignKey('Car',on_delete=models.CASCADE,blank=True,null=True)
    license = models.CharField(max_length=10,choices= TOIFA,blank=True,null=True)
    license_img = models.ImageField(upload_to='uploads/license_car',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    admin = models.BooleanField(default=False)
    user = models.BooleanField(default=True)
    doctor = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):

        return True
    
    @property
    def get_role(self):
        return self.role

    @property
    def is_staff(self):
        return self.staff
    

    @property
    def is_active(self):
        return self.active

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_doctor(self):
        return self.doctor

    @property
    def is_user(self):
        return self.user
IMG_TYPE =(
    (1,'CAR'),
    (2,'TOTAL')
)
    
class Images(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='image_thumb')
    path = models.ImageField(upload_to='uploads/car_images/')
    type_img = models.SmallIntegerField(choices=IMG_TYPE,default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Car(models.Model):
    model_name = models.CharField(max_length=30,blank=True,null=True)
    model_img = models.ImageField(upload_to='uploads/model',blank=True,null=True)
    mark = models.CharField(max_length=30,blank=True,null=True)
    photo = models.ImageField(upload_to='uploads/photo',blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
