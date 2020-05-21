from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user's object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name') 
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5 
            }
        }

    def create(self, validated_data):
        """Create and new user with email and password"""
        return get_user_model().object.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type':'password'}, 
        trim_whitespace=False
    ) 

    def validate(self, attrs):
        """Validates and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = _('invalid credentials')
            raise serializers.ValidationError(msg, code='authentication')
            print(self.context.get('request'))
            
        attrs['user'] = user
        return attrs