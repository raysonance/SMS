
"use strict";
$(document).ready(function() {
  //Smooth Scroll
  // Select all links with hashes
  $('a[href*="#"]')
    // Remove links that don't actually link to anything
    .not('[href="#"]')
    .not('[href="#0"]')
    .not('[href="#Section1"]')
    .not('[href="#Section2"]')
    .not('[href="#collapse1"]')
    .not('[href="#collapse2"]')
    .not('[href="#collapse3"]')
    .click(function (event) {
      // On-page links
      if (
        location.pathname.replace(/^\//, "") ==
          this.pathname.replace(/^\//, "") &&
        location.hostname == this.hostname
      ) {
        // Figure out element to scroll to
        var target = $(this.hash);
        target = target.length
          ? target
          : $("[name=" + this.hash.slice(1) + "]");
        // Does a scroll target exist?
        if (target.length) {
          // Only prevent default if animation is actually gonna happen
          event.preventDefault();
          $("html, body")
            .stop()
            .animate(
              {
                scrollTop: target.offset().top,
              },
              2500,
              "easeInOutExpo",
              function () {
                // Callback after animation
                // Must change focus!
                var $target = $(target);
                $target.focus();
                if ($target.is(":focus")) {
                  // Checking if the target was focused
                  return false;
                } else {
                  $target.attr("tabindex", "-1"); // Adding tabindex for elements not focusable
                  $target.focus(); // Set focus again
                }
              }
            );
        }
      }
    });

  //	Back Top Link

  var offset = 200;
  var duration = 500;
  var backtotop = $(".back-to-top");
  $(window).scroll(function () {
    if ($(this).scrollTop() > offset) {
      backtotop.fadeIn(400);
    } else {
      backtotop.fadeOut(400);
    }
  });

  //Owl-carousels

  $("#blog-slider").owlCarousel({
    dots: true,
    loop: true,
    margin: 10,
    autoplay: false,
    nav: true,
    navText: [
      "<i class='fa fa-arrow-left'></i>",
      "<i class='fa fa-arrow-right'></i>",
    ],
    responsive: {
      1: {
        items: 1,
      },
      1200: {
        items: 3,
      },
    },
  });
  $("#team-slider").owlCarousel({
    dots: true,
    loop: true,
    margin: 50,
    nav: true,
    navText: [
      "<i class='fa fa-arrow-left'></i>",
      "<i class='fa fa-arrow-right'></i>",
    ],
    responsive: {
      1: {
        items: 1,
      },
      600: {
        items: 2,
      },
      900: {
        items: 3,
      },
    },
  });
  $("#services-slider").owlCarousel({
    dots: true,
    loop: true,
    margin: 30,
    autoplay: false,
    nav: true,
    navText: [
      "<i class='fa fa-arrow-left'></i>",
      "<i class='fa fa-arrow-right'></i>",
    ],
    responsive: {
      1: {
        items: 1,
      },
      767: {
        items: 2,
      },
      1000: {
        items: 3,
      },
    },
  });
  $("#featured-icons").owlCarousel({
    dots: true,
    loop: true,
    margin: 50,
    autoplay: true,
    nav: true,
    navText: [
      "<i class='fa fa-arrow-left'></i>",
      "<i class='fa fa-arrow-right'></i>",
    ],
    responsive: {
      1: {
        items: 1,
      },
      600: {
        items: 2,
      },
      1000: {
        items: 3,
      },
    },
  });
  $("#testimonial-slider").owlCarousel({
    loop: true,
    dots: true,
    autoplay: false,
    nav: true,
    navText: [
      "<i class='fa fa-arrow-left'></i>",
      "<i class='fa fa-arrow-right'></i>",
    ],
    responsive: {
      1: {
        items: 1,
      },
      767: {
        items: 2,
      },
    },
  });

  //Load Skrollr

  //Load Skrollr

  $(function () {
    // initialize skrollr if the window width is large enough
    if ($(window).width() > 991) {
      var skr0llr = skrollr.init({
        forceHeight: false,
      });
    }
  });

  //Dropdown nav on Hover

  if ($(window).width() > 991) {
    var dropmenu = $(".dropdown-menu");
    $(".dropdown").hover(
      function () {
        $(this).find(dropmenu).stop(true, true).delay(100).fadeIn(500);
      },
      function () {
        $(this).find(dropmenu).stop(true, true).delay(100).fadeOut(500);
      }
    );
  }
}); // end document ready


//On Click  function
	$(document).on('click',function(){

		//Navbar toggle
		$('.navbar .collapse').collapse('hide');

	})

// Window load function

$(window).load(function() {

    // Page Preloader

    $("#preloader").slideUp("slow");

    // Pretty Photo

    $("a[data-gal^='prettyPhoto']").prettyPhoto({
        hook: 'data-gal'
    });
    ({
        animation_speed: 'normal',
        opacity: 1,
        show_title: true,
        allow_resize: true,
        counter_separator_label: '/',
        theme: 'light_square',
        /* light_rounded / dark_rounded / light_square / dark_square / facebook */
    });

    //Isotope Nav Filter

    $('.category a').on('click', function() {
        $('.category .active').removeClass('active');
        $(this).addClass('active');

        var selector = $(this).attr('data-filter');
        $container.isotope({
            filter: selector,
            animationOptions: {
                duration: 750,
                easing: 'linear',
                queue: false
            }
        });
        return false;
    });

    //Isotope

    var $container = $('#lightbox');
    $container.isotope({
        filter: '*',
        animationOptions: {
            duration: 750,
            easing: 'linear',
            queue: false,
            layoutMode: 'masonry'
        }

    });
	$(window).smartresize(function() {
        $container.isotope({
            columnWidth: '.col-sm-3'
        });
    });


}); // end window load
