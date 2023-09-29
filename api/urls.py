from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import SplitWiseViewSets

router = DefaultRouter(trailing_slash=False)
router.register("", SplitWiseViewSets, basename="split-wise")


urlpatterns = [path("", include(router.urls))]
