from django.urls import include, path


urlpatterns = [
    path("v1/", include("movie_admin.api.v1.urls")),
]
