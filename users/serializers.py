from rest_framework import serializers

from . models import UserProfile
from django.contrib.auth.models import User
# from . utils import sendMail

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
           model = UserSerializer()
           fields = ['fullname', 'phone', 'gender', 'image']

class RegistrationSerializer(serializers.ModelSerializer):
     username = serializers.CharField(write_only = True)
     password1 = serializers.CharField(write_only = True)
     password2 = serializers.CharField(write_only = True)
     email = serializers.EmailField(write_only = True)
     class Meta:
          model = UserProfile
          fields = ['fullname', 'username', 'email', 'password1', 'password2', 'phone', 'gender', 'image']

     def validate(self,data):
        if data['password1'] != data['password2']:
             raise serializers.ValidationError("Password does not match!!!")
        return data 
     
     def create(self, validated_data):
          username = validated_data.pop('username')
          email = validated_data.pop('email')
          password = validated_data.pop('password1')

          user = User.objects.create_user(username=username, email=email, password=password)
          profile = UserProfile.objects.create(
               user = user,
               fullname = validated_data['fullname'],
               phone = validated_data['phone'],
               gender = validated_data['gender'],
               image = validated_data.get('image'),
          )
          # sendMail(email, profile.fullname)
          return profile 