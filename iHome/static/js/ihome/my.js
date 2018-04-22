function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}
//加载个人信息函数
function showMsg() {
    $.get('api_1_0/userinfo',function (response) {
        if (response.error_no == '0'){
            $('#user-avatar').attr('src', response.data.avatar_url);
            $('#user-name').html(response.data.name);
            $('#user-mobile').html(response.data.mobile);
        }else if(response.error_no == '4101'){
                location.href = 'login.html'
            }
            else {
                alert(response.error_msg)
            }}
    )
}

// TODO: 点击推出按钮时执行的函数
function logout() {

    $.ajax({
        url: "api_1_0/session",
        type: "delete",
        headers: {"X-CSRFToken": getCookie("csrf_token")},
        success: function (response) {
            if (response.error_no == '0') {
                alert("注销成功")
                location.href = '/';
            } else if (response.error_no == '4101') {
                location.href = 'login.html';
            } else {
                alert(response.error_msg);
            }
        }
    })

}
    // $.ajax({
    //     url: "api_1_0/session",
    //     type: "delete",
    //     headers: {"X-CSRFToken": getCookie("csrf_token")},
    //     success: function (response) {
    //         if (response.errno == '0') {
    //             location.href = '/';
    //         } else if (response.errno == '4101') {
    //             location.href = 'login.html';
    //         } else {
    //             alert(response.errmsg);
    //         }
    //     }
    // })

$(document).ready(function(){

    // TODO: 在页面加载完毕之后去加载个人信息
    showMsg()

});
