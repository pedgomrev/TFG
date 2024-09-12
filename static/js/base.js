$(document).ready(function() {
$('#search-musica').on('submit', function(event) {
    event.preventDefault(); // Evita que el formulario se envíe
    var query = $(this).find('input[name="canciones"]').val(); // Obtiene el valor del campo de búsqueda
    $.ajax({
        url: '/buscarCancion/',
        data: {
            'canciones': query  
        },
        dataType: 'json',
        success: function(data) {
            var $container = $('.modalCanciones-body .row');
            $container.empty(); // Vacía el contenedor antes de agregar nuevos elementos
            data.canciones.forEach(function(cancion) {
                var card = `
                <button type="button" class="btn btn-cancion" data-cancion-id="${cancion.id}">
                    <div class="card card-modal-canciones" style="max-width: 540px;">
                        <div class="row g-0">
                            <div class="col-md-4" style="width: fit-content !important;">
                                <img src="/static/albums/${cancion.album}" class="img-fluid img-fluid-canciones rounded-start" alt="...">
                            </div>
                            <div class="col-md-9 d-flex align-content-center">
                                <div class="card-body card-body-modal d-flex align-items-center">
                                    <h6 class="card-title">${cancion.nombre}</h6>
                                </div>
                            </div>
                        </div>
                    </div>
                </button>`;
                $container.append(card); // Agrega el elemento al contenedor
            });
        }
    });
});

// Variable para almacenar la canción seleccionada
var cancionSeleccionada = null;
var idCancion = null;
$('.container-canciones-post').on('click', '.btn-cancion', function() {
    idCancion = $(this).data('cancion-id');
    // Aquí puedes hacer lo que quieras con la canción seleccionada
    // Por ejemplo, almacenarla en una variable o ejecutar alguna función
    cancionSeleccionada = {
        foto : $(this).find('.img-fluid-canciones').attr('src'),
        nombre : $(this).find('.card-title').text(),
    }
    // Ocultar el modal de selección de canciones
    $('#modalCanciones').modal('hide');
    
    // Mostrar el modal anterior
    $('#postModal').modal('show');});


// Evento al abrir el primer modal
$('#postModal').on('show.bs.modal', function() {
    // Actualiza el formulario con la canción seleccionada
    if (cancionSeleccionada) {
        $('#texto-informacion').hide();
        if($(".cancion-post").length > 0){
            $(".cancion-post").empty();
        }
        var cardCancion = `
                    <div class="col-md-4" style="width: fit-content !important;padding-right:0px;">
                        <img src="${cancionSeleccionada.foto}" class="img-fluid img-fluid-canciones" alt="..." style="border-radius:50%;">
                    </div>
                    <div class="col-md-9 d-flex align-content-center" style="padding-left:0px">
                        <div class="card-body card-body-modal d-flex align-items-center">
                            <h6 class="card-title">${cancionSeleccionada.nombre}</h6>
                        </div>
                    </div>`;
        $('.cancion-post').append(cardCancion);
        // También puedes agregar un campo oculto al formulario con el ID de la canción seleccionada
        $('#id_cancion_seleccionada').val(idCancion);
        var foto = cancionSeleccionada.foto.replace('/static/albums/', '');
        $('#imagen_cancion_seleccionada').val(foto);
    }
});
$()
    $('#complete_post').on('click', function() {
        // Obtener el token CSRF
        var csrftoken = $('[name=csrfmiddlewaretoken]').val();

        // Obtener los datos del formulario
        var comentario = $('#floatingTextarea').val();
        var idCancion = $('#id_cancion_seleccionada').val();
        var imagenCancion = $('#imagen_cancion_seleccionada').val();

        // Construir los datos a enviar
        var formData = new FormData();
        formData.append('csrfmiddlewaretoken', csrftoken); // Incluir el token CSRF
        formData.append('comentario', comentario);
        formData.append('id_cancion', idCancion);
        formData.append('imagen_cancion', imagenCancion);

        // Enviar los datos del formulario utilizando AJAX
        $.ajax({
            url: '/postear/',
            type: 'POST',
            data: formData,
            processData: false,  // Evitar el procesamiento de datos
            contentType: false,  // No establecer el tipo de contenido
            success: function(response) {
                // Aquí puedes manejar la respuesta del servidor
                location.reload();
            },
            error: function(xhr, status, error) {
                // Aquí puedes manejar errores de la solicitud AJAX
                console.error('Error al enviar el formulario:', error);
            }
        });
    });
    // Encuentra el botón "Postear" por su ID
    var postButton = document.getElementById("complete_post");

    // Agrega un evento de clic al botón "Postear"
    postButton.addEventListener("click", function () {
        // Encuentra el modal por su ID
        var postModal = document.getElementById("postModal");

        // Cierra el modal
        var modalInstance = bootstrap.Modal.getInstance(postModal);
        modalInstance.hide();
    });
});
