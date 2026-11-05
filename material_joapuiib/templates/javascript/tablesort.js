document$.subscribe(function() {
  var tables = document.querySelectorAll("article div.table-sortable table")
  tables.forEach(function(table) {
    if (table.dataset.tablesortReady) return
    table.dataset.tablesortReady = "true"
    new Tablesort(table)
  })
})
