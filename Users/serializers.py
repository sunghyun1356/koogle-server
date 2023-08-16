from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # password = serializers.CharField(write_only=True) 코드를 추가하는 이유는 
    # 패스워드 필드에 대해 특별한 처리를 하기 위해서. 그 처리가 바로 write_only=True 인데, 
    # 이 설정이 있으면 시리얼라이저는 해당 필드를 "쓰기 전용"으로 만든다.
    # 일반적으로 사용자 정보를 클라이언트에게 반환할 때 패스워드와 같은 민감한 정보를 포함해서는 안 되기에 
    # write_only=True 설정을 사용하면, 해당 필드는 클라이언트에서 서버로의 요청(request)에만 사용되고, 
    # 서버에서 클라이언트로의 응답(response)에는 포함되지 않게 된다.
    class Meta:
        model = User
        fields = ('id', 'username', 'password','country', 'is_staff')

    def create(self, validated_data):
        country_name = validated_data.pop('country')  # Extract country_name from validated_data
        try:
            country = Country.objects.get(name=country_name)  # Find the Country object with the given name
        except Country.DoesNotExist:
            # Handle case where country doesn't exist
            raise serializers.ValidationError({"country": "Country with the given name does not exist."})

        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            country=country,  # Set the country object
            is_staff=validated_data['is_staff']
        )
        return user