{% block body %}
{% set magicComment = '#mg ' -%}
{% set markdownComment = '#md ' -%}
{% for cell in nb.cells %}
{% if cell.cell_type == 'code' -%}
{% if cell.source.startswith('%') -%}
{% set lines = cell.source.split('\n') -%}
{% for line in lines -%}
{{ magicComment + line }}
{% endfor -%}
{% else -%}
{{ cell.source }}
{% endif -%}
{% elif cell.cell_type == 'markdown' -%}
{% set lines = cell.source.split('\n') -%}
{% for line in lines -%}
{{ markdownComment + line }}
{% endfor -%}
{% endif -%}
{% endfor -%}
{% endblock body -%}