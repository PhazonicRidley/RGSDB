// dark mode script
// check for existing cookie
if (document.cookie === "")
{
    document.cookie = "theme=DARK";
}

function setDarkmode()
{
    // switching to dark mode
    $("a").css("color", "#ea433b");
    document.querySelector("body").classList.add("body-darkmode");
    document.getElementById("navbar").classList.replace("navbar-light", "navbar-dark");
    document.getElementById("navbar").classList.replace("bg-light", "bg-dark");
    document.getElementById("theme-mode").classList.replace("btn-dark", "btn-light");
    document.cookie = "theme=DARK";
}

function setLightMode()
{
    // switching to light mode
    $("a").css("color", "#007bff");
    document.querySelector("body").classList.remove("body-darkmode");
    document.getElementById("navbar").classList.replace("navbar-dark", "navbar-light");
    document.getElementById("navbar").classList.replace("bg-dark", "bg-light");
    document.getElementById("theme-mode").classList.replace("btn-light", "btn-dark");
    document.cookie = "theme=LIGHT";
}

function switchMode()
{
    // to be used on a btn
    if (document.cookie.split("=")[1] === "DARK")
    {
        setLightMode();
    }
    else
    {
        setDarkmode();
    }
    
}
// persistence function
function updateTheme() {
    // theme persistance
    if (document.cookie.split("=")[1] === "LIGHT")
    {
        setLightMode();
    }
    else 
    {
        setDarkmode();
    }
}

// switchmode is called on the theme-mode btn in layout.html
// updateTheme is called when the body is loaded in layout.html
