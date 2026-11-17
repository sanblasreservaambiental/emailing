# Disponibilidad de Barceló Experiences

Inspección de solo lectura del 17/11/2026. No hay sincronización remota activa.

## Lo comprobado

Las fichas públicas de las actividades 104 (interiores) y 1121 (completa) cargan un iframe de `app.kora.travel/widget/index`. El widget consulta `GET /widget/availabilities` con mes, año y su configuración pública. La respuesta es JSON con fechas, horas y `availableSeats`. La prueba observada usa mes 10 para noviembre: no asumir mes humano 1–12.

La lectura directa desde el origen de Barceló falló en el navegador por la restricción entre orígenes. Las respuestas observadas no incluyen `Access-Control-Allow-Origin`. El widget también declara `frame-ancestors` con una lista de dominios que no incluye el dominio de la Reserva. Por tanto, no basta con copiar el iframe o hacer un `fetch` desde nuestro GitHub Pages.

No se ha encontrado documentación pública que garantice el contrato de este endpoint de Kora. No se han guardado cookies ni configuraciones de acceso del widget en este repositorio.

## Integración propuesta

Confirmar con Barceló/Kora el acceso para consultar disponibilidad (API o feed). Consultar desde un servidor, o sincronizar a un JSON público propio con fecha de actualización. El formulario debe comparar plazas con adultos + niños y mantener los cierres de solicitudes directas de las 09:00/11:00, que son reglas propias.

Una consulta no bloquea plazas: el envío por correo o WhatsApp sigue siendo una solicitud pendiente de confirmación. Si el origen no responde, no presentar datos antiguos como disponibilidad en tiempo real.

## Diferencias que requieren confirmar

El calendario remoto de interiores devolvió sesiones a las 10:00, 11:00, 12:00 y 13:00, además de algunas a las 11:30. También había días diferentes de martes/jueves/viernes. No se deben tratar todas esas sesiones como disponibilidad de nuestra visita de las 11:30.

La completa devolvió sesiones de las 09:30; algunas fechas de su patrón habitual no aparecían. La ausencia de una fecha en una respuesta no basta para distinguir por sí sola entre lleno, cerrado o no publicado.

## Archivo manual disponible

Mientras se acuerda la integración, `booking-availability.json` permite bloquear fechas sin tocar traducciones:

```json
{
  "closedDates": ["2026-12-25"],
  "fullyBookedDates": {
    "full": ["2026-12-01"],
    "inside": ["2026-12-03"]
  }
}
```

Estas fechas son solo ejemplos; el archivo real contiene los cierres que ha confirmado el equipo. `closedDates` bloquea ambas modalidades; las otras listas bloquean solo la indicada. Usar `AAAA-MM-DD`, ejecutar `python scripts/build_hotel.py` y publicar los archivos regenerados. La regla se aplica igual al cálculo de la siguiente fecha y a la alternativa de recepción para hoy.
