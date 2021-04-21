from django.conf.urls import url

from .views import image, search, same_image

app_name = "views"
urlpatterns = [
    url(r'^image/(?P<filename>.+)$',        image.ImageView.as_view(), name='image'),

    url(r'^search/?$', search.SearchImagesView.as_view(), name='search'),
    url(r'^same/(?P<pk>\d+)$', same_image.SameImagesView.as_view(), name='same'),
]
