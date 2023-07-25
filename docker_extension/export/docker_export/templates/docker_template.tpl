{% block body %}
{% set cellOpeningComment = '#cellStart' -%}
{% set cellClosingComment = '#cellEnd' -%}
{% set magicComment = '#mg ' -%}
{% set markdownComment = '#md ' -%}
{% for cell in nb.cells %}
{% set lines = cell.source.split('\n') -%}
{% if cell_has_empty_line(cell) -%}
{{ cellOpeningComment }}
{% endif -%}
{% if cell.cell_type == 'code' -%}
{% if cell.source.startswith('%') -%}
{% for line in lines -%}
{{ magicComment + line }}
{% endfor -%}
{% else -%}
{{ cell.source }}
{% endif -%}
{% elif cell.cell_type == 'markdown' -%}
{% for line in lines -%}
{{ markdownComment + line }}
{% endfor -%}
{% endif -%}
{% if cell_has_empty_line(cell) -%}
{{ cellClosingComment }}
{% endif -%}
{% endfor -%}
{% endblock body -%}