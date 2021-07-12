$(document).ready(function () {
    $('.sidenav').sidenav({edge: "right"});
    $('.collapsible').collapsible();
    $('.tabs').tabs();
    $('select').formSelect();
    $('.datepicker').datepicker({
        format: "dd mmmm, yyyy",
        yearRange: 1,
        showClearBtn: true,
        i18n: {
            done: "Select"
        },
        showDaysInNextAndPreviousMonths: true
    });
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
function deleteRow() {
    const TABLE = document.getElementById('exerciseRow');
    let rowCount = TABLE.rows.length;
    if(rowCount >'1'){
        let row = TABLE.deleteRow(rowCount-1);
        rowCount--;
    } else{
        alert("There has to be more than one Exercise")
    }
}
function addRow() {
	var table = document.getElementById('exerciseRow');
	var rowCount = table.rows.length;
	var cellCount = table.rows[0].cells.length; 
	var row = table.insertRow(rowCount);
    for(var i =0; i <= cellCount; i++){
        var cell = 'cell'+i;
		cell = row.insertCell(i);
		var copycel = document.getElementById('col'+i).innerHTML;
		cell.innerHTML=copycel;
    }
}
