$document.ready(function() {

var $flash = $('div.flash');
if ($flash.length){
    $('<a class="flash_close">Cerrar</a>')
    .appendTo($flash)
    .click(function(){
        var $el = $(this).hide().parents('div.flash');
        $el.animate({
            'opacity': 0,
            'height': 0,
            'marginTop': 0,
            'marginBottom': 0,
            'paddingTop': 0,
            'paddingBottom': 0
        }, 
        400, function(){ 
            $el.remove();
            $document.trigger('flash_closed');
        });
    });
}
