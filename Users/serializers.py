from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model

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
        # User는 password 해싱을 자동으로 처리해서 저장해주도록
        # User.objects.create_user() 방식으로 객체를 생성함!(다른 객체 생성과 달리)
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            country = validated_data['country'],
            is_staff = validated_data['is_staff']
        )
        return user