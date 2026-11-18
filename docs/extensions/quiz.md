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
/// quiz | Quina és la capital d'__Austràlia__?
- [ ] Sydney
- [x] Canberra
- [ ] Melbourne

Canberra és la capital d'Austràlia, encara que Sydney és la ciutat més poblada.
///
````

/// quiz | Quina és la capital d'__Austràlia__?
- [ ] Sydney
- [x] Canberra
- [ ] Melbourne

Canberra és la capital d'Austràlia, encara que Sydney és la ciutat més poblada.
///

Tot el que hi ha __abans__ de la llista (paràgrafs, blocs de codi) forma part de l'enunciat i
es mostra sempre. Una opció també pot ser un bloc de codi: escriu `[x]` o `[ ]` sol en la línia
i el bloc indentat a sota.

`````markdown
/// quiz | Què mostra aquest codi?
```python
print(len("hola"))
```

- [ ]
    ```python
    "hola"
    ```
- [x]
    ```python
    4
    ```
- [ ]
    ```python
    Error
    ```
///
`````

/// quiz | Què mostra aquest codi?
```python
print(len("hola"))
```

- [ ]
    ```python
    "hola"
    ```
- [x]
    ```python
    4
    ```
- [ ]
    ```python
    Error
    ```
///

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

Com a drecera, si la pregunta comença amb `~`, el bloc barreja les opcions:

````markdown
/// quiz | ~ Quin d'aquests sectors ofereix serveis?
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

## Tipus de pregunta

Cada tipus de pregunta té el seu bloc: `quiz` i `quiz-test` per a la selecció, i `quiz-text`,
`quiz-match`, `quiz-order` i `quiz-essay` per a la resta.

Tots els blocs comparteixen aquestes característiques:

- __Argument__: (opcional) la pregunta, en una línia. Si no n'hi ha, tot el que hi ha abans
    de la llista és l'enunciat.
- __Enunciat__: paràgrafs i blocs de codi abans de la llista. Es mostren sempre.
- __`points`__: (opcional) puntuació de la pregunta dins d'un examen. Per defecte és `1`.

### Selecció (`quiz` i `quiz-test`)
Cada opció comença per `[ ]` (incorrecta) o `[x]` (correcta). Amb una sola opció correcta,
la pregunta és de __selecció simple__ i, amb diverses, de __resposta múltiple__. Fora d'un examen,
`quiz-test` es comporta exactament igual que `quiz`.

````markdown
/// quiz-test | ~ Quin d'aquests impostos són directes?
- [x] IRPF
- [ ] IVA
- [x] Impost de societats

Aquesta explicació només es mostra en mode pràctica.
///
````

/// quiz-test | ~ Quin d'aquests impostos són directes?
- [x] IRPF
- [ ] IVA
- [x] Impost de societats

Aquesta explicació només es mostra en mode pràctica.
///

