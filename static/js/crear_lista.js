$(document).ready(function () {
  $("#search_musica_lista").on("submit", function (event) {
    event.preventDefault(); // Evita que el formulario se envíe
    var query = $(this).find('input[name="canciones"]').val(); // Obtiene el valor del campo de búsqueda
    $.ajax({
      url: "/buscarCancion/",
      data: {
        canciones: query,
      },
      dataType: "json",
      success: function (data) {
        var $container = $(".container-canciones .col-12");
        $container.empty(); // Vacía el contenedor antes de agregar nuevos elementos
        data.canciones.forEach(function (cancion) {
          var card = `
                <div class="row m-3">
                    <div class="col-12">
                        <div class="card card-modal-canciones" style="font-family: 'Glacial';">
                            <div class="row g-0">
                                <div class="col-md-4" style="width: fit-content !important;">
                                    <img src="/static/albums/${cancion.album}" class="img-fluid img-fluid-canciones rounded-start" alt="...">
                                </div>
                                <div class="col-md-6 d-flex align-content-center" style="margin-right:auto">
                                    <div class="card-body card-body-modal d-flex align-items-center">
                                        <h6 class="card-title">${cancion.nombre}</h6>
                                    </div>
                                </div>
                                <div class="col-md-2 d-flex align-items-center justify-content-end p-2">
                                    <button type="button" class="btn btn_cancion_add" data-cancion-id="${cancion.id}">Añadir</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>`;
          $container.append(card); // Agrega el elemento al contenedor
        });
      },
    });
  });
  $(document).on("click", ".btn_cancion_add", function (event) {
    event.preventDefault(); // Evita que el formulario se envíe
    var query = $(this).attr("data-cancion-id"); // Obtiene el valor del campo de búsqueda
    $.ajax({
        url: "/buscarCancion/",
        data: {
            id: query,
        },
        dataType: "json",
        success: function (data) {
            var $container = $("#lista_reproduccion");
            var cancion = data.cancion;
            var id_playlist = segments[segments.length - 1];

            // Función para convertir segundos a formato min:seg
            function convertirDuracion(segundos) {
              var duracion = Math.floor(segundos / 60);
              var minutos = Math.floor(duracion / 60)
              var segundos = duracion % 60;
              // Formatear la duración como "minutos:segundos"
              return duracionFormateada = minutos + ":" + (segundos < 10 ? "0" + segundos : segundos);
            }

            var duracionFormateada = convertirDuracion(cancion.duracion);
            var card = `
                <tr>
                                    <th scope="row"><a
                        href="{% url 'eliminar_cancion' ${id_playlist} ${cancion.id} %}"><button type="button" class="btn btn_elim_cancion"
                            data-cancion-id="${cancion.id}">X</button></a></th>
                    <td>${cancion.nombre}</td>
                    ${
                      cancion.link_spotify
                        ? `<td><a href="${cancion.link_spotify}" target="_blank"><i class="fa-brands fa-spotify" style="color: green;"></i></a></td>`
                        : "<td>Sin link</td>"
                    }
                    ${
                      cancion.link_youtube
                        ? `<td><a href="${cancion.link_youtube}" target="_blank"><i class="fa-brands fa-youtube" style="color: red;"></i></a></td>`
                        : "<td>Sin link</td>"
                    }
                    <td>${cancion.oyentes}</td>
                    <td>${duracionFormateada}</td>
                </tr>
            `;
            $container.append(card); // Agrega el elemento al contenedor
        },
    });
    var path = window.location.pathname; // Esto será algo como "/buscar_cancion/5"
    var segments = path.split("/"); // Esto divide la ruta en segmentos: ["", "buscar_cancion", "5"]
    console.log(id_playlist);
    $.ajax({
        url: `/guardar_cancion/${id_playlist}/${query}`,
        data: {},
        dataType: "json",
        success: function (data) {
            console.log(data);
        },
    });
});



  document
    .getElementById("imagen_modal")
    .addEventListener("click", function () {
      document.getElementById("input_imagen").click();
    });
  document
    .getElementById("input_imagen")
    .addEventListener("change", function (e) {
      var file = e.target.files[0];
      var reader = new FileReader();

      reader.onloadend = function () {
        document.getElementById("imagen_modal").src = reader.result;
        document.getElementById("input_imagen").src = reader.result;
      };

      if (file) {
        reader.readAsDataURL(file);
      } else {
        document.getElementById("imagen_modal").src = "";
        document.getElementById("input_imagen").src = "";
      }
    });
      const checkbox = document.getElementById('checkboxVisibilidad');
      const label = document.getElementById('labelVisibilidad');
  
      checkbox.addEventListener('change', function () {
          if (checkbox.checked) {
              label.textContent = 'Lista pública';
          } else {
              label.textContent = 'Lista privada';
          }
      });
});
function confirmacion_eliminar(event) {
  const confirmacion = confirm("¿Estás seguro de que quieres realizar esta acción?");
  if (!confirmacion) {
      event.preventDefault();
  } else {
      alert("Acción confirmada");
  }
}