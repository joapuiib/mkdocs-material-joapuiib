---
template: programacio.html
title: Header i footer
icon: material/page-layout-header-footer
---

## Programació
La plantilla `programacio.html` és una plantilla que inclou un header
i un footer.

Es pot configurar la pàgina perquè utilitze aquesta plantilla afegint
la següent capçalera al fitxer de la pàgina:
```yml
---
template: programacio.html
---
```


<div class="break-page"></div>

## Capçalera i peus de pàgina
La capçalera i el peu de pàgina poden ser configurant sobreescrivint
els blocks `content_header` i `content_footer` de la plantilla.

```html
{% raw %}
{% block content_header %}
    <p>Custom header</p>
{% endblock %}
{% endraw %}
```

La capçalera i el peu de pàgina es mostraran a totes les pàgines
quan s'imprimisca la pàgina ++ctrl+p++.
