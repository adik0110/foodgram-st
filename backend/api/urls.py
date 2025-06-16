from django.urls import include, path

app_name = 'api'

urlpatterns = [
    path('', include('users.urls')),
    path('', include('ingredients.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]