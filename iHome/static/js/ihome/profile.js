function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function showMsg() {
    $.get('api_1_0/userinfo',function (response) {
        if (response.error_no == '0'){
            $('#user-avatar').attr('src', response.data.avatar_url);
            $('#user-name').val(response.data.name);
            // $('#user-mobile').val(response.data.mobile);
        }else if(response.error_no == '4101'){
                location.href = 'login.html'
            }
            else {
                alert(response.error_msg)
            }}
    )
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    // TODO: 在页面加载完毕向后端查询用户的信息
        showMsg()
    // TODO: 管理上传用户头像表单的行为


    $("#form-avatar").submit(function (event) {
        //阻止默认表单的提交功能
        event.preventDefault()
    //    模拟表单提交ajax请求
        $(this).ajaxSubmit({
            url : "api_1_0/users/avatar",
            type : "post",

            contentType:'application/file',
            headers:{"X-CSRFToken":getCookie("csrf_token")},
            success: function (response) {
                if (response.error_no == '0'){
                    // alert(response.data.avatar_url)
                    // $('#user-avatar').attr('src', response.data.avatar_url);
                    showSuccessMsg()
                    showMsg()
                }else if(response.error_no == '4101'){
                    location.href = 'login.html'
                }
                else {
                    alert(response.error_msg)
                }

            }
        })
        
    });

    // TODO: 管理用户名修改的逻辑

    $("#form-name").submit(function (event) {
        //阻止默认表单的提交功能
        event.preventDefault();
    //    模拟表单提交ajax请求
        if(!$('#user-name').val()){
            alert('修改的用户名参数不能为空')
        }
        var params = {
        "name":$('#user-name').val()
        };
        $.ajax({
            url : "api_1_0/users/name",
            type : "put",
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{"X-CSRFToken":getCookie("csrf_token")},
            success: function (response) {
                if (response.error_no == '0'){

                    $('#user-name').val(response.data.name);
                    showMsg()
                    showSuccessMsg();
                    // $('#user-avatar').attr('src', response.data.avatar_url);
                }else if(response.error_no == '4101'){
                    location.href = 'login.html'
                }
                else {
                    alert(response.error_msg)
                }

            }
        })

    })
});

