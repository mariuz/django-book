import pysvn
import datetime
import urlparse
from django.db import models
from django.utils import text
from django.core import validators

LANGUAGE_CHOICES = (
    ("en", "English"),
)

CHAPTER_TYPE_CHOICES = (
    ("C", "chapter"),
    ("A", "appendix"),
)

def isValidSVNRoot(field_data, all_data):
    c = pysvn.Client()
    if not c.is_url(field_data):
        raise validators.ValidationError("Please enter a valid SVN URL.")

class Chapter(models.Model):
    type         = models.CharField(maxlength=1, choices=CHAPTER_TYPE_CHOICES)
    number       = models.PositiveSmallIntegerField()
    title        = models.CharField(maxlength=200)

    class Meta:
        unique_together = [("type", "number")]
        ordering = ("-type", "number")

    class Admin:
        list_display = ("title", "number")
        
    def __str__(self):
        return "%s %s: %s" % (self.get_type_display().title(), self.number, self.title)

class BookVersion(models.Model):
    version  = models.CharField(maxlength=6)
    language = models.CharField(maxlength=5, choices=LANGUAGE_CHOICES)
    svn_root = models.CharField(maxlength=200, validator_list=[isValidSVNRoot])
    
    class Admin:
        ordering = ("language", "version")
        list_display = ("version", "language")
        
    def __str__(self):
        return "%s (%s)" % (self.version, self.get_language_display().lower())
        
    @models.permalink
    def permalink(self):
        return ("djangobook.views.toc", (self.language, self.version))
        
class PrivateVersion(models.Model):
    slug = models.SlugField()
    svn_root = models.CharField(maxlength=200, validator_list=[isValidSVNRoot])

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

class ReleasedChapter(models.Model):
    version       = models.ForeignKey(BookVersion, related_name="chapters")
    chapter       = models.ForeignKey(Chapter, related_name="releases")
    release_date  = models.DateTimeField(blank=True, null=True)
    comments_open = models.BooleanField("comments are open", default=True)

    class Meta:
        unique_together = [("version", "chapter")]

    class Admin:
        ordering = ("-release_date",)
        list_display = ('chapter', 'version', 'release_date')

    def __str__(self):
        return "%s (%s; %s)" % (self.chapter, self.version.version, self.version.language)
        
    @models.permalink
    def permalink(self):
        return ("djangobook.views.chapter", (self.version.language, 
                                             self.version.version, 
                                             self.chapter.type,
                                             "%02i" % self.chapter.number))

    def get_svn_url(self):
        filename = "%s%02i.txt" % (self.chapter.get_type_display().lower(), self.chapter.number)
        return urlparse.urljoin(self.version.svn_root, filename)
        
    def get_content(self):
        c = pysvn.Client()
        try:
            return c.cat(self.get_svn_url())
        except pysvn.ClientError:
            return None
        
    def is_released(self):
        return self.release_date < datetime.datetime.now()

    def get_public_comments(self):
        return self.comments.filter(is_removed=False).order_by("date_posted")
        
    def get_next_chapter(self):
        if not hasattr(self, "_next_chapter"):
            toc = list(Chapter.objects.all())
            index = toc.index(self.chapter)
            if index == len(toc) - 1:
                self._next_chapter = None
            else:
                try:
                    self._next_chapter = ReleasedChapter.objects.get(
                        version__pk = self.version_id, 
                        chapter__pk = toc[index+1].id,
                        release_date__lte = datetime.datetime.now(),
                    )
                except ReleasedChapter.DoesNotExist:
                    self._next_chapter = None
        return self._next_chapter
        
    def get_previous_chapter(self):
        if not hasattr(self, "_previous_chapter"):
            toc = list(Chapter.objects.all())
            index = toc.index(self.chapter)
            if index == 0:
                self._previous_chapter = None
            else:
                try:
                    self._previous_chapter = ReleasedChapter.objects.get(
                        version__pk = self.version_id, 
                        chapter__pk = toc[index-1].id,
                        release_date__lte = datetime.datetime.now(),
                    )
                except ReleasedChapter.DoesNotExist:
                    self._previous_chapter = None
        return self._previous_chapter
        
class Comment(models.Model):
    chapter     = models.ForeignKey(ReleasedChapter, related_name="comments")
    name        = models.CharField(maxlength=50)
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