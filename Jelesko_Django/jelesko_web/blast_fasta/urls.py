from django.conf.urls.defaults import *

# replace `jelesko_web` with the name of your deployment site
urlpatterns = patterns('jelesko_web.blast_fasta.views',
    (r'^blast/$', 'blast'),
    (r'^fasta/$', 'fasta'),
    (r'^ssearch/$', 'ssearch'),
    (r'^selection/(\d+)/', 'seqselection'),
)

