$(document).ready(function() {
    $(document).on("click", ".page-link", function(event) {
        event.preventDefault();
        let page = $(this).data("page");
        let partial = $(this).data("partial");
        let url = new URL(window.location.href);
        
        // Actualizar los parámetros de la URL
        url.searchParams.set('page' + partial.charAt(0).toUpperCase() + partial.slice(1), page);
        url.searchParams.set('partial', partial);

        fetch(url, {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.text())
        .then(html => {
            let containerId = `${partial}-list`;
            let container = $(`#${containerId}`);
            container.addClass('fade-out'); // Agregar clase de animación de salida
            setTimeout(() => {
                container.html(html);
                container.removeClass('fade-out'); // Eliminar clase de animación de salida
                container.addClass('fade-in'); // Agregar clase de animación de entrada
            }, 500); // Ajustar el tiempo para que coincida con la duración de la animación
            attachPageLinkEvents(); // Volver a adjuntar eventos después de actualizar el contenido
        });
    });
});