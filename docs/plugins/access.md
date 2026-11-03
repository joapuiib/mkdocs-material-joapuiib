---
title: Access
icon: material/lock
alias: access
---

# Access

Plugin que controla l'accés al contingut: protegeix pàgines amb __contrasenya__, defineix __usuaris__ i __grups__, i limita la visibilitat a una __finestra de temps__.

El lloc és estàtic, així que no hi ha cap servidor que decidisca qui pot veure què. Per això el contingut es __xifra durant la construcció__ i es desxifra al navegador de la persona visitant quan aporta una contrasenya o inicia la sessió.

!!! warning "Límits de la protecció"
    - Les __contrasenyes__ i els __usuaris__ protegeixen de debò el contingut de la pàgina.
    - Les __dates d'inici i final__ són orientatives: les valida el rellotge del navegador i no impedeixen que algú amb coneixements tècnics llija el contingut.
    - Els __fitxers adjunts__ (imatges, PDF, ZIP...) no es xifren. Una pàgina protegida no protegeix els fitxers que enllaça.
    - Qualsevol persona pot descarregar els fitxers de claus i provar contrasenyes sense connexió. Utilitza contrasenyes llargues.

## Configuració

```yml title="properdocs.yml"
plugins:
  - material-joapuiib/access:
      timezone: Europe/Madrid
      users:
        professor:
          password: !ENV PROFESSOR_PASSWORD
          groups: [professors]
        maria:
          password: !ENV MARIA_PASSWORD
          groups: [dam1]
      groups:
        professors: {}
        alumnes: {}
        dam1:
          inherits: [alumnes]
      rules:
        - pattern: dam1/examens/**
          allow: [dam1]
          bypass: [professors]
```

- __`salt`__: (opcional) text que fa úniques les claus del lloc. Per defecte s'utilitza el `site_name`, així que no cal definir-lo. Si canvies el `salt` (o el `site_name`, quan no s'ha definit), es tanca la sessió de tothom i les contrasenyes guardades deixen de funcionar.
- __`timezone`__: zona horària per a les dates sense zona (per defecte, `UTC`). També és la zona en què es mostren les dates a l'alumnat, amb l'abreviatura (per exemple, `CET`).
- __`users`__: usuaris amb `password` i els `groups` als quals pertanyen.
- __`users_file`__: fitxer YAML amb més usuaris, per a no escriure les contrasenyes al repositori.
- __`groups`__: grups. Amb `inherits`, els membres hereten els permisos dels grups indicats.
- __`rules`__: regles d'accés per patró (vegeu [Regles](#regles)).
- __`nav`__: com es mostren les pàgines protegides al menú.

    ??? info "Valors de `nav`"

        | Valor  | Significat                                       |
        |--------|--------------------------------------------------|
        | `lock` | Es mostra amb una icona de cadenat (per defecte) |
        | `show` | Es mostra com una pàgina normal                  |
        | `hide` | S'amaga del menú                                 |

