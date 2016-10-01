function openTab(evt, elmId) {
	// Declare all variables
	var i, tabcontent, tablinks;

	// Get all elements with class="tabcontent" and hide them
	$(".tabcontent").css("display", "none");

    // Get all elements with class="tablinks" and remove the class "active"
    /*tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }*/
	$(".groupCreater_option_btn").removeClass("active");

	$(elmId).css("display", "block");
	evt.currentTarget.className += " active";
}