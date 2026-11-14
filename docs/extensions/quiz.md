---
title: Quiz
icon: lucide/circle-help
---

# Quiz

Extensió de [Pymdownx Blocks][blocks] que crea preguntes tipus test interactives amb el bloc
`/// quiz`. La solució no es mostra fins que s'encerta la pregunta: si es tria una opció
incorrecta, es marca en roig i es pot tornar a provar.

[blocks]: https://facelessuser.github.io/pymdown-extensions/extensions/blocks/

## Configuració

Per utilitzar el bloc, cal afegir l'extensió a `markdown_extensions` dins de `properdocs.yml`:

```yaml title="properdocs.yml"
markdown_extensions:
  - material_joapuiib.extensions.quiz:
      shuffle: false
```

- __`shuffle`__: barreja l'ordre de les opcions de tots els blocs en carregar la pàgina.
    Per defecte és `false`.

L'extensió activa automàticament el gestor de blocs de `pymdownx`. Els estils i el
JavaScript ja venen inclosos al tema.

!!! warning "Exclou `quiz` de `inline_blocks`, perquè una pregunta amb `:` no es convertisca en un bloc d'una línia."
    ```yaml title="properdocs.yml"
    markdown_extensions:
      - inline_blocks:
          exclude_blocks: [html, quiz]
    ```

## Sintaxi

L'argument del bloc és la pregunta, i el cos és una llista on cada opció comença per `[ ]`
(incorrecta) o `[x]` (correcta). Tot el que hi ha després de la llista és l'__explicació__,
que només es mostra quan s'encerta la pregunta.

````markdown
/// quiz | Per quin port escolta per defecte __PostgreSQL__?
- [ ] `8069`
- [x] `5432`
- [ ] `3306`

`5432` és el port per defecte de PostgreSQL. El `8069` és el del servidor web d'Odoo.
///
````

/// quiz | Per quin port escolta per defecte __PostgreSQL__?
- [ ] `8069`
- [x] `5432`
- [ ] `3306`

`5432` és el port per defecte de PostgreSQL. El `8069` és el del servidor web d'Odoo.
///

Tant la pregunta com les opcions i l'explicació admeten Markdown. Les opcions es poden
triar amb el ratolí o amb el teclat (++tab++ i ++enter++).

!!! warning "Les respostes correctes estan en l'HTML de la pàgina, així que el bloc serveix per practicar, no per avaluar."

## Resposta múltiple

Si la llista té més d'una opció marcada amb `[x]`, la pregunta és de __resposta múltiple__:
s'indica quantes respostes correctes hi ha i la pregunta es resol quan s'han triat totes.
Mentrestant, cada encert es marca en verd i s'avisa que encara en falta alguna.

````markdown
/// quiz | Quins d'aquests impostos són directes?
- [x] IRPF
- [ ] IVA
- [x] Impost de societats
///
````

/// quiz | Quins d'aquests impostos són directes?
- [x] IRPF
- [ ] IVA
- [x] Impost de societats
///

## Opcions del bloc

El bloc accepta l'opció `shuffle`, que té preferència sobre la configuració de l'extensió:

- __`shuffle`__: (opcional) `true` barreja les opcions del bloc i `false` les manté en l'ordre
    en què s'han escrit.

````markdown
/// quiz | Quin d'aquests sectors ofereix serveis?
    shuffle: true

- [x] Terciari
- [ ] Primari
- [ ] Secundari
///
````

/// quiz | Quin d'aquests sectors ofereix serveis?
    shuffle: true

- [x] Terciari
- [ ] Primari
- [ ] Secundari
///

## Esdeveniment `quiz:answered`

Quan una pregunta es resol, el bloc emet l'esdeveniment `quiz:answered`, que es propaga pel
document. El camp `detail.firstTry` indica si s'ha encertat sense cap error, de manera que una
pàgina pot portar el recompte d'encerts:

```js
document.addEventListener("quiz:answered", function (event) {
  console.log(event.detail.firstTry ? "Encertada a la primera" : "Encertada");
});
```
