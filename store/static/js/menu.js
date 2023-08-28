$(document).ready(function(){
    $(".menu-icon").on("click", function(e){
        if($(e.currentTarget).hasClass('closed')){
            $(".close-menu").fadeIn(50).delay(50).fadeOut(50);
            $(".open-menu").delay(150).fadeIn(100);
            $(".hidden-menu").delay(250).fadeIn(100);
            $(e.currentTarget).removeClass('closed');
            $(e.currentTarget).addClass('opened');
        }
        else if($(e.currentTarget).hasClass('opened')){
            console.log('f')
            $(".open-menu").delay(100).fadeOut(50);
            $(".close-menu").delay(160).fadeIn(100).delay(100).fadeOut(400);
            $(".hidden-menu").fadeOut(100);
            $(e.currentTarget).removeClass('opened');
            $(e.currentTarget).addClass('closed');
        }
        

    })
})