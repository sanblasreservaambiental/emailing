# Emailing · San Blas Reserva Ambiental

Campaña para huéspedes de Barceló Tenerife. Diseño con K2D, Source Serif 4, basalto, arena y almagre, siguiendo el dossier.

## Archivos

- `mailing/emails/intern_email_2.0_{es,en,fr,de,nl,ru,it,pl}.html`: ocho páginas online estáticas con selector de idioma.
- `mailing/emails/hotel-content.json`: textos y traducciones.
- `mailing/emails/hotel.css`: estilos adaptables.
- `mailing/emails/hotel-booking.js`: calendario, validación, mensaje y consentimiento de cargo.
- `mailing/emails/correo-huespedes-{es,en}.{html,txt,eml}`: correos en español e inglés y borradores multipartes para Outlook, sin destinatarios.
- `assets/img/hotel-*`, `logo-blanco.png`, `logo-reserva.png`: fotografías, logotipo y favicon locales.
- `/`, `/mailing/` y `/mailing/emails/`: entradas con selector de idioma.

Se conservan los correos escolares y `intern_email_1.0.html` como histórico.

## Actualizar

Editar textos o generador y ejecutar desde la raíz de `emailing`:

```powershell
python scripts/build_hotel.py
node --test scripts/hotel-booking.test.mjs
```

El generador sobrescribe las ocho páginas, los correos HTML/TXT/EML y las entradas. No requiere dependencias externas. El script clásico permite revisar la web mediante `file://`.

## Tarifas y horarios

- Completa: huéspedes adultos desde 12 años 15 €; niños de 3 a 11 años 8 €. No residentes: 22,50 € y 14,50 €, respectivamente. De martes a sábado, 09:30.
- Solo interiores: 10 € por entrada para huéspedes, adultos y niños; no residentes 15 €. Martes, jueves y viernes, 11:30.
- Plazas limitadas. El hero expresa «entre un 33 % y un 45 % de descuento», con la nota de porcentajes aproximados frente a no residentes. Los descuentos exactos son 33,33 % y 44,83 % según tarifa.

## Reservas

Tres desplegables nativos, inicialmente cerrados y en este orden:

1. **Reservar online · Barceló Experiences**: fichas `/actividades/1121/` para completa y `/actividades/104/` para interiores.
2. **Reservar personalmente en el hotel · Recepción**: marcar 3 desde la habitación o llamar al +34 922 74 90 10. Recepción llama al equipo para consultar visitas del mismo día tras el cierre de solicitudes directas.
3. **Reservar directamente con la Reserva Ambiental**: formulario con opción y fecha en la primera fila; apellidos, nombre opcional, habitación, adultos y niños.

Las solicitudes directas para hoy cierran a las 09:00 de Canarias. La primera carga propone una fecha válida. Después, la fecha elegida se conserva aunque sea inválida: el campo se marca en rojo y explica el motivo, muestra los días de visita y propone una fecha posterior. Solo «Tomar esta fecha» aplica la alternativa. En interiores, hoy sigue seleccionable si hay sesión: entre las 09:00 y las 11:00 oculta y deshabilita los datos personales y muestra solo recepción. Desde las 11:00, hoy deja de ser seleccionable; si estaba elegido, se conserva con aviso y una propuesta que debe aceptarse. Para una fecha futura vuelve el formulario.

Tras rellenar datos y revisar la solicitud, el cliente acepta el cargo del total a su habitación después de la visita. Eso habilita dos botones: **Enviar desde mi correo** y **Enviar desde mi WhatsApp**. El mensaje se redacta siempre en inglés e incluye visita, hora, fecha, datos del huésped y `userlanguage` con el código del idioma de la página. No incluye comparativas de precios ni notas internas. El formulario y el consentimiento siguen en el idioma del huésped. El cargo y la aceptación se muestran antes de abrir la aplicación del cliente.

Correo y WhatsApp contactan directamente con el equipo en `tenerife.ambiental-res@barcelo.com` y +34 922 097 040. No hay backend, envío automático, cobro automático ni almacenamiento persistente. Los datos no se añaden a la URL de la página ni se transfieren a Barceló Experiences. Los correos enlazan al formulario online; no contienen formularios interactivos.

## Publicación y revisión

Publicar en el GitHub Pages existente con el dominio de `CNAME`: `emailing.sanblasreservaambiental.org`. Sin compilación. Las imágenes y enlaces públicos de los correos presuponen esa publicación.

