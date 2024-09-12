document.addEventListener("DOMContentLoaded", function() {
    // Obtener todas las celdas de duración de la tabla
    var duracionCanciones = document.querySelectorAll("tbody td:last-child");

    // Iterar sobre cada celda de duración
    duracionCanciones.forEach(function(duracionCancion) {
        // Obtener la duración en segundos
        var duracionSegundos = parseInt(duracionCancion.textContent);
        // Calcular los minutos y segundos
        var duracion = Math.floor(duracionSegundos / 60);
        var minutos = Math.floor(duracion / 60)
        var segundos = duracion % 60;
        // Formatear la duración como "minutos:segundos"
        var duracionFormateada = minutos + ":" + (segundos < 10 ? "0" + segundos : segundos);
        // Actualizar el contenido de la celda con la duración formateada
        duracionCancion.textContent = duracionFormateada;
    });
});
document.addEventListener("DOMContentLoaded", function() {
    // Obtener todas las celdas de oyentes de la tabla
    var oyentesCanciones = document.querySelectorAll("tbody td:nth-child(5)");

    // Iterar sobre cada celda de oyentes
    oyentesCanciones.forEach(function(oyentesCancion) {
        // Obtener el número de oyentes
        var oyentes = parseInt(oyentesCancion.textContent);
        // Formatear el número de oyentes con puntos como separadores de miles
        var oyentesFormateados = oyentes.toLocaleString();
        // Actualizar el contenido de la celda con el número de oyentes formateado
        oyentesCancion.textContent = oyentesFormateados;
    });
});