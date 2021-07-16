$(document).ready(function () {
    $('.sidenav').sidenav({
        edge: "right"
    });
    $('.collapsible').collapsible();
    $('.tabs').tabs();
    $('select').formSelect();
    $('.dropdown-trigger').dropdown()
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
    /* Code used from course material */
    validateMaterializeSelect();
    function validateMaterializeSelect() {
        let classValid = {
            "border-bottom": "1px solid #4caf50",
            "box-shadow": "0 1px 0 0 #4caf50"
        };
        let classInvalid = {
            "border-bottom": "1px solid #f44336",
            "box-shadow": "0 1px 0 0 #f44336"
        };
        if ($("select.validate").prop("required")) {
            $("select.validate").css({
                "display": "block",
                "height": "0",
                "padding": "0",
                "width": "0",
                "position": "absolute"
            });
        }
        $(".select-wrapper input.select-dropdown").on("focusin", function () {
            $(this).parent(".select-wrapper").on("change", function () {
                if ($(this).children("ul").children("li.selected:not(.disabled)").on("click", function () {})) {
                    $(this).children("input").css(classValid);
                }
            });
        }).on("click", function () {
            if ($(this).parent(".select-wrapper").children("ul").children("li.selected:not(.disabled)").css("background-color") === "rgba(0, 0, 0, 0.03)") {
                $(this).parent(".select-wrapper").children("input").css(classValid);
            } else {
                $(".select-wrapper input.select-dropdown").on("focusout", function () {
                    if ($(this).parent(".select-wrapper").children("select").prop("required")) {
                        if ($(this).css("border-bottom") != "1px solid rgb(76, 175, 80)") {
                            $(this).parent(".select-wrapper").children("input").css(classInvalid);
                        }
                    }
                });
            }
        });
    }

});
function deleteRow() {
    const TABLE = document.getElementById('exerciseRow');
    let rowCount = TABLE.rows.length;
    if(rowCount >'1'){
        let row = TABLE.deleteRow(rowCount-1);
        rowCount--;
    } else{
        alert("Cannot Delete Exercise")
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

document.getElementById("table").style.display = "none";
document.getElementById("exercise_name1").disabled = true;
document.getElementById("exercise_reps1").disabled = true;
document.getElementById("exercise_sets1").disabled = true;
document.getElementById("exercise_weight1").disabled = true;

function addExercise() {
    let table = document.getElementById("table")
    if (table.style.display === "none") {
        table.style.display = "block";
        document.getElementById("exercise_name1").disabled = false;
        document.getElementById("exercise_reps1").disabled = false;
        document.getElementById("exercise_sets1").disabled = false;
        document.getElementById("exercise_weight1").disabled = false;
    } else {
        table.style.display = "none";
        document.getElementById("exercise_name1").disabled = true;
        document.getElementById("exercise_reps1").disabled = true;
        document.getElementById("exercise_sets1").disabled = true;
        document.getElementById("exercise_weight1").disabled = true;
    }
}
function resetForm() {
    document.getElementById('workoutForm').reset();
}


