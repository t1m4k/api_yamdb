from django.urls import path

from api.views import SignUpApiView, TokenApiView

urlpatterns = [
    path('signup/', SignUpApiView.as_view(), name='signup'),
    path('token/', TokenApiView.as_view(), name='token_access'),
]
