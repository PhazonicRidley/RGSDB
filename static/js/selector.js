// hides and shows selector options
$(document).ready(function(){
    $("select").change(function(){
        $(this).find("option:selected").each(function(){
            var optionValue = $(this).attr("value");
            if(optionValue){
                $(".select").not("." + optionValue).hide();
                $("." + optionValue).show();
                $("." + optionValue).prop('required', true);
            } else{
                $(".select").hide();
            }
        });
    }).change();
});

// hides file upload
$(document).ready(function() {
    $('select').change(function() {
        let selector = document.getElementById("datatype")
        console.log(selector.value)
        console.log(selector.options[0].value)
        console.log(selector.value === selector.options[0].value)
        document.getElementById("fileuploadblock").hidden = selector.options[0].value === selector.value;
    });
})
