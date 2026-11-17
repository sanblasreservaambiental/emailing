# Emailing · San Blas Reserva Ambiental

Campaña para huéspedes de Barceló Tenerife: dos correos breves y una ficha web en ocho idiomas. Diseño de la web basado en el dossier, con K2D, Source Serif 4, basalto, arena y almagre. Los correos usan tablas y estilos en línea para clientes de correo.

## Dónde están los correos

Los archivos vigentes están en **`hotel/correo/`**:

| Idioma | Vista HTML | Texto alternativo | Borrador para correo |
| --- | --- | --- | --- |
| Español | [hotel/correo/es.html](hotel/correo/es.html) | [es.txt](hotel/correo/es.txt) | [es.eml](hotel/correo/es.eml) |
| Inglés | [hotel/correo/en.html](hotel/correo/en.html) | [en.txt](hotel/correo/en.txt) | [en.eml](hotel/correo/en.eml) |

Vistas públicas: [correo en español](https://emailing.sanblasreservaambiental.org/hotel/correo/es.html) y [correo en inglés](https://emailing.sanblasreservaambiental.org/hotel/correo/en.html).

Los HTML sirven para revisar y reutilizar el contenido. Los EML son borradores multipartes (HTML y texto), con `X-Unsent: 1` y sin destinatarios. Abrirlos en el cliente de correo compatible, revisar remitente y formato, añadir destinatarios y realizar un envío de prueba en Outlook/Gmail antes de distribuir. Generar o publicar estos archivos no envía ningún correo.

Cada correo presenta brevemente las dos modalidades y destaca el descuento para huéspedes, dejando los precios en la web; incluye una ficha visual enlazada a la web y enlaces a los ocho idiomas. Los horarios, las condiciones y el formulario están en la ficha web. Al cierre, cinco estrellas enlazan a [FastReview](https://app.fastreview.pro/home/A5q3G8kVo1eM6Zr); son un enlace, no un selector de puntuación.

## Páginas web

Dominio: **https://emailing.sanblasreservaambiental.org**.

| Ruta | Contenido |
| --- | --- |
| `/` | Índice vacío |
| `/hotel/` | Inglés, versión predeterminada |
| `/hotel/es/` | Español |
| `/hotel/en/` | Inglés, también accesible con código de idioma |
| `/hotel/fr/` | Francés |
| `/hotel/de/` | Alemán |
| `/hotel/nl/` | Neerlandés |
| `/hotel/ru/` | Ruso |
| `/hotel/it/` | Italiano |
| `/hotel/pl/` | Polaco |
| `/hotel/correo/es.html` y `/hotel/correo/en.html` | Vistas de los dos correos |

Los índices de `/mailing/`, `/mailing/emails/` y `/hotel/correo/` también están vacíos. Las rutas anteriores `mailing/emails/intern_email_2.0_{idioma}.html` y `mailing/emails/correo-huespedes-{es,en}.{html,txt,eml}` se conservan por compatibilidad con enlaces compartidos. Para nuevos usos, utilizar las rutas de `hotel/`. Se conservan también el correo escolar y `intern_email_1.0.html` como histórico.

## Fuentes y generación

| Archivo o directorio | Función |
| --- | --- |
| `scripts/build_hotel.py` | Genera las páginas, los correos y los índices vacíos |
| `mailing/emails/hotel-content.json` | Textos y traducciones de las ocho páginas |
| `mailing/emails/hotel.css` | Estilos de la web |
| `mailing/emails/hotel-booking.js` | Calendario, validación, revisión, consentimiento y preparación del mensaje |
| `booking-availability.json` | Cierres y fechas llenas compartidos por los ocho idiomas |
| `scripts/hotel-booking.test.mjs` | Pruebas de fechas, horarios, tarifas y mensajes |
| `assets/img/` y `assets/flags/` | Fotos, logotipos, favicon, imagen para compartir y banderas |
| `docs/disponibilidad-remota.md` | Investigación de la disponibilidad de Barceló Experiences/Kora |

Editar las fuentes y ejecutar desde la raíz de este repositorio:

```powershell
python scripts/build_hotel.py
node --test scripts/hotel-booking.test.mjs
git diff --check
```

El generador usa Python 3 sin dependencias externas. Sobrescribe los archivos de salida, incluidas las copias de compatibilidad: no editar manualmente esos HTML, TXT o EML. La copia breve específica del correo está en `email_copy` dentro del generador. El JavaScript es clásico y permite revisar las páginas mediante `file://`; las imágenes de los correos usan direcciones públicas.

## Tarifas y datos prácticos

| Modalidad | Huéspedes | No residentes | Horario | Duración |
| --- | --- | --- | --- | --- |
| Completa, exterior e interiores | Adultos desde 12 años: 15 €; niños de 3–11 años: 8 € | Adultos: 22,50 €; niños: 14,50 € | Martes a sábado, 09:30 | 3 h |
| Solo interiores | 10 € por entrada, adultos y niños | 15 € por entrada | Martes, jueves y viernes, 11:30 | 1 h |

Plazas limitadas. La web anuncia entre un 33 % y un 45 % de descuento, con explicación al pie: 33,33 % para adultos de completa y entradas de interiores; 44,83 % para niños de completa. Punto de encuentro: mostrador de la Reserva Ambiental, planta 2 del hotel.

Los contenidos y las visitas con guía están garantizados en español e inglés. Para contenidos en otros idiomas, contactar con antelación para planificar la visita. Las ocho traducciones de la web no implican guías en ocho idiomas.

## Reservas y calendario

Tres desplegables, inicialmente cerrados:

1. **Barceló Experiences:** completa en `/actividades/1121/` e interiores en `/actividades/104/`.
2. **Recepción:** marcar 3 desde la habitación o llamar al +34 922 74 90 10.
3. **Directamente con la Reserva Ambiental:** formulario con modalidad y fecha arriba, apellidos, nombre opcional, habitación, adultos y niños.

Todas las horas son de Canarias. Las solicitudes directas para hoy cierran a las 09:00. Solo para interiores en un día con sesión y sin cierre, después de las 09:00 y antes de las 11:00 se ocultan los datos personales y se ofrece contactar con recepción para que llame al equipo. Desde las 11:00 ya no se puede elegir interiores para hoy. Para fechas futuras vuelve el formulario.

El calendario deshabilita días sin sesión, pasados, cerrados o llenos. Admite escritura de fecha `AAAA-MM-DD`. La primera carga propone una fecha válida; después conserva la elección del cliente aunque sea inválida. El aviso explica el problema y ofrece la primera visita desde hoy y la primera posterior a la fecha elegida, sin duplicarlas si coinciden. Solo el botón «Tomar esta fecha» aplica una propuesta.

Tras revisar la solicitud, el cliente acepta el cargo del total a su habitación después de la visita. Se habilitan dos opciones: enviar desde su correo o desde su WhatsApp; también puede copiar el mensaje. El mensaje siempre está en inglés e incluye `userlanguage` con el idioma del cliente. Si cambian los datos hay que revisar y aceptar de nuevo el cargo.

Contacto directo: `tenerife.ambiental-res@barcelo.com` y WhatsApp +34 922 097 040. No hay backend, envío automático, confirmación automática, cobro automático ni almacenamiento persistente. Los datos del formulario no se envían a Barceló Experiences ni se añaden a la dirección de la página.

### Cerrar días

Editar únicamente `booking-availability.json`:

- `closedDates`: cierres para ambas modalidades.
- `fullyBookedDates.full`: fechas llenas/cerradas de la completa.
- `fullyBookedDates.inside`: fechas llenas/cerradas de interiores.

Usar fechas completas `AAAA-MM-DD`, regenerar y publicar. Se respetan también al ofrecer recepción y fechas alternativas. La disponibilidad remota de Kora está investigada, pero **no está conectada**: el calendario no representa cupos en tiempo real.

## Compartir y buscadores

Las páginas de hotel y las vistas HTML de los correos incluyen Open Graph y Twitter Card localizados. La imagen compartida es `assets/img/hotel-compartir.jpg`, de 1200 × 630. `robots.txt` permite esa imagen para las vistas previas y bloquea otros recursos y archivos auxiliares.

Todas las páginas HTML llevan `noindex, nofollow, noarchive`. El HTML permanece rastreable para que los buscadores puedan leer `noindex`. Los índices vacíos no muestran contenido ni tienen ficha de compartir. Estas directivas no sustituyen un control de acceso.

## Publicación y comprobación

GitHub Pages publica desde la rama `main`, directorio raíz, con el dominio indicado en `CNAME`. Después de regenerar, revisar los cambios, ejecutar las pruebas, confirmar y subir a `main`. Comprobar que termina el despliegue y que funcionan las páginas, recursos, enlaces y metadatos públicos.

El formulario se ha comprobado en Chrome con anchuras móviles, texto al 200 %, colores forzados, errores de inicio y datos multilingües. Los correos mantienen tablas y estilos en línea, espaciado en celdas, tipografía explícita, ajustes MSO a 96 DPI y un botón VML para Outlook clásico/Word. Las fuentes web quedan excluidas de la rama MSO, con alternativas Georgia y Arial. Las estrellas usan una fuente de símbolos y conservan un enlace accesible. Se verifican las ramas MSO y moderna por separado. Ambos HTML se han abierto en Microsoft Word instalado y se ha revisado su exportación a PDF (texto, imagen, botón VML, idiomas, contactos y estrellas); la prueba real de envío en Outlook/Gmail y la revisión en Safari siguen siendo necesarias antes de distribuirlos.
