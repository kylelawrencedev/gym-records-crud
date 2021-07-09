$(document).ready(function () {
    $('.sidenav').sidenav({edge: "right"});
    $('.tabs').tabs();
    /* Code for confirming password was used from 
    http://jsfiddle.net/SirusDoma/ayf832td/
    */
    $("#password").on("focusout", function (e) {
        if ($(this).val() != $("#passwordConfirm").val()) {
            $("#passwordConfirm").removeClass("valid").addClass("invalid");
        } else {
            $("#passwordConfirm").removeClass("invalid").addClass("valid");
        }
    });
    $("#passwordConfirm").on("keyup", function (e) {
        if ($("#password").val() != $(this).val()) {
            $(this).removeClass("valid").addClass("invalid");
        } else {
            $(this).removeClass("invalid").addClass("valid");
        }
    });
    /* Code sourced from 
    https://www.aspsnippets.com/Articles/Password-and-Confirm-Password-validation-using-JavaScript-and-jQuery.aspx
    */
    $("#accountBtn").click(function () {
        var password = $("#password").val();
        var confirmPassword = $("#passwordConfirm").val();
        if (password != confirmPassword) {
            alert("Make sure your passwords match");
            return false;
        }
        return true;
    });
});
