---
title: Examen
icon: lucide/clipboard-check
---

# Examen

Extensió de [Pymdownx Blocks][blocks] que permet fer un examen en el navegador. Utilitza
blocs de pregunta (`/// quiz-test`, `/// quiz-text`...) basats en [`/// quiz`](quiz.md), però el bloc `/// exam` __elimina la solució__ i les
explicacions de l'HTML generat. L'alumnat exporta les respostes en un fitxer xifrat que el
professorat desxifra i corregeix en local.

[blocks]: https://facelessuser.github.io/pymdown-extensions/extensions/blocks/

## Funcionament

1. El professorat genera una parella de claus. La __clau pública__ es publica amb la pàgina
    i la __clau privada__ es guarda fora del repositori.
2. L'alumnat contesta l'examen en el navegador i prem __Acaba l'examen__. El navegador
    xifra les respostes amb la clau pública i descarrega un fitxer
    `examen-<id>-<nom>.enc.txt`. Després esborra les respostes guardades i, si l'examen està
    protegit pel plugin `access`, tanca la sessió.
3. L'alumnat puja el fitxer a l'aula virtual.
4. El professorat descarrega les entregues i les corregeix amb la ferramenta `examtool`, que
    llig la solució del fitxer Markdown de l'examen.

!!! warning "El xifratge protegeix la solució, no impedeix que l'alumnat consulte apunts ni que modifique les respostes abans d'exportar-les."

## Configuració

Cal afegir l'extensió `quiz` i excloure `quiz` i `exam` de `inline_blocks`:

```yaml title="properdocs.yml"
markdown_extensions:
  - inline_blocks:
      exclude_blocks: [html, quiz, quiz-test, quiz-text, quiz-match, quiz-order, quiz-essay, exam]
  - material_joapuiib.extensions.quiz:
      public_key: MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...
```

- __`public_key`__: clau pública en format _base64_ (SPKI) o PEM, o la ruta d'un fitxer que la
    continga (relativa a la carpeta des d'on s'executa `properdocs`). Es pot sobreescriure
    en cada examen amb l'opció `key`.

### Generació de les claus

```bash
python -m material_joapuiib.examtool keygen --private examen.key
```

L'ordre guarda la clau privada en `examen.key` i mostra la clau pública, que cal copiar a
`public_key`.

!!! danger "No pugues la clau privada al repositori. Qui la tinga pot desxifrar totes les entregues."

## Plantilla `quiz.html`

Amb `template: quiz.html` en el front matter, la pàgina de l'examen mostra un quadre fix a la
dreta (a dalt, en pantalles estretes) amb:

- el __nom i cognoms__ de l'alumnat;
- el __progrés__ (preguntes contestades) i una quadrícula amb tots els números de pregunta: els
    contestats es marquen i un clic porta a la pregunta. Si l'examen té seccions (`##`), els
    números s'agrupen per secció;
- el botó __Acaba l'examen__, que demana confirmació i avisa si queden preguntes sense contestar.

Cada pregunta mostra el seu número («Pregunta 7»), la seua puntuació i una marca quan està
contestada. Les respostes es guarden com a esborrany en el navegador mentre es contesta. La plantilla
estén `exam.html`, així que manté els estils que impedeixen copiar el text, i mostra la __portada__ si la pàgina o el tema en defineixen una.

```yaml title="docs/examens/quiz.md"
---
template: quiz.html
title: Test UD1-4
---
```

## Sintaxi

El bloc `/// exam` envolta les preguntes. L'argument és el títol i l'opció `id` identifica
l'examen (per defecte, el títol sense accents ni espais).

````markdown
/// exam | Examen de la UD4
    id: ud4

//// quiz-test | Per quin port escolta __PostgreSQL__?
- [ ] `8069`
- [x] `5432`

////

///
````

- __`demo`__: (opcional) `true` mostra només les preguntes, sense el camp del nom ni el botó
    d'acabar. S'utilitza per als exemples de la documentació.
