from django.conf.urls import include, url, patterns
from django.contrib import admin
admin.autodiscover()  ## what???

urlpatterns = [
    url(r'^admin/', include(admin.site.urls,)),
    url(r'^', include('grader.urls', namespace="grader")),
]
