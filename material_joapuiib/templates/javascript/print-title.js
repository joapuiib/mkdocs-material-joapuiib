var printTitle = ""
var previousTitle = ""
var isPrinting = false
var pendingRestore = false

function updatePrintTitle() {
  var printTitleMeta = document.querySelector('meta[name="print-title"]')
  printTitle = printTitleMeta ? printTitleMeta.content.trim() : ""
}

function setPrintTitle() {
  if (!printTitle || isPrinting) {
    return
  }

  previousTitle = document.title
  document.title = printTitle
  isPrinting = true
  pendingRestore = false
}

function restoreTitle() {
  if (!isPrinting) {
    return
  }

  document.title = previousTitle
  isPrinting = false
  pendingRestore = false
}

function queueRestoreTitle() {
  if (!isPrinting) {
    return
  }

  pendingRestore = true
}

function restoreTitleIfPending() {
  if (pendingRestore) {
    restoreTitle()
  }
}

if (typeof document$ !== "undefined" && document$.subscribe) {
  document$.subscribe(updatePrintTitle)
} else {
  updatePrintTitle()
}

window.addEventListener("beforeprint", setPrintTitle)
window.addEventListener("afterprint", queueRestoreTitle)
window.addEventListener("focus", restoreTitleIfPending)
window.addEventListener("pointerdown", restoreTitleIfPending)
window.addEventListener("keydown", restoreTitleIfPending)

if (window.matchMedia) {
  var printMediaQuery = window.matchMedia("print")
  var handlePrintChange = function(event) {
    if (event.matches) {
      setPrintTitle()
    } else {
      queueRestoreTitle()
    }
  }

  if (typeof printMediaQuery.addEventListener === "function") {
    printMediaQuery.addEventListener("change", handlePrintChange)
  } else if (typeof printMediaQuery.addListener === "function") {
    printMediaQuery.addListener(handlePrintChange)
  }
}

document.addEventListener("visibilitychange", function() {
  if (document.visibilityState === "visible") {
    restoreTitleIfPending()
  }
})
