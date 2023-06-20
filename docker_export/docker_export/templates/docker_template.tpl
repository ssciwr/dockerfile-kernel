{% block body %}
{% for cell in nb.cells %}
{{- cell.source }}
{% endfor %}
{% endblock body %}