document.getElementById('imagen_modal').addEventListener('click', function() {
    document.getElementById('input_imagen').click();
});
document.getElementById('input_imagen').addEventListener('change', function(e) {
    var file = e.target.files[0];
    var reader = new FileReader();

    reader.onloadend = function() {
        document.getElementById('imagen_modal').src = reader.result;
        document.getElementById('input_imagen').src = reader.result;
    }

    if (file) {
        reader.readAsDataURL(file);
    } else {
        document.getElementById('imagen_modal').src = "";
        document.getElementById('input_imagen').src = "";
    }
});
function confirmacion_eliminar(event) {
    const confirmacion = confirm("¿Estás seguro de que quieres realizar esta acción?");
    if (!confirmacion) {
        event.preventDefault();
    } else {
        alert("Acción confirmada");
    }
}