function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function getAuth() {
    $.get("/api_1_0/users/auth",function (response) {
                if (response.error_no == "0"){

                    $("#real-name").val(response.data.real_name);
                    $("#id-card").val(response.data.id_card);
                    $("#real-name").attr('disabled',true);
                    $("#id-card").attr('disabled',true);
                    $(":submit").hide();

                }else if(response.error_no == '4101'){
                    location.href = 'login.html'
                }
                else {
                    alert(response.error_msg)
                }
            }
    )
}

$(document).ready(function(){
    // TODO: 查询用户的实名认证信息
    getAuth();

    // TODO: 管理实名信息表单的提交行为
    $("#form-auth").submit(function (event) {
        //阻止默认表单的提交功能
        event.preventDefault()

        //获取真实姓名和身份证号码
        var real_name = $("#real-name").val()
        var id_card = $("#id-card").val()

        //判断实姓名和身份证号码是否为空
        if (!real_name){
            $(".error-msg").show()
        }
        if (!id_card){
            $(".error-msg").show()
        }
        //隐藏错误提示的板块
        $(".error-msg").hide();

        var params = {
            "real_name" :real_name,
            "id_card" : id_card ,
        };

        $.ajax({
            url :"/api_1_0/users/auth",
            type:"post",
            data :JSON.stringify(params),
            contentType : "application/json",
            headers : {"X-CSRFToken":getCookie('csrf_token')},
            success : function (response) {
                if (response.error_no == "0"){
                    alert(response.error_msg)
                    showSuccessMsg()
                    $("#real-name").attr('disabled',true);
                    $("#id-card").attr('disabled',true)
                    $(":submit").hide()
                }else if(response.error_no == '4101'){
                    location.href = 'login.html'
                }
                else {
                    alert(response.error_msg)
                }
            }
        })
    })
})