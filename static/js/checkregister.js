// script to dynamically respond to the user about reginstering their accounts
// ensure that all fields are filled
let uname = document.querySelector("#username");
let pass = document.querySelector("#password");
let confirmPass = document.querySelector("#password_confirm");
let unameBoxEmpty = true;
let passBoxEmpty = true;
let passwordConfirmation = false;
// check that password and password confirmation boxes are not empty and the same
function verifyPasswords(){
    if (pass.value !== confirmPass.value)
    {
        confirmPass.style.border = "1px solid red";
        document.getElementById("err").innerHTML = `\nPasswords do not match`;
        passwordConfirmation = false;
    }
    else
    {
        confirmPass.style.border = "1px solid #ced4da"
        document.getElementById("err").innerHTML = "";
        passwordConfirmation = true;
    }
}
confirmPass.onkeyup = verifyPasswords;
function checkValue()
{
    let btn = document.querySelector("#submit");
    btn.disabled = !((uname.value !== "" || hasWhiteSpace(uname.value)) && (pass.value !== "" || hasWhiteSpace(pass.value)) && passwordConfirmation);
}

function hasWhiteSpace(s) {
    return /\s/g.test(s);
}

window.setInterval(checkValue, 1);