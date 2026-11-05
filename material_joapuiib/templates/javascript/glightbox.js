/* Temporary: remove once mkdocs-glightbox supports instant navigation.
 *
 * The glightbox plugin adds the library and its setup outside the container,
 * and skips pages with `glightbox: false`. If one of those was the first page
 * loaded, this document has no library, so the page needs a full load.
 */
document$.subscribe(function() {
  if (typeof GLightbox === "undefined" && document.querySelector(".glightbox")) {
    location.reload()
  }
})
