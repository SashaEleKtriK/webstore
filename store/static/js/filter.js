function loadJson(selector) {
  return JSON.parse($(selector).attr('data-json'));
}
$(document).ready(function(){


    var data = loadJson("#jsonCategory");
    for (let i = 0; i < data.length; i++){
        var name = data[i]['name'];
        var id = data[i]['id'];
        $(".hidden_filter").append(`<li class="filter-li" id="${id}"><a>${name}</a></li>`);
    }
    $("#filter_btn").on("click", function(e){
            if($(e.currentTarget).hasClass('off')){
                $(e.currentTarget).removeClass('off');
                $(e.currentTarget).addClass('on');
                $("#scat").removeClass("hidden_sub_filter")
                $("#scat").addClass('sub_filter')
                $("#cat").removeClass("hidden_filter")
                $("#cat").addClass('filter')

            }
           else if($(e.currentTarget).hasClass('on')){
                $(e.currentTarget).removeClass('on');
                $(e.currentTarget).addClass('off');
                $(".sub_filter").html("")
                $('#scat').removeClass('sub_filter')
                $('#scat').addClass('hidden_sub_filter')
                $("#cat").removeClass('sub_filter')
                $("#cat").addClass('hidden_filter')
            }
        })
    $(".filter-li").on("click", function(e){
        curId = $(e.currentTarget).attr("id");
        var data = loadJson("#jsonSubCategory");
        $(".sub_filter").html("")
        for (let i = 0; i < data.length; i++){
            var category = data[i]['category']
            if (category == curId){
                var name = data[i]['name'];
                var id = data[i]['id'];
                $(".sub_filter").append(`<li class="filter-li" id="${id}"><a href="/?filter=${id}">${name}</a></li>`)
            }
        }
    })
})
