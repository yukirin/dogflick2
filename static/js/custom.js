
jQuery.event.add(window, "load", function() {
  var pageH = $('#gallery').height();
  var $photos = $('#thumbnails');
  $photos.imagesLoaded(function() {
    $photos.masonry({
      columnWidth: '.thumb',
      itemSelector: '.thumb',
    });
  });
  $('#fade').css('height', pageH).delay(900).fadeOut(800);
  $('#loader').delay(600).fadeOut(300);
  $('#gallery').css('display', 'block');
});

