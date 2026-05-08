---
title: Badges
icon: material/information-box
---

# Badges

Plugin que proporciona etiquetes (badges) per a destacar metadades del contingut: paquets, branques de Git, avaluacions i tags.

## Configuració

```yml title="properdocs.yml"
plugins:
  - material-joapuiib/badges
```

## Tipus de badges

!!! example "Experimental"

| Títol | Definició | Resultat |
|-------|-----------|----------|
| __Package__ | `<\!-- md:package ud1.examples -->` | <!-- md:package ud1.examples --> |
| __Avaluació__ | `<\!-- md:eval "__Bloc 1: Títol__" 20% -->` | <!-- md:eval "__Bloc 1: Títol__" 20% --> |
| __Tag__ | `<\!-- md:tag Example -->` | <!-- md:tag Example --> |
| __Branch__ | `<\!-- md:branch main -->` | <!-- md:branch main --> |
