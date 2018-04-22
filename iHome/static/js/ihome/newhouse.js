function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');

    // TODO: 在页面加载完毕之后获取区域信息
    $.get('api_1_0/areas',function (response) {
        if (response.error_no == "0"){
            //
            // $.each(response.data, function (i,area) {
            //     $(".area-list").append('<option value="'+area.aid+'">'+area.aname+'</option>')
            //     alert('12')
            // })
            var html = template("areas-tmpl",{"areas":response.data})
            $("#area-id").html(html)

        }else if(response.error_no == '4101'){
            location.href = 'login.html'
        }
        else {
            alert(response.error_msg)
        }
    })
    // TODO: 处理房屋基本信息提交的表单数据
    //0.监听表单提交行行行为,并禁用用默认的提交
    $('#form-house-info').submit(function (event) {
        event.preventDefault();
    //1.准备封装参数的字典对象
    //2.收集表单中所有需要提交的数据
    //3.将表单中的被选中的checkbox筛选出来
    //4.将设备列列表添加到params中
        var params = {}
        var facilities= []
        $(this).serializeArray().map(function (obj) {
            params[obj.name] = obj.value
        })
        $(":checkbox:checked[name='facility']").each(function (i,elm) {
            facilities[i] = elm.value
        })
        params['facility'] = facilities

// 2.发送请求
        $.ajax({
            url: '/api_1_0/houses',
            type: 'post',
            data: JSON.stringify(params),
            contentType: 'application/json',
            headers: {'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
            if (response.error_no == '0') {

                // 隐藏发布房屋的界面面
                $('#form-house-info').hide()
                // 展示上传房屋图片片界面面
                $("#form-house-image").show()

                $("#house-id").val(response.data.house_id)

            } else {
            alert(response.error_msg);
            }
            }
        });

    });

    //2.收集表单中所有需要提交的数据
    //3.将表单中的被选中的checkbox筛选出来
    //4.将设备列列表添加到params中

    // TODO: 处理图片表单的数据
    $("#form-house-image").submit(function (event) {
        event.preventDefault()

        $(this).ajaxSubmit({
            url:"/api_1_0/houses/image",
            type:"post",
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
            if (response.error_no == '0') {
            // 把上传的图片片展示到界面面上
            $('.house-image-cons').append('<img src="'+response.data.house_image_url+'">')
            } else if (response.error_no == '4101') {
            location.href = '/';
            } else {
            alert(response.error_msg);
            }
            }
        })
    })
})