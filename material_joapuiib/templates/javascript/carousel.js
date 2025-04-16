document$.subscribe(function() {
  let carousels = document.querySelectorAll(".carousel");

  carousels.forEach(function(e) {
    initCarousel(e);
    showSlides(e, 0);
  });
})

function initCarousel(e){
  renderControls(e);
  renderDots(e);
}

function renderControls(e){
  // Create the "prev" link
  const prev = document.createElement('a');
  prev.className = 'prev';
  prev.innerHTML = '&#10094;'; // Left arrow
  prev.onclick = function() {
    plusSlides(e, -1);
  };

  // Create the "next" link
  const next = document.createElement('a');
  next.className = 'next';
  next.innerHTML = '&#10095;'; // Right arrow
  next.onclick = function() {
    plusSlides(e, 1);
  };

  e.append(prev);
  e.append(next);
}

function renderDots(e){
  const dotContainer = document.createElement('div');
  dotContainer.className = 'carousel__dot-container';

  const images = e.querySelectorAll('img');
  for (i = 0; i < images.length; i++) {
    let dot = document.createElement('span');
    dot.className = 'dot';
    dot.onclick = function() {
      plusSlides(e, i);
    };

    dotContainer.append(dot);
  }

  e.after(dotContainer);
}


// Next/previous controls
function plusSlides(e, n) {
  showSlides(e, n);
}

// Thumbnail image controls
function currentSlide(e, n) {
  showSlides(e, n);
}

function showSlides(e, n) {
  let i;
  const images = e.querySelectorAll('img');
  let dots = document.getElementsByClassName("dot");

  n = n % images.length;

  for (i = 0; i < images.length; i++) {
    images[i].style.display = "none";
  }
  //for (i = 0; i < dots.length; i++) {
    //dots[i].className = dots[i].className.replace(" active", "");
  //}
  console.log(images, n);
  images[n].style.display = "block";
  //dots[n-1].className += " active";
}
