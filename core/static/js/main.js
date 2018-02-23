$(window).on("resize", function() {
    // On small screens, the nav links should disappear when the page is resized
    if ($("#mobile-menu-icon").is(":visible")) {
        $("#nav-links").hide();
    }
    $("#nav-links").removeAttr("style");
});


$(document).ready(function() {
    $("#mobile-menu-icon").on("click", function() {
        if ($("#nav-links").is(":hidden")) {
            $("#nav-links").slideToggle("fast");
        } else {
            $("#nav-links").slideToggle("fast", function() {
                $("#nav-links").removeAttr("style");
            });
        }
    });
});
