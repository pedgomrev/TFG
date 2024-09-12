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
document.getElementById('btn_comunidades').addEventListener('click', function() {
    formulario = document.getElementById('formularioComunidades')
    if(formulario.style.display == 'block'){
        formulario.style.display = 'none';
    }else{
        formulario.style.display = 'block';
    }
});
$(document).ready(function() {
    $('#search').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        $('#generos-container .genero').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
});
$(document).ready(function() {
    $('.genero-checkbox').on('change', function() {
        var genero = $(this).data('genero');
        if ($(this).is(':checked')) {
            // Si el checkbox está seleccionado, añade un nuevo elemento li a la lista ul
            $('.lista_generos').append('<li class="dropdown-item">' + genero + '</li>');
            $('.lista_generos').append('<hr class="dropdown-divider">')
        } else {
            // Si el checkbox no está seleccionado, elimina el elemento li correspondiente de la lista ul
            $('.lista_generos li').filter(function() {
                return $(this).text() === genero;
            }).remove();
        }
    });
});

$(document).ready(function() {
    $('#crearComunidades').on('submit', function(e) {
        // Evita que el formulario se envíe de inmediato
        e.preventDefault();

        // Elimina los campos de entrada ocultos existentes
        $('.genero-input').remove();

        // Crea un nuevo campo de entrada oculto para cada género seleccionado
        $('.lista_generos li').each(function() {
            var genero = $(this).text();
            $(this).append('<input type="hidden" class="genero-input" name="generos" value="' + genero + '">');
        });

        // Envía el formulario
        this.submit();
    });
});
$(document).ready(function() {
    $('#buscador_comunidades').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        $('#comunidades_container .comunidad').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
});