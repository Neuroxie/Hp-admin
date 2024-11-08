from functools import wraps
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

def user_type_required(user_type):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.user_type == user_type:
                return view_func(request, *args, **kwargs)
            return Response({'error': 'Unauthorized'}, status=HTTP_400_BAD_REQUEST)
        return _wrapped_view
    return decorator
