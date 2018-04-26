$(document).ready(function(){
    // TODO: 对于发布房源，只有认证后的用户才可以，所以先判断用户的实名认证状态
    $.get('/api_1_0/users/auth', function (response) {
        if (response.error_no == '0') {
        // 当用用户有实名认证信息时,展示实名认证信息,输入入框改为不不可用用
        if (response.data.real_name && response.data.id_card) {
        // TODO: 如果用用户已实名认证,那么就去请求之前发布的房源
            $.get('/api_1_0/users/houses', function (response) {
            if (response.error_no == '0') {
            var html = template('houses-list-tmpl', {'houses':response.data});
            $('#houses-list').html(html);
            } else if (response.error_no == '4101') {
            location.href = 'login.html';
            } else {
            alert(response.error_msg);
            }
            })
        } else {
        $(".auth-warn").show();
        }
        } else if (response.error_no == '4101') {
        location.href = 'login.html';
        } else {
        alert(response.error_msg);
        }
    });
    // $(".auth-warn").show();
    // TODO: 如果用户已实名认证,那么就去请求之前发布的房源
})
