document.getElementById('imagen_modal_comunidad').addEventListener('click', function() {
    document.getElementById('input_imagen_comunidad').click();
});
document.getElementById('input_imagen_comunidad').addEventListener('change', function(e) {
    var file = e.target.files[0];
    var reader = new FileReader();

    reader.onloadend = function() {
        document.getElementById('imagen_modal_comunidad').src = reader.result;
        document.getElementById('input_imagen_comunidad').src = reader.result;
    }

    if (file) {
        reader.readAsDataURL(file);
    } else {
        document.getElementById('imagen_modal_comunidad').src = "";
        document.getElementById('input_imagen_comunidad').src = "";
    }
});
document.getElementById('eliminar_comunidad').addEventListener('click', function() {
    document.getElementById('form_eliminar_comunidad').submit();
});