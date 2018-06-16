from django.conf.urls import url
from denunciation.views import DenunciationList, DenunciationDetails

urlpatterns = [
    url(r'denunciation/$', DenunciationList.as_view(),
        name='denunciation-list'),
    url(r'denunciation/(?P<pk>[0-9]+)/$', DenunciationDetails.as_view(),
        name='denunciation-detail'),
]
