function openTab(evt, elmId) {
	$(".tabcontent").css("display", "none");
	$(".groupCreater_option_btn").removeClass("active");
	$(elmId).css("display", "block");
	evt.currentTarget.className += " active";
}