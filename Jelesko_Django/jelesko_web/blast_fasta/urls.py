from django.conf.urls.defaults import *
from blast_fasta import views

# replace `jelesko_web` with the name of your deployment site
urlpatterns = patterns('',
    url(r'^blast/$', views.blast, name='blast2'),
    url(r'^fasta/$', views.fasta, name='fasta'),
    url(r'^ssearch/$', views.ssearch, name='ssearch'),
    url(r'^selection/(\d+)/$', views.seqselection, name='selection'),
    url(r'^seqrequest/$', views.seqrequest, name='seqrequest'),
)

