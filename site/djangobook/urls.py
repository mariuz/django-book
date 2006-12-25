from django.conf.urls.defaults import *
from djangobook.feeds import PublishedChaptersFeed, CommentFeed
from djangobook.views import toc, chapter, comments, comment_counts, remove_comment

urlpatterns = patterns('',
    (r'accounts/login/$',  'django.contrib.auth.views.login'),
    (r'accounts/logout/$', 'django.contrib.auth.views.logout'),
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
    )
)