- __`exclude`__: on no apareixen les pàgines protegides. Per defecte `[search, social]`, és a dir, ni al cercador ni a les targetes socials.
- __`remember_days`__: durada, en dies, de l'opció «Recorda'm» (per defecte, 30).
- __`share_links`__: permet copiar un enllaç que desbloqueja la pàgina (per defecte, `true`).
- __`strings`__: substitueix els textos de la interfície (vegeu [Textos de la interfície](#textos-de-la-interficie)).

## Textos de la interfície

Tots els missatges que mostra el plugin es poden canviar amb l'opció `strings`, indicant només les claus que es volen substituir. Alguns textos admeten __marcadors__ entre claus, que se substitueixen pel valor corresponent.

```yaml title="properdocs.yml"
plugins:
  - material-joapuiib/access:
      strings:
        locked_text: "Aquest examen està protegit."
        window_until: "L'examen es pot fer fins al {end}."
```

??? info "Textos amb marcadors"

    | Clau                 | Marcadors                | Quan es mostra                                              |
    |----------------------|--------------------------|-------------------------------------------------------------|
    | `window_range`       | `{start}`, `{end}`       | contingut fora de la finestra, amb inici i final            |
    | `window_from`        | `{start}`                | contingut fora de la finestra, només amb inici              |
    | `window_until`       | `{end}`                  | contingut fora de la finestra, només amb final              |
    | `countdown`          | `{time}`                 | compte enrere abans de l'inici (`3d 04:05:06`)              |
    | `unlocked_exception` | `{start}`, `{end}`, `{range}` | accés amb `bypass` fora de la finestra                 |
    | `not_allowed`        | `{user}`                 | l'usuari no té accés a la pàgina                            |
    | `not_allowed_section`| `{user}`                 | l'usuari no té accés a la secció                            |

    - Els textos de la finestra de temps es mostren també com a etiqueta d'accessibilitat de la línia d'icones d'inici i final.
    - `{range}` és `{start} - {end}`, o `des del {start}` / `fins al {end}` si només hi ha una de les dues dates.

## Regles

Cada regla té un `pattern` amb la mateixa sintaxi que `exclude_docs` i les claus següents. Les regles s'apliquen __en ordre__, i després s'hi afegeix l'`access` de la capçalera de la pàgina.

| Clau              | Significat                                                           |
|-------------------|----------------------------------------------------------------------|
| `allow`           | usuaris o grups amb accés (`*` són tots els usuaris)                 |
| `deny`            | usuaris o grups que perden l'accés concedit abans                    |
| `password`        | contrasenya (o llista) que desbloqueja la pàgina                     |
| `bypass`          | usuaris o grups que hi accedeixen també fora de la finestra de temps |
| `bypass_password` | contrasenya que desbloqueja la pàgina fora de la finestra de temps   |
| `start`, `end`    | data i hora en què el contingut està disponible                      |
| `nav`             | substitueix l'opció global `nav` per a la pàgina                     |
| `author`          | la pàgina només existeix en mode de desenvolupament                  |

Cal tindre en compte:

- __`deny`__ s'aplica a la llista d'usuaris acumulada fins a aquell moment, de manera que una regla posterior pot tornar a concedir l'accés. Una pàgina amb `deny` necessita algun `allow`, `bypass` o `password`; si no, la construcció falla.
- __`deny`__ no revoca una contrasenya de pàgina que la persona ja conega.
- __`bypass`__ implica `allow`.
- Una pàgina amb només `start` o `end` queda oberta a tothom dins de la finestra.

### Protegir una pàgina des de la capçalera

```yaml title="docs/examen.md"
---
access:
  password: "1234"
  bypass: [professors]
  start: 2026-11-10T09:00
  end: 2026-11-10T11:00
---
```

Els valors de la capçalera se sumen als de les regles del `properdocs.yml`.

## Seccions protegides

No cal protegir la pàgina sencera: amb un bloc `access` es xifra només una part del contingut, per exemple la solució d'un exercici. La resta de la pàgina continua sent pública.

````markdown
/// access
    password: "1234"
    bypass: professors
    end: 2026-11-10T11:00

## Solució

Contingut protegit.
///
````

El bloc admet les opcions `allow`, `deny`, `bypass`, `password`, `bypass_password`, `start` i `end`, amb el mateix significat que en les [regles](#regles). Els usuaris i els grups es poden separar amb comes (`allow: professors, maria`).

!!! warning "Tingues en compte els següents aspectes:"
    - Una secció només aplica les seues pròpies opcions: no hereta les regles ni l'`access` de la pàgina.
    - Els títols de dins de la secció __no apareixen__ a la taula de continguts.
    - Les seccions es poden niar, i dins d'una pàgina ja protegida també funcionen.

## Inici i tancament de la sessió

Si hi ha usuaris, la capçalera mostra un botó per a **iniciar la sessió**. La sessió es guarda al navegador i, si es marca «Recorda'm», dura `remember_days` dies. Si no, desapareix en tancar la pestanya.

Les pàgines desbloquejades amb una __contrasenya de pàgina__ mostren una barra amb dos botons: __Tanca la sessió d'aquesta pàgina__, que oblida aquella contrasenya, i __Copia l'enllaç d'accés__, que genera un enllaç que desbloqueja la pàgina sense demanar la contrasenya.

!!! tip "Un enllaç d'accés equival a la contrasenya. Comparteix-lo només amb qui haja de veure la pàgina."

## Mode de desenvolupament

Amb `properdocs serve`, el contingut protegit es mostra complet i apareix una barra inferior que permet __previsualitzar com a__ qualsevol usuari o com a persona anònima. Així es comprova que cada regla fa el que s'espera abans de publicar.

```bash
ACCESS_SERVE=gate properdocs serve
```

Amb `serve: gate` (o la variable `ACCESS_SERVE=gate` de l'exemple de la configuració d'aquest lloc), les pàgines apareixen bloquejades com al lloc publicat.

## Exemples

Aquest lloc defineix els usuaris de demostració `professor`, `alumne` i `maria`, amb la seua mateixa paraula com a contrasenya.

- [Examen](../features/examen.md): secció protegida amb contrasenya `1234`, finestra de temps i accés d'excepció per al professorat.
- [Pàgina privada](../features/pagina_privada.md): pàgina visible només per al grup `professors`.
- [Seccions protegides](../features/seccions_protegides.md): pàgina pública amb una secció que es desbloqueja amb la contrasenya `1234` o amb l'usuari `professor`.
