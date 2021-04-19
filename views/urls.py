from django.conf.urls import url

from .views import image, random

app_name = "views"
urlpatterns = [
    url(r'^image/(?P<filename>.+)$',        image.ImageView.as_view(), name='image'),

    url(r'^random/?$',                      random.RandomImagesView.as_view(), name='random'),
]
