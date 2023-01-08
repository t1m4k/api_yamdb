from django.urls import path

from api.views import SignUpApiView, TokenApiView

urlpatterns = [
    path('signup/', SignUpApiView.as_view()),
    path('token/', TokenApiView.as_view()),
]
