from django.conf.urls.defaults import *
from djangobook.feeds import PublishedChaptersFeed, CommentFeed
from djangobook.views import *

urlpatterns = patterns('',
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^accounts/login/$',  'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (    
        r'^feed/(?P<url>.*)/$', 
        'django.contrib.syndication.views.feed', 
        {'feed_dict': {"comments" : CommentFeed}}
    ),
    (
        r'^tools/removecomment/(?P<comment_id>\d+)/$',
        remove_comment,
    ),
    (
        r'^tools/markreviewed/(?P<comment_id>\d+)/$',
        mark_comment_reviewed,
    ),
    (
        r'^private/(?P<slug>[\w-]+)/$',
        private_toc
    ),
    (
        r'^private/(?P<slug>[\w-]+)/(?P<type>chapter|appendix)(?P<chapter>\d{2})/$', 
        private_chapter
    ),
    (
        r'^(?P<lang>[\w-]+)/(?P<version>[\w-]+)/$',
        toc
    ),
    (
        r'^(?P<lang>[\w-]+)/(?P<version>[\w-]+)/(?P<type>chapter|appendix)(?P<chapter>\d{2})/$', 
        chapter
    ),
    (
        r'^(?P<lang>[\w-]+)/(?P<version>[\w-]+)/(?P<type>chapter|appendix)(?P<chapter>\d{2})/comments/(?:(?P<nodenum>\d+)/)?$', 
        comments,
    ),
    (
        r'^(?P<lang>[\w-]+)/(?P<version>[\w-]+)/(?P<type>chapter|appendix)(?P<chapter>\d{2})/comments/counts/$', 
        comment_counts,
    ),
    (
        r'^feed/$', 
        'django.contrib.syndication.views.feed', 
        {'feed_dict': {"chapters" : PublishedChaptersFeed}, "url" : "chapters"}
    ),
    (
        r'(?P<url>.*)$',
        'django.contrib.flatpages.views.flatpage',
    ),
)