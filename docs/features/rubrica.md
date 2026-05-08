---
title: Rúbrica
icon: material/format-list-checks
---

# Rúbrica

Component per a generar rúbriques d'avaluació amb nivells i criteris.

```md
/// rubric
levels:
  - Excel·lent
  - Bé
  - Acceptable
  - Insuficient

criteria:
  - title: Claredat
    description: L'escriptura és clara i fàcil d'entendre.
    score: 10 punts
    levels:
      - title: L'escriptura és excel·lent.
        score: 10 punts
      - title: L'escriptura està bé.
        score: 7 punts
        checked: true
      - title: L'escriptura és acceptable.
        score: 3 punts
      - title: L'escriptura és insuficient.
        score: 0 punts
///
```

/// rubric
levels:
  - Excel·lent
  - Bé
  - Acceptable
  - Insuficient

criteria:
  - title: Claredat
    description: L'escriptura és clara i fàcil d'entendre.
    score: 10 punts
    levels:
      - title: L'escriptura és excel·lent.
        score: 10 punts
      - title: L'escriptura està bé.
        score: 7 punts
        checked: true
      - title: L'escriptura és acceptable.
        score: 3 punts
      - title: L'escriptura és insuficient.
        score: 0 punts
///
