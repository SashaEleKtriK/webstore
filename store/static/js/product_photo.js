$(document).ready(function(){
    $(".prod_img_page").on("click", function(e){
        $(e.currentTarget).attr("id")
        var res =getImg($(e.currentTarget))
        console.log(res)
        $("#main_photo").attr("src", `${res}`);
    })
})
function getImg(div){
    var bg = $(div).css("background-image");
    var res = bg.substring(16, bg.length - 2);
    var separator = '/';
    var separated_array = res.split(separator);
    var len = separated_array.length;
    res = "../" + separated_array[len-3] + separator + separated_array[len-2]+separator+separated_array[len-1];
    return res;
}