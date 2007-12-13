import pysvn
import datetime
import urlparse
from django.db import models
from django.utils import text
from django.core import validators
from unipath import Path

LANGUAGE_CHOICES = (
    ("en", "English"),
)

CHAPTER_TYPE_CHOICES = (
    ("C", "chapter"),
    ("A", "appendix"),
)

def isValidSVNRoot(field_data, all_data):
    c = pysvn.Client()
    try:
        c.info2(field_data, recurse=False)
    except pysvn.ClientError:
        raise validators.ValidationError("Please enter a valid SVN URL.")

class BookVersion(models.Model):
    version  = models.CharField(max_length=6)
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    svn_root = models.CharField(max_length=200, validator_list=[isValidSVNRoot])
    newer_version = models.ForeignKey('self', blank=True, null=True)
    
    class Admin:
        ordering = ("language", "version")
        list_display = ("version", "language")
        
    def __str__(self):
        return "%s (%s)" % (self.version, self.get_language_display().lower())
        
    @models.permalink
    def permalink(self):
        return ("djangobook.views.toc", (self.language, self.version))

class Chapter(models.Model):
    type          = models.CharField(max_length=1, choices=CHAPTER_TYPE_CHOICES)
    number        = models.PositiveSmallIntegerField()
    title         = models.CharField(max_length=200)
    version       = models.ForeignKey(BookVersion, related_name="chapters")
    release_date  = models.DateTimeField(blank=True, null=True)
    comments_open = models.BooleanField("comments are open", default=True)
    code          = models.FileField(upload_to="code", blank=True, null=True)

    class Meta:
        unique_together = [("type", "number", "version")]
        ordering = ("version", "-type", "number")

    class Admin:
        list_filter = ("version",)
        list_display = ("title", "get_number_display", "version", "release_date", "comments_open")
        ordering = ("number",)

    def __str__(self):
        return "%s %s: %s" % (self.get_type_display().title(), self.get_number_display(), self.title)
    
    def get_number_display(self):
        if self.type == "C":
            return str(self.number)
        else:
            return chr(ord('A') + self.number - 1)
    get_number_display.short_description = "Number"
    get_number_display.admin_order_field = "number"
            
    def get_number_url_fragment(self):
        if self.type == "C":
            return "%02i" % self.number
        else:
            return chr(ord('A') + self.number - 1)
    
    @models.permalink
    def permalink(self):
        return ("djangobook.views.chapter", (self.version.language, 
                                             self.version.version, 
                                             self.type,
                                             self.get_number_url_fragment()))

    def get_svn_url(self):
        filename = "%s%s.txt" % (self.get_type_display().lower(), self.get_number_url_fragment())
        return str(Path(self.version.svn_root).child(filename))
        
    def get_content(self):
        c = pysvn.Client()
        try:
            return c.cat(self.get_svn_url())
        except pysvn.ClientError:
            return None
        
    def is_released(self):
        return self.release_date and self.release_date < datetime.datetime.now()

    def get_public_comments(self):
        return self.comments.filter(is_removed=False).order_by("date_posted")
        
    def get_next_chapter(self):
        if not hasattr(self, "_next_chapter"):
            self._next_chapter = None
            toc = list(Chapter.objects.filter(version=self.version))
            index = toc.index(self)
            for c in toc[index+1:]:
                if c.is_released():
                    self._next_chapter = c
                    break;
        return self._next_chapter
        
    def get_previous_chapter(self):
        if not hasattr(self, "_prev_chapter"):
            self._prev_chapter = None
            toc = list(Chapter.objects.filter(version=self.version))
            index = toc.index(self)
            for c in reversed(toc[:index]):
                if c.is_released():
                    self._prev_chapter = c
                    break;
        return self._prev_chapter
        
    next = property(get_next_chapter)
    previous = property(get_previous_chapter)
        
class Comment(models.Model):
    chapter     = models.ForeignKey(Chapter, related_name="comments")
    name        = models.CharField(max_length=50)
    email       = models.EmailField()
    url         = models.URLField(verify_exists=False, blank=True)
    nodenum     = models.PositiveSmallIntegerField()
    comment     = models.TextField()
    date_posted = models.DateTimeField()
    is_removed  = models.BooleanField()
    is_reviewed = models.BooleanField()
        
    class Meta:
        ordering = ("-date_posted",)    
        
    class Admin:
        list_display = ("get_truncated_comment", "name", "email", "date_posted", "is_removed", "is_reviewed")
        list_filter = ("is_removed", "is_reviewed")
        search_fields = ("name", "email", "comment")
    
    def get_truncated_comment(self):
        return text.truncate_words(self.comment, 100)
    get_truncated_comment.short_description = "Comment"
    
class PrivateVersion(models.Model):
    slug = models.SlugField()
    svn_root = models.CharField(max_length=200, validator_list=[isValidSVNRoot])

    class Admin:
        list_display = ["slug", "svn_root"]

    def __str__(self):
        return "Private version from %s" % self.svn_root

    @models.permalink
    def permalink(self):
        return ("djangobook.views.private_toc", (self.slug))

    def get_content(self, chapterslug):
        c = pysvn.Client()
        try:
            return c.cat(urlparse.urljoin(self.svn_root, chapterslug + ".txt"))
        except pysvn.ClientError:
            return None
