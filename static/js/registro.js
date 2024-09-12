// Obtener el elemento de fecha de nacimiento por su ID
const fechaNacimientoInput = document.getElementById('fecha_nacimiento');

// Obtener la fecha actual
const fechaActual = new Date();

// Formatear la fecha actual en el formato deseado (por ejemplo, "YYYY-MM-DD")
const fechaActualFormateada = fechaActual.toLocaleDateString('es-ES');

// Establecer la fecha actual como el valor del placeholder
fechaNacimientoInput.placeholder = fechaActualFormateada;