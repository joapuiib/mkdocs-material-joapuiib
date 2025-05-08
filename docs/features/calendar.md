---
title: Calendar
icon: material/calendar
---
# Calendar
<div class="calendar">
    <div class="month">
      <div class="month-header">
        <div class="cell">May</div>
      </div>

      <div class="month-days">
        <!-- Weekday headers -->
        <div class="cell header">DL</div>
        <div class="cell header">DT</div>
        <div class="cell header">DM</div>
        <div class="cell header">DJ</div>
        <div class="cell header">DV</div>
        <div class="cell header">DS</div>
        <div class="cell header">DG</div>

        <div class="cell"></div>
        <div class="cell"></div>
        <div class="cell ud1">1</div>
        <div class="cell ud2">2</div>
        <div class="cell ud3">3</div>
        <div class="cell weekend">4</div>
        <div class="cell weekend">5</div>

        <div class="cell ud4">6</div>
        <div class="cell ud5">7</div>
        <div class="cell ud6">8</div>
        <div class="cell ud7">9</div>
        <div class="cell exam">10</div>
        <div class="cell holiday">11</div>
        <div class="cell weekend">12</div>
      </div>
    </div>
</div>

```
/// calendar
from: 2024-09-01
to: 2025-06-30
events:
    holidays:
        - "2024-09-10"
        - "2024-09-12"
        - "2024-11-01"
        - "2024-12-06"
        - "2024-12-08"
        - ["2024-12-23", "2025-01-06"]
    ud1:
        - ["2024-09-10", "2024-09-27"]
///
```
