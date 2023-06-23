{% block body %}
{% set comment = '# ' -%}
{% for cell in nb.cells %}
{% if cell.cell_type == 'code' -%}
{% if cell.source.startswith('%') -%}
{{ comment + cell.source }}
{% else -%}
{{ cell.source }}
{% endif -%}
{% elif cell.cell_type == 'markdown' -%}
{{ comment + cell.source }}
{% endif -%}
{% endfor -%}
{% endblock body -%}