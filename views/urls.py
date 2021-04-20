from django.conf.urls import url

from .views import image, search

app_name = "views"
urlpatterns = [
    url(r'^image/(?P<filename>.+)$',        image.ImageView.as_view(), name='image'),

    url(r'^search/?$', search.SearchImagesView.as_view(), name='random'),
]