Las pruebas cubren días de visita, fechas inválidas, cierre diario, hora de Canarias en verano, alternativa de recepción, tarifas, mensajes y enlaces multilingües. Revisar también escritorio/móvil y realizar un envío de prueba en Outlook/Gmail antes de distribuir. Los contenidos y las visitas con guía están garantizados en español e inglés. Para contenidos en otros idiomas, contactar con la Reserva con antelación para planificar la visita. Las ocho traducciones de la web no implican visitas guiadas en ocho idiomas.

## Fechas llenas y disponibilidad remota

`booking-availability.json` permite cerrar días para ambas modalidades (`closedDates`) o marcar fechas llenas por modalidad (`fullyBookedDates.full` y `fullyBookedDates.inside`). Las fechas cerradas se mantienen en este único archivo compartido por los ocho idiomas. Usar `AAAA-MM-DD`, regenerar con `python scripts/build_hotel.py` y publicar los resultados. Se saltan también en la alternativa presencial del mismo día.

La consulta remota de Kora Travel está investigada pero no conectada: ver `docs/disponibilidad-remota.md` para resultados, diferencias de horarios y requisitos de integración.

## Calendario y datos prácticos

El calendario propio deshabilita los días sin sesión y los días cerrados/llenos: completa de martes a sábado; interiores martes, jueves y viernes. Permite escribir una fecha ISO (`AAAA-MM-DD`), con error junto al campo y confirmación explícita para adoptar la siguiente fecha válida. Se puede manejar con teclado, flechas y Escape. No altera la fecha al recuperar el foco, cambiar de modalidad o superar una hora de cierre.

Duración: completa 180 minutos (3 h), según `intern_email_1.0.html`; interiores 1 h, confirmada por el equipo. Punto de encuentro para ambas: mostrador de la Reserva Ambiental en la planta 2 del hotel.

### Dos alternativas para una fecha no válida

El aviso propone la primera visita disponible desde hoy y, si es distinta, la primera posterior a la fecha elegida. Cada propuesta tiene su botón «Tomar esta fecha». Si coinciden, solo aparece una. Se respetan los días de sesión, los cierres horarios de Canarias y `booking-availability.json`. Ninguna de las propuestas se aplica sin pulsar su botón.

## Refuerzo del formulario

Incluye errores junto a cada campo, nombre marcado como opcional, límites aritméticos seguros para cantidades, preservación de fechas, bloqueo de días no hábiles, confirmación de cada propuesta y revisión del resumen frente a los datos actuales antes de abrir una aplicación. Si los datos cambian, hay que aceptar de nuevo el cargo. Se evita abrir varias aplicaciones por una doble pulsación. La solicitud se puede copiar como alternativa tras aceptar el cargo; si no hay acceso al portapapeles, se selecciona el texto para copiarlo manualmente.

Si el script falta o no puede iniciarse, queda visible el contacto directo y los paneles de reserva siguen disponibles. El formulario puede preparar el mensaje sin red una vez cargada la página; enviar desde correo/WhatsApp requiere la aplicación correspondiente. No hay reserva, confirmación ni cobro automáticos.

Comprobado en Chrome con 320 y 390 px, texto al 200 %, colores forzados, datos con acentos/CJK/árabe/emoji, errores de inicio, cantidades inválidas y cambios posteriores a la revisión. Ocho banderas en una fila. Los mensajes se mantienen en inglés con `userlanguage`, también `pl`. Los clientes Outlook y Safari requieren su prueba de envío/dispositivo correspondiente.

## Claridad y adaptación visual

Instrucciones abreviadas en los ocho idiomas, explicación del mensaje en inglés y opción de volver a editar conservando los datos. El envío mantiene dos opciones; copiar queda como alternativa secundaria. Iconos SVG coherentes en la web y estructura independiente compatible con correo en las plantillas. Imagen principal adaptable a la anchura de pantalla.

El calendario se monta fuera del desplegable para evitar recortes; en móvil aparece dentro de la pantalla y en escritorio se coloca junto al campo. Comprobado también en horizontal de 844 × 390 px.

## Exclusión de buscadores

Todas las páginas HTML incluyen `noindex, nofollow, noarchive`, también las generadas y las plantillas antiguas. `robots.txt` bloquea recursos y archivos auxiliares; permite leer el HTML para que los buscadores puedan aplicar `noindex`. No sustituye un control de acceso.
