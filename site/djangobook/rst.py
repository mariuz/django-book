import urlparse
import smartypants
from docutils import nodes
from docutils.core import publish_parts
from docutils.writers import html4css1

def publish_html(content, **settings):
    return publish_parts(
        source = content, 
        writer = DjangoBookHTMLWriter(), 
        settings_overrides = settings
    )

class DjangoBookHTMLWriter(html4css1.Writer):
    
    settings_spec = html4css1.Writer.settings_spec + (
        "Djangobook-specific options",
        "Options specific to the Django book web site",
        (
            ('The root URL for images/figures',
              ['--media-base'],
              {'metavar': '<URL>', 'overrides': 'media_base'}),
        ),
    )
    
    settings_defaults = dict(html4css1.Writer.settings_defaults,
        initial_header_level = 3,
        media_base = "",
    )
    
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = DjangoBookHTMLTranslator

class DjangoBookHTMLTranslator(html4css1.HTMLTranslator):
    
    #
    # Hacks to work around various annoying docutils defaults.
    #
    
    # This prevents name attributes from being generated.
    named_tags = []
        
    # Remove the stupid "border=1" default on tables.
    def visit_table(self, node):
        self.body.append(self.starttag(node, 'table', CLASS='docutils'))

    # Prevent <h3> from becoming <h3><a id=...>
    def visit_title(self, node, move_ids=1):
        if isinstance(node.parent, nodes.Admonition):
            self.body.append(self.starttag(node, 'p', '', CLASS='admonition-title'))
            self.context.append("</p>\n")
        else:
            html4css1.HTMLTranslator.visit_title(self, node)
            
    # Make images be relative to media_base
    def visit_image(self, node):
        base = self.settings.media_base
        if not base.endswith("/"): base = base + "/"
        node["uri"] = urlparse.urljoin(base, node["uri"])
        html4css1.HTMLTranslator.visit_image(self, node)
    
    # Avoid doing <blockquote><ul>...
    # Adapted from http://thread.gmane.org/gmane.text.docutils.user/742/focus=804
    _suppress_blockquote_child_nodes = (nodes.bullet_list,
                                        nodes.enumerated_list,
                                        nodes.definition_list, 
                                        nodes.literal_block,
                                        nodes.doctest_block,
                                        nodes.line_block,
                                        nodes.table)
    
    def visit_literal_block(self, node):
        self._in_literal += 1
        html4css1.HTMLTranslator.visit_literal_block(self, node)

    def depart_literal_block(self, node):
        html4css1.HTMLTranslator.depart_literal_block(self, node)
        self._in_literal -= 1
     
    def visit_literal(self, node):
        self._in_literal += 1
        try:
            html4css1.HTMLTranslator.visit_literal(self, node)
        finally:
            self._in_literal -= 1
     
    def encode(self, text):
        text = html4css1.HTMLTranslator.encode(self, text)
        if self._in_literal <= 0:
            text = smartypants.smartyPants(text, "qde")
        return text
    
    def visit_block_quote(self, node):
        if len(node.children) != 1 or not isinstance(node.children[0], self._suppress_blockquote_child_nodes):
            html4css1.HTMLTranslator.visit_block_quote(self, node)

    def depart_block_quote(self, node):
        if len(node.children) != 1 or not isinstance(node.children[0], self._suppress_blockquote_child_nodes):
            html4css1.HTMLTranslator.depart_block_quote(self, node)

    #
    # Avoid using reserved words in section titles
    #
    def visit_section(self, node):
        node['ids'] = ['s-' + i for i in node.get('ids', [])]
        html4css1.HTMLTranslator.visit_section(self, node)

    #
    # Code for auto-ID generation.
    #
    
    # tags we want to autogenerate ids on
    _autoid_prefix = "cn"
    _autoid_tags = ["blockquote", "h3", "h4", "h5", "h6", "li", "p", "pre", "table"]
    
    def __init__(self, document):
        html4css1.HTMLTranslator.__init__(self, document)
        self._autoid_number = 0
        self._skip_autoid_depth = 0
        self._in_literal = 0
        
    def _add_autoid(self, node):
        node.setdefault("classes", []).append(self._autoid_prefix)
        node.setdefault("ids", []).insert(0, "%s%s" % (self._autoid_prefix, self._autoid_number))
        self._autoid_number += 1
    
    def starttag(self, node, tagname, suffix='\n', empty=0, **attributes):
        if self._skip_autoid_depth == 0 and tagname in self._autoid_tags:
            self._add_autoid(node)
        return html4css1.HTMLTranslator.starttag(self, node, tagname, suffix, empty, **attributes)
        
    def visit_admonition(self, node, name=''):
        self._skip_autoid_depth += 1
        self._add_autoid(node)
        node.setdefault("classes", []).append("admonition")
        self.body.append(self.starttag(node, 'div'))
        self.set_first_last(node)
        
    def depart_admonition(self, node=None):
        html4css1.HTMLTranslator.depart_admonition(self, node)
        self._skip_autoid_depth -= 1
        
    # wrap <div> around <dd>/<dt>s
    def visit_definition_list_item(self, node):
        self._add_autoid(node)
        self.body.append(self.starttag(node, "div", ""))

    def depart_definition_list_item(self, node):
        self.body.append("</div>\n");

