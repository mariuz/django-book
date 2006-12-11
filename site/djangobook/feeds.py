from djangobook.models import BookVersion, Comment
from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed

class PublishedChaptersFeed(Feed):
    feed_type = Atom1Feed
    
    title = "Django Book new chapter feed"
    description = "New chapters of the Django Book published online."
    link = "/en/beta/"
    author_name = "Adrian Holovaty and Jacob Kaplan-Moss"
    author_email = "feedback@djangobook.com"
    
    def items(self):
        version = BookVersion.objects.get(language="en", version="beta")
        return [rc for rc in version.chapters.order_by("-release_date") if rc.is_released()]
        
    def item_link(self, obj):
        return "/%s/%s/%s%02i/" % (
            obj.version.language, 
            obj.version.version, 
            obj.chapter.get_type_display(), 
            obj.chapter.number
        )
                                   
    def item_pubdate(self, obj):
        return obj.release_date
        
class CommentFeed(Feed):
    feed_type = Atom1Feed
    
    title = "Django Book comment feed"
    description = "Comment feed for the Django Book"
    link = "/en/beta/"
    author_name = "Adrian Holovaty and Jacob Kaplan-Moss"
    author_email = "feedback@djangobook.com"
    
    def items(self):
        version = BookVersion.objects.get(language="en", version="beta")
        return Comment.objects.filter(chapter__version=version, is_removed=False).order_by('-date_posted')[:50]
        
    def item_link(self, obj):
        return "/%s/%s/%s%02i/#cn%i" % (
            obj.chapter.version.language, 
            obj.chapter.version.version, 
            obj.chapter.chapter.get_type_display(), 
            obj.chapter.chapter.number,
            obj.nodenum,
        )
        
    def item_pubdate(self, obj):
        return obj.date_posted