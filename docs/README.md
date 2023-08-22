# Sphinx Documentaion for DockerKernel

#### Install dependencies
- `pip install Sphinx`
- `pip install commonmark`

#### Add templates
[This](https://stackoverflow.com/a/62613202/11785440) shows a way to use `sphinx.ext.autosummary` with custom templates. For now an [AssertionError](https://github.com/sphinx-doc/sphinx/issues/11632) is raied by `sphinx.ext.autodoc` when using these custom templates -why we would want to use them is described [here](https://stackoverflow.com/a/62613202/11785440) as well - by adding them in the `_template` directory.
A workaround for now is to add the templates to the sphinx site-package source code manually. The templates are located in `site-packages/sphinx/ext/autosummary/templates/autosummary`.

`module.rst`:
```rst
{{ fullname | escape | underline}}

.. automodule:: {{ fullname }}

   {% block attributes %}
   {% if attributes %}
   .. rubric:: {{ _('Module Attributes') }}

   .. autosummary::
      :toctree:
   {% for item in attributes %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block functions %}
   {% if functions %}
   .. rubric:: {{ _('Functions') }}

   .. autosummary::
      :toctree:
   {% for item in functions %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block classes %}
   {% if classes %}
   .. rubric:: {{ _('Classes') }}

   .. autosummary::
      :toctree:
   {% for item in classes %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block exceptions %}
   {% if exceptions %}
   .. rubric:: {{ _('Exceptions') }}

   .. autosummary::
      :toctree:
   {% for item in exceptions %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

{% block modules %}
{% if modules %}
.. rubric:: Modules

.. autosummary::
   :toctree:
   :recursive:
{% for item in modules %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}
```

`class.rst`:
```rst
{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :show-inheritance:
   :inherited-members:

   {% block methods %}
   .. automethod:: __init__

   {% if methods %}
   .. rubric:: {{ _('Methods') }}

   .. autosummary::
   {% for item in methods %}
      ~{{ name }}.{{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block attributes %}
   {% if attributes %}
   .. rubric:: {{ _('Attributes') }}

   .. autosummary::
   {% for item in attributes %}
      ~{{ name }}.{{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}
```

#### Build Documentation
Navigate into the `/docs` directory and run `make html`.

#### Sphinx Autobuild
To have a live view of the documentation you can use `sphinx-autobuild`.
Install it via `pip install sphinx-autobuild` and run 
```bash
sphinx-autobuild . _build/html
```
inside the `/docs` directory.