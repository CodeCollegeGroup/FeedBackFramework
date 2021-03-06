from django.conf.urls import url
from rest_framework import routers
from denunciation.views import DenunciationList, DenunciationDetails
from .views import (
    DenunciableViewSet,
    DenunciationCategoryViewSet,
    DenouncerViewSet,
    change_denunciation_state,
    DenunciationQueueViewList,
    DenunciationStateViewSet
)

ROUTER = routers.DefaultRouter()
ROUTER.register(r'denunciable', DenunciableViewSet)
ROUTER.register(r'denunciation-category', DenunciationCategoryViewSet)
ROUTER.register(r'denouncer', DenouncerViewSet)
ROUTER.register(r'denunciation-state', DenunciationStateViewSet)

urlpatterns = ROUTER.urls  # pylint: disable=invalid-name

urlpatterns += [
    url(
        r'denunciation/$',
        DenunciationList.as_view(),
        name='denunciation-list'
    ),
    url(
        r'denunciation/(?P<pk>[0-9]+)/$',
        DenunciationDetails.as_view(),
        name='denunciation-detail'
    ),
    url(
        r'denunciation/(?P<pk>[0-9]+)/(?P<state>[a-z]+)/$',
        change_denunciation_state
    ),
    url(
        r'denunciation-queue',
        DenunciationQueueViewList.as_view()
    )
]