- __`~`__ al principi de la pregunta (o l'opció `shuffle: true`) barreja les opcions.
- Una opció pot ser un bloc de codi: escriu `[x]` o `[ ]` sol en la línia i el bloc indentat a sota.
- Dins d'un examen s'elimina l'explicació i no es marca cap opció com a correcta. En
    les preguntes de resposta múltiple, es demana seleccionar totes les correctes.
- __Correcció__: automàtica. Els errors resten; vegeu [Puntuació](exam.md#puntuacio).

### Resposta curta (`quiz-text`)
L'alumnat escriu una resposta en una línia i prem ++enter++ per comprovar-la. Cada element de la llista és una resposta acceptada.

````markdown
/// quiz-text | Quin és el planeta més gran del sistema solar?
- Júpiter
- Jupiter

Júpiter té una massa més de dues vegades superior a la de tots els altres planetes junts.
///
````

/// quiz-text | Quin és el planeta més gran del sistema solar?
- Júpiter
- Jupiter

Júpiter té una massa més de dues vegades superior a la de tots els altres planetes junts.
///

### Relacionar (`quiz-match`)
Cada element de la llista és una parella `esquerra -> dreta`. L'alumnat tria, per a cada element
de l'esquerra, la dreta corresponent en un desplegable i prem __Comprova__. Les opcions de la dreta es mostren barrejades.

````markdown
/// quiz-match | Relaciona cada país amb la seua capital.
- Portugal -> Lisboa
- Itàlia -> Roma
- Grècia -> Atenes
///
````

/// quiz-match | Relaciona cada país amb la seua capital.
- Portugal -> Lisboa
- Itàlia -> Roma
- Grècia -> Atenes
///

- La separació es fa en el __primer__ `->`; per tant, la part de l'esquerra no pot contindre `->`.
- Es poden repetir textos a la dreta.

### Ordenar (`quiz-order`)
Els elements de la llista s'escriuen en l'__ordre correcte__, però es mostren barrejats. Es poden arrossegar o moure amb les fletxes.

````markdown
/// quiz-order | Ordena les fases del cicle de l'aigua.
- Evaporació: l'aigua passa a vapor per l'escalfor del sol
- Condensació: el vapor forma núvols en refredar-se
- Precipitació: l'aigua torna a la superfície en forma de pluja o neu
///
````

/// quiz-order | Ordena les fases del cicle de l'aigua.
- Evaporació: l'aigua passa a vapor per l'escalfor del sol
- Condensació: el vapor forma núvols en refredar-se
- Precipitació: l'aigua torna a la superfície en forma de pluja o neu
///

- L'ordre barrejat no coincideix mai amb el correcte.
- Si l'alumnat no mou cap element, la pregunta es considera sense contestar.

### Redacció (`quiz-essay`)
L'alumnat escriu una resposta lliure en una àrea de text. No té llista: tot el contingut del bloc
és l'enunciat.

````markdown
//// quiz-essay
Explica amb les teues paraules la diferència entre __temps atmosfèric__ i __clima__,
i posa'n un exemple de cadascun.
////
````

/// exam
    demo: true

//// quiz-essay
Explica amb les teues paraules la diferència entre __temps atmosfèric__ i __clima__,
i posa'n un exemple de cadascun.
////

///

- __`lang`__: (opcional) llenguatge de la resposta (`java`, `sql`, `python`...). Amb un
    llenguatge, la caixa és un editor de codi: ressalta la sintaxi, sagna automàticament i més.
- __`table`__: (opcional) `true` fa que la resposta siga una taula editable, que s'entrega en Markdown.
- __`columns`__: (opcional, amb `table`) noms de les columnes inicials, separats per `|`.
- __`pinned`__: (opcional, amb `table`) nom d'una última columna fixa, que no es pot canviar ni esborrar.
- No té correcció automàtica.

La resposta també pot ser una taula:

````markdown
//// quiz-essay | Completa la taula amb tres països.
    table: true
    columns: País | Capital
    pinned: Observacions
////
````

/// exam
    demo: true

//// quiz-essay | Completa la taula amb tres països.
    table: true
    columns: País | Capital
    pinned: Observacions
////

///

### Resum

| Bloc          | Llista                                  | Fora d'`/// exam` | Correcció                        |
|---------------|-----------------------------------------|-------------------|----------------------------------|
| `quiz`        | Opcions `[ ]` / `[x]`                   | Interactiu        | Immediata (mode pràctica)        |
| `quiz-test`   | Opcions `[ ]` / `[x]`                   | Interactiu        | Automàtica (simple o múltiple)   |
| `quiz-text`   | Respostes acceptades                    | Sense efecte      | Automàtica, tot o res            |
| `quiz-match`  | `esquerra -> dreta`                     | Sense efecte      | Automàtica, parcial              |
| `quiz-order`  | Elements en l'ordre correcte            | Sense efecte      | Automàtica, parcial              |
| `quiz-essay`  | Cap                                     | Sense efecte      | Manual                           |

## Esdeveniment `quiz:answered`

Quan una pregunta es resol, el bloc `quiz` (o `quiz-test`) emet l'esdeveniment `quiz:answered`,
que es propaga pel document. El camp `detail.firstTry` indica si s'ha encertat sense cap error,
de manera que una pàgina pot portar el recompte d'encerts:

```js
document.addEventListener("quiz:answered", function (event) {
  console.log(event.detail.firstTry ? "Encertada a la primera" : "Encertada");
});
```

!!! note "Dins d'un [`/// exam`](exam.md) no s'emet cap esdeveniment: la pregunta no revela si és correcta i només es contesta."
