---
template: quiz.html
title: Quiz exam
icon: lucide/clipboard-check
---

# Quiz exam

Exemple d'examen amb el bloc [`/// exam`](../extensions/exam.md) i la plantilla `quiz.html`. A la dreta (a dalt, en pantalles estretes) hi ha el quadre amb el nom, el progrés i el botó __Acaba l'examen__. Les respostes no es revelen i es guarden en el navegador mentre es contesta.

!!! note "Aquest examen no té clau pública, així que no es poden exportar les respostes."

````markdown title="docs/examen.md"
---
template: quiz.html
title: Examen d'exemple
---

/// exam | Examen d'exemple
    id: exemple

## Selecció

//// quiz-test | Quina és la capital d'Austràlia?
- [ ] Sydney
- [x] Canberra
- [ ] Melbourne
////

## Resposta curta

//// quiz-text | Quin és el planeta més gran del sistema solar?
- Júpiter
- Jupiter
////

///
````

/// exam | Examen d'exemple
    id: exemple

## Selecció

//// quiz-test | Quina és la capital d'__Austràlia__?
- [ ] Sydney
- [x] Canberra
- [ ] Melbourne
////

//// quiz-test | ~ Quins d'aquests impostos són directes?
- [x] IRPF
- [ ] IVA
- [x] Impost de societats
////

## Resposta curta

//// quiz-text | Quin és el planeta més gran del sistema solar?
- Júpiter
- Jupiter
////

## Relacionar i ordenar

//// quiz-match | Relaciona cada país amb la seua capital.
- Portugal -> Lisboa
- Itàlia -> Roma
- Grècia -> Atenes
////

//// quiz-order | Ordena les fases del cicle de l'aigua.
- Evaporació: l'aigua passa a vapor per l'escalfor del sol
- Condensació: el vapor forma núvols en refredar-se
- Precipitació: l'aigua torna a la superfície en forma de pluja o neu
////

## Redacció

//// quiz-essay | Explica amb les teues paraules la diferència entre temps atmosfèric i clima.
////

//// quiz-essay | Escriu una funció que retorne el major de dos nombres.
    lang: python
////

///
