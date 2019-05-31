import os
import jinja2

templates_dir = '/'.join((os.path.dirname(__file__), 'templates'))

# Template initial configuration
JENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(templates_dir),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
    trim_blocks=True
)