$(document).ready(function() {
    // For all sliders, on input event, update the corresponding label
    $('.form-range').on('input', function() {
        $(this).siblings('.amountLabel').text($(this).val());
    });
});
