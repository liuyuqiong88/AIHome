function hrefBack() {
    history.go(-1);
}

// 解析提取url中的查询字符串参数
function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}
function swiper() {
        // TODO: 数据加载完毕后,需要设置幻灯片对象，开启幻灯片滚动
        var mySwiper = new Swiper ('.swiper-container', {
        loop: true,
        autoplay: 2000,
        autoplayDisableOnInteraction: false,
        pagination: '.swiper-pagination',
        paginationType: 'fraction'
    });

}
$(document).ready(function(){
    // 获取详情页面要展示的房屋编号
    var queryData = decodeQuery();
    var houseId = queryData["id"];

    // TODO: 获取该房屋的详细信息
    $.get("/api_1_0/houses/"+houseId,function (response) {
        if (response.error_no == "0"){

            var html_image = template('house-image-tmpl', {'img_urls':response.data.img_urls,'price':response.data.price});
            $('.swiper-container').html(html_image);
            // 图片片轮播
            swiper()
            var html_detail = template("house-detail-tmpl",{"house":response.data})
            $('.detail-con').html(html_detail);

            if (response.data.user_id == response.login_user_id){

                $(".book-house").hide()
            }else {

                $(".book-house").show();


                if (response.login_user_id == '-1'){
                    $(".book-house").attr('href','login.html')
                    // $(".book-house").attr('href','booking.html?hid='+response.data.hid)
                }else {
                    // $(".book-house").attr('href','login.html')
                    $(".book-house").attr('href','booking.html?hid='+response.data.hid)

                }

            }

        }else if(response.error_no == '4101'){
            location.href = 'login.html'
        }
        else {
            alert(response.error_msg)
        }
    });
    // // TODO: 数据加载完毕后,需要设置幻灯片对象，开启幻灯片滚动



});