{{ fullname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
    :members:

    {% block methods %}
    .. automethod:: __init__
    {% endblock %}
