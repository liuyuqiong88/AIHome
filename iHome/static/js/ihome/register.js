function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}
var uuid = "";
// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    // 1.获取uuid
    uuid = generateUUID();

    // 2.拼接带有uuid的请求地址
    var img_url = "/api_1_0/image_code?uuid=" +uuid;


    // > 标签选择器，表示寻找父节点的子节点
    // '空格' ： 标签选择器，表示寻找父节点的子节点，如果一级找不见，自动寻找下一级，直到找到为止

    $('.image-code>img').attr('src',img_url);
}

function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".phonecode-a").removeAttr("onclick");
    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    } 
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    // TODO: 通过ajax方式向后端接口发送请求，让后端发送短信验证码

    var params = {
        "uuid" :uuid,
        "imageCode" :imageCode,
        "mobile" : mobile,
    }
    $.ajax({
        url:"api_1_0/send_sms_code",　　
        type:'post',
        data:JSON.stringify(params),
        headers:{'X-CSRFToken':getCookie('csrf_token')},
        contentType:"application/json",
        
        success:function (response) {

            if (response.error_no == '0'){
                                // 发送成功后，进行倒计时
                var num = 60;
                var t = setInterval(function ()  {
                    if (num == 0) {
                        // 倒计时完成,清除定时器
                        clearInterval(t);         // 重新生成验证码
                        generateImageCode();
                        // 重置内容
                        $(".phonecode-a").html('获取验证码');
                        // 重新添加点击事件
                        $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    } else {
                        // 正在倒计时，显示秒数
                        $(".phonecode-a").html(num + '秒');
                    }

                    num = num - 1;
                }, 1000);

            }else{
                            // 重新添加点击事件
                $(".phonecode-a").attr("onclick", "sendSMSCode();");
                // 重新生成验证码
                generateImageCode();
                // 弹出错误消息
                alert(response.errmsg);

        }
        }

        }
    )


}

function checkMobile(){
    //判定手机号码格式是否合法
    var mobile = $("#mobile").val();

    // var ret = /^1[2345678][0~9]{9}&/;

    if (!mobile){
        $("#mobile-err span").html("请填写正确手机号")
        $("#mobile-err").show()
    }
}

function checkpassword(){
    //判定两次密码是否一致
    var password = $("#password").val().trim(),password2 = $("#password2").val().trim();

    if (password != password2){
        $("#password2-err span").html("两次密码不一致")
        $("#password2-err").show()
    }
}




$(document).ready(function() {
    generateImageCode();  // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性

    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });

    // TODO: 注册的提交(判断参数是否为空)
    $(".form-register").submit(function (event) {
        event.preventDefault()
        var password = $("#password").val(),password2 = $("#password2").val();
        var mobile = $('#mobile').val(),smscode = $('#phonecode').val();

        if (password != password2){
            $("#password2-err span").html("两次密码不一致")
            $("#password2-err").show()

        }
        params = {
            "mobile":mobile,
            "smscode":smscode,
            "password":password,
        }


        var mobile = $('#mobile'),smscode = $('#phonecode'),password = $("#password");
        $.ajax({
            url : "api_1_0/users",
            type : "post",
            data: JSON.stringify(params),
            contentType:"application/json",
            headers: {"X-CSRFToken":getCookie("csrf_token")},
            success:function (response) {
                if (response.error_no == '0'){
                    location.href = "/"
                }else {
                    alert(response.error_msg)
                }
            }
        })
        })
});
$()