- __`lockdown`__: (opcional) `true` activa el __control anticòpia__. En obrir la pàgina, l'examen
    queda ocult fins que l'alumnat accepta unes condicions en un avís; si les rebutja, no pot fer
    l'examen. Mentre dura, es bloquegen les ordres de copiar, retallar, apegar i el menú
    contextual, i es demana la pantalla completa.

    > JavaScript no pot impedir que una persona copie des d'un altre dispositiu. Per això el
    > control __registra__ cada eixida de la finestra o de la pantalla completa i inclou el
    > registre en el fitxer entregat. [`examtool`](#correccio) mostra el nombre d'incidències de
    > cada entrega.

- __`unlock`__: (opcional, amb `lockdown`) contrasenya del professorat. Amb ella, la __primera
    incidència__ (eixir de la finestra o de la pantalla completa, copiar, retallar o apegar)
    bloqueja l'examen: es mostra la llista d'incidències i no es pot continuar fins que el
    professorat escriu la contrasenya. El bloqueig es manté si es recarrega la pàgina, i
    `examtool` detalla les incidències de cada entrega.

    També es registra com a incidència obrir les eines de desenvolupador.

    En la vista d'autor de `properdocs serve` i per a l'usuari amb el rol `bypass` del plugin
    `access`, el control anticòpia no s'activa.

    També es registra, __sense bloquejar__ l'examen, el nom de les extensions del navegador que
    modifiquen la pàgina (correctors, traductors...). Només se'n poden detectar algunes, i
    l'avís inicial n'informa l'alumnat.

    > Utilitza una contrasenya llarga: la comprovació es fa al navegador.

!!! important "Les preguntes van niades dins d'`/// exam`, així que utilitzen una barra més: `////`."

## Previsualització amb solucions

Amb `properdocs serve` i la vista d'autor del plugin `access`, el panell de l'examen mostra el
botó __Mostra les respostes__. En activar-lo, es ressalten les opcions correctes i les altres
preguntes mostren la seua solució (les de redacció no en tenen).

!!! danger "Les solucions només es mostren amb `properdocs serve`. Una compilació de producció no en conté cap."

## Tipus de pregunta

Cada tipus de pregunta té el seu bloc. La sintaxi de cadascun, amb exemples, està en
[Tipus de pregunta](quiz.md#tipus-de-pregunta).

| Bloc            | Llista del cos                                      | Correcció                                         |
|-----------------|-----------------------------------------------------|---------------------------------------------------|
| `quiz-test`     | Opcions `[ ]` / `[x]`                               | Automàtica. Amb diverses `[x]`, resposta múltiple |
| `quiz-text`     | Cada element és una resposta acceptada              | Automàtica, sense distingir majúscules            |
| `quiz-match`    | Elements `esquerra -> dreta`                        | Automàtica, per parelles correctes                |
| `quiz-order`    | Elements en l'ordre correcte (es mostren barrejats) | Automàtica, per posicions correctes               |
| `quiz-essay`    | Cap                                                 | Manual                                            |

### Puntuació

Cada pregunta val `points` punts (1 per defecte) i les respostes incorrectes resten:

| Pregunta         | Encert                          | Cada error                                                        |
|------------------|---------------------------------|-------------------------------------------------------------------|
| Selecció simple  | Tots els punts                  | Resta `1/(n-1)` dels punts (`n` opcions). Sense contestar, 0.     |
| Resposta múltiple| `1/k` per cada correcta triada  | Resta `1/k` (`k` correctes), sense baixar de 0 en la pregunta.    |
| Resposta curta   | Tots els punts                  | No resta.                                                         |
| Relacionar       | `1/n` per cada parella correcta | Cada parella incorrecta anul·la una correcta. Sense triar, no resta. |
| Ordenar          | `1/n` per cada element al seu lloc | Cada element fora de lloc anul·la un de correcte, sense baixar de 0. |

La nota total no baixa mai de 0. Cada pregunta mostra com resta un error.

## Correcció

```bash
python -m material_joapuiib.examtool grade \
    --private examen.key \
    --source docs/examens/ud4.md \
    --submissions entregues.zip \
    --csv notes.csv \
    --essays redaccions/
```

- __`--submissions`__: carpeta o fitxer `.zip` amb els fitxers pujats (per exemple, el
    que descarrega l'aula virtual amb totes les entregues).
- __`--csv`__: (opcional) taula amb la nota de cada pregunta.
- __`--essays`__: (opcional) carpeta on es guarda un fitxer per estudiant amb les respostes
    de redacció, per corregir-les a mà.
- __`--exam`__: (opcional) identificador de l'examen, si el fitxer en té més d'un.

La ferramenta ignora els fitxers que no són entregues vàlides i les d'un altre examen, i avisa
per la consola.
