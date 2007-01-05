import datetime

from django.conf import settings
from django.utils import simplejson
from django.core.cache import cache
from docutils.core import publish_parts
from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render_to_response, get_object_or_404

from djangobook.rst import DjangoBookHTMLWriter
from djangobook.models import Chapter, BookVersion, ReleasedChapter, Comment

def toc(request, lang, version):
    book = get_object_or_404(BookVersion, version=version, language=lang)
    toc = []
    for chapter in Chapter.objects.all():
        try:
            release = chapter.releases.get(version=book)
        except ReleasedChapter.DoesNotExist:
            release = None
        toc.append({"chapter" : chapter, "release" : release})
    return render_to_response(
        "book/toc.html", 
        {"contents" : toc, "book_version" : book},
        RequestContext(request, {})
    )

def _get_release_or_404(lang, version, type, chapter, show_future_chapters=False):
    lookup = dict(
        version__version=version, 
        version__language=lang,
        chapter__type=type[0].upper(),
        chapter__number=int(chapter),
    )
    if not show_future_chapters:
        lookup["release_date__lte"] = datetime.datetime.now()
    release = get_object_or_404(ReleasedChapter, **lookup)
    content = release.get_content()
    if content is None:
        raise Http404("Chapter release has no content.")
    return release, content

def chapter(request, lang, version, type, chapter):
    release, content = _get_release_or_404(lang, version, type, chapter, request.user.has_perm("djangobook.change_chapter"))
    parts = cache.get("djangobook:rendered_content:%s" % release.id)
    if parts is None or settings.DEBUG or request.GET.has_key("clear_cache"):
        parts = publish_parts(source=content, writer=DjangoBookHTMLWriter(), settings_overrides={'initial_header_level' : 3})
        cache.set("djangobook:rendered_content:%s" % release.id, parts, 5*60)
    return render_to_response(
        ["book/%s%02i.html" % (release.chapter.get_type_display(), release.chapter.number), "book/chapter.html"], 
        {"release" : release, "content" : parts},
        RequestContext(request, {})
    )

def comments(request, lang, version, type, chapter, nodenum=None):
    release, content = _get_release_or_404(lang, version, type, chapter)
        
    if request.method == "POST":
        manip = Comment.AddManipulator()
        data = request.POST.copy()
        data["date_posted_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
        data["date_posted_time"] = datetime.datetime.now().strftime("%H:%M:%S")
        data["chapter"] = str(release.id)
        errors = manip.get_validation_errors(data)
        if errors:
            return HttpResponse(simplejson.dumps(errors.keys()), mimetype="text/javascript")
        else:
            manip.do_html2python(data)
            comment = manip.save(data)
            return render_to_response(
                "book/comments_snippet.html", 
                {"comments" : [comment]},
                RequestContext(request, {})
            )
    else:
        comments = comments = release.get_public_comments()
        if nodenum:
            comments = comments.filter(nodenum=nodenum)
        return render_to_response(
            "book/comments_snippet.html", 
            {"comments":list(comments)},
            RequestContext(request, {})
        )
        
def comment_counts(request, lang, version, type, chapter):
    release, content = _get_release_or_404(lang, version, type, chapter)
    comment_counts = {}
    for c in release.get_public_comments():

        #don't include reviewed comments in counts for reviewers.
        if request.user.has_perm("djangobook.change_comment") and c.is_reviewed:
            inc = 0
        else:
            inc = 1
        comment_counts[c.nodenum] = comment_counts.get(c.nodenum, 0) + inc
    return HttpResponse(simplejson.dumps(comment_counts.items()), mimetype="text/javascript")

@require_POST
@permission_required("djangobook.change_comment")
def remove_comment(request, comment_id):
    c = get_object_or_404(Comment, pk=comment_id)
    c.is_removed = True
    c.save()
    return HttpResponse("OK")
    
@require_POST
@permission_required("djangobook.change_comment")
def mark_comment_reviewed(request, comment_id):
    c = get_object_or_404(Comment, pk=comment_id)
    c.is_reviewed = not c.is_reviewed
    c.save()
    return HttpResponse("OK")
