from api.views import SignUpApiView, TokenApiView
from django.urls import path

urlpatterns = [
    path('signup/', SignUpApiView.as_view()),
    path('token/', TokenApiView.as_view()),
]
