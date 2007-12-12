import string
import datetime

from django.conf import settings
from django.utils import simplejson
from django.core.cache import cache
from docutils.core import publish_parts
from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import render_to_response, get_object_or_404

from djangobook.rst import publish_html
from djangobook.models import Chapter, BookVersion, Comment, PrivateVersion

def toc(request, lang, version):
    bookversion = get_object_or_404(BookVersion, version=version, language=lang)
    return render_to_response(
        "book/toc.html", 
        {"contents" : Chapter.objects.filter(version=bookversion), "book_version" : bookversion},
        RequestContext(request, {})
    )

def _get_release_or_404(lang, version, type, chapter, show_future_chapters=False):
    if chapter in string.ascii_uppercase:
        chapter = ord(chapter) - ord('A') + 1
    lookup = dict(
        version__version=version, 
        version__language=lang,
        type=type[0].upper(),
        number=int(chapter),
    )
    if not show_future_chapters:
        lookup["release_date__lte"] = datetime.datetime.now()
    release = get_object_or_404(Chapter, **lookup)
    content = release.get_content()
    if content is None:
        raise Http404("Chapter release has no content.")
    return release, content

def chapter(request, lang, version, type, chapter):
    release, content = _get_release_or_404(lang, version, type, chapter, request.user.has_perm("djangobook.change_chapter"))
    parts = cache.get("djangobook:rendered_content:%s" % release.id)
    if parts is None or settings.DEBUG or request.GET.has_key("clear_cache"):
        parts = publish_html(content)
        cache.set("djangobook:rendered_content:%s" % release.id, parts, 5*60)
    return render_to_response(
        ["book/%s%s.html" % (release.get_type_display(), release.get_number_display()), "book/chapter.html"], 
        {"release" : release, "content" : parts},
        RequestContext(request, {})
    )

@login_required
def private_toc(request, slug):
    vers = get_object_or_404(PrivateVersion, slug=slug)
    chapters = list(Chapter.objects.all())
    for c in chapters:
        c.exists_in_branch = bool(vers.get_content("%s%si" % (c.get_type_display().lower(), c.get_number_display())))
    return render_to_response(
        "book/private_toc.html",
        {"contents" : chapters, "version" : vers},
        RequestContext(request, {})
    )

@login_required
def private_chapter(request, slug, type, chapter):
    vers = get_object_or_404(PrivateVersion, slug=slug)
    content = vers.get_content(type+chapter)
    if not content:
        raise Http404
    parts = publish_parts(source=content, writer=DjangoBookHTMLWriter(), settings_overrides={'initial_header_level' : 3})
    return render_to_response(
        ["book/private_%s%s.html" % (type, chapter), "book/private_chapter.html"], 
        {"version" : vers, "content" : parts},
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
