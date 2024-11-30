function copyText() {
    let copyText = document.getElementById("link");

    copyText.select();
    copyText.setSelectionRange(0, 99999);

    navigator.clipboard.writeText(copyText.value);

}