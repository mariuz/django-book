import pysvn
from djangobook.models import Chapter
from djangobook.rst import publish_html
from unipath import FSPath as Path

def create_chapters(vers, release_date=None, comments_open=True):
    """
    Create a bunch of ``Chapter`` objects for a given ``BookVersion``.
    """
    c = pysvn.Client()
    for record in c.ls(vers.svn_root):
        name = Path(record["name"]).name
        if name.ext != ".txt":
            continue
        
        parts = publish_html(c.cat(record["file"]))
        
        if name.startswith("appendix"):
            Chapter.objects.get_or_create(
                type = "A",
                number = ord(name.stem[-1]) - ord('A'),
                title = parts["title"],
                version = vers,
                defaults = dict(
                    release_date = release_date,
                    comments_open = comments_open,
                )
            )
        
        elif name.startswith("chapter"):
            Chapter.objects.get_or_create(
                type = "C",
                number = int(name.stem[-2:])
                title = parts["title"],
                version = vers,
                defaults = dict(
                    release_date = release_date,
                    comments_open = comments_open,
                )
            )