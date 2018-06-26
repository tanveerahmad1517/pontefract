$(window).on("resize", function() {
    // On small screens, the nav links should disappear when the page is resized
    if ($("#mobile-menu-icon").is(":visible")) {
        $("#nav-links").hide();
    }
    $("#nav-links").removeAttr("style");
});


$(document).ready(function() {
    $("#mobile-menu-icon").on("click", function() {
        var SPEED = 100;
        if ($("#nav-links").is(":hidden")) {
            $("#nav-links").slideToggle(SPEED);
        } else {
            $("#nav-links").slideToggle(SPEED, function() {
                $("#nav-links").removeAttr("style");
            });
        }
    });

    $(".notes-button").each(function(x) {
        $(this).click(function(e) {
            var row = $(this).parent().parent();
            var sessionId = $(row).attr("data-id");
            if ($('*[data-session-id="' + sessionId + '"]').length) {
                $('*[data-session-id="' + sessionId + '"]').slideToggle("fast", function() {
                    $(this).remove();
                })
            } else {
                var note = $(this).attr("data-notes");
                $("<span data-session-id='" + sessionId + "'>" + note + "</span>").insertAfter(row).hide().slideDown("fast");
            }

        });
    })
});
