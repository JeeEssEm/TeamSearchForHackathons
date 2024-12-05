document.getElementById('select-all').addEventListener('click', function (event) {
    const checkboxes = document.querySelectorAll('input[name="selected_technologies"]');
    checkboxes.forEach(checkbox => checkbox.checked = event.target.checked);
});