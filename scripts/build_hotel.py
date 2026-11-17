"""Genera páginas estáticas y correos de huéspedes. Python 3, sin dependencias."""
import json
from pathlib import Path
from html import escape as e
from email.message import EmailMessage
from email import policy
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'mailing' / 'emails'
EMAIL_OUT = ROOT / 'hotel' / 'correo'
EMAIL_OUT.mkdir(parents=True, exist_ok=True)
DATA = json.loads((OUT / 'hotel-content.json').read_text(encoding='utf-8'))
AVAILABILITY = json.loads((ROOT / 'booking-availability.json').read_text(encoding='utf-8'))
required_form_keys=set(DATA['en']['bookingForm'])
for language,content in DATA.items():
    missing=required_form_keys-set(content['bookingForm'])
    if missing:
        raise ValueError(f'Traducciones del formulario incompletas en {language}: {sorted(missing)}')
for dates in [AVAILABILITY['closedDates'], AVAILABILITY['fullyBookedDates']['full'], AVAILABILITY['fullyBookedDates']['inside']]:
    if not isinstance(dates, list):
        raise ValueError('Cada grupo de booking-availability.json debe ser una lista de fechas.')
    for value in dates:
        if not isinstance(value, str) or date.fromisoformat(value).isoformat() != value:
            raise ValueError(f'Fecha no válida en booking-availability.json: {value!r}. Usar AAAA-MM-DD.')
BASE = 'https://emailing.sanblasreservaambiental.org/hotel/'

def hotel_url(lang):
    return BASE if lang == 'en' else BASE + lang + '/'

ADDRESS = 'tenerife.ambiental-res@barcelo.com'
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=K2D:wght@400;500;700&amp;family=Source+Serif+4:wght@400;600&amp;display=swap" rel="stylesheet">'
EXPERIENCES = {key: 'https://www.barcelo.com/guia-turismo/es/espana/tenerife/actividades/' + code + '/'
               for key, code in [('full', '1121'), ('inside', '104')]}

REVIEW_URL = 'https://app.fastreview.pro/home/A5q3G8kVo1eM6Zr'
SHARE_IMAGE = 'https://emailing.sanblasreservaambiental.org/assets/img/hotel-compartir.jpg'
LOCALES = {'es':'es_ES','en':'en_GB','fr':'fr_FR','de':'de_DE','nl':'nl_NL','ru':'ru_RU','it':'it_IT','pl':'pl_PL'}

def social_meta(d, lang, url):
    title = d['title'] + ' · San Blas Reserva Ambiental'
    description = d['intro'] + ' ' + d['offer']
    return f'''<meta property="og:type" content="website">
<meta property="og:site_name" content="San Blas Reserva Ambiental">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(url)}"><meta property="og:locale" content="{LOCALES[lang]}">
<meta property="og:image" content="{SHARE_IMAGE}"><meta property="og:image:secure_url" content="{SHARE_IMAGE}">
<meta property="og:image:type" content="image/jpeg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(d['heroAlt'])}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(description)}"><meta name="twitter:image" content="{SHARE_IMAGE}"><meta name="twitter:image:alt" content="{e(d['heroAlt'])}">'''


def icon(name):
    paths = {
        'arrow':'<path d="M5 12h14m-6-6 6 6-6 6"/>',
        'leaf':'<path d="M20 4c-8-1-15 3-15 9a6 6 0 0 0 6 6c6 0 10-7 9-15Z"/><path d="M4 21 16 9"/>',
        'inside':'<path d="m3 9 9-6 9 6H3Zm2 12h14M7 11v7m5-7v7m5-7v7"/>',
        'ticket':'<path d="M3 7h18v3a2 2 0 0 0 0 4v3H3v-3a2 2 0 0 0 0-4V7Z"/><path d="M16 7v2m0 2v2m0 2v2"/>',
        'reception':'<path d="M5 17a7 7 0 0 1 14 0M3 17h18M3 21h18M12 6v3m-2-3h4"/>',
        'email':'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
        'chat':'<path d="M21 11.5a9 9 0 0 1-13 8L3 21l1.5-5A9 9 0 1 1 21 11.5Z"/><path d="M8 9h8m-8 5h5"/>',
        'copy':'<rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 5V3H4v14h1"/>',
        'chevron':'<path d="m6 9 6 6 6-6"/>',
    }
    return f'<svg class="ui-icon" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>'

def button(label, url):
    return f'<a class="button" href="{e(url)}">{icon("arrow")}<span>{e(label)}</span></a>'

def booking(d, key, email=False):
    url = (hotel_url(lang) + f'?modalidad={key}#reserve') if email else '#reserve'
    symbol = '🥾' if key == 'full' else '🏛'
    if email:
        return f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td bgcolor="#eee3c9" style="padding:14px 20px;border-radius:10px"><a href="{e(url)}" style="font:bold 16px K2D,Arial,sans-serif;color:#1a1614;text-decoration:none"><span aria-hidden="true">{symbol}</span> {e(d[key+"Cta"])} →</a></td></tr></table>'
    return f'<a class="button" href="{url}" data-option="{key}">{icon("leaf" if key=="full" else "inside")}<span>{e(d[key+"Cta"])}</span></a>'

def email_other_options(d):
    return f'<h2 style="font:700 22px K2D,Arial,sans-serif">{e(d["onlineTitle"])}</h2><p><a style="color:#1a1614" href="{EXPERIENCES["full"]}">{e(d["full"])}</a><br><a style="color:#1a1614" href="{EXPERIENCES["inside"]}">{e(d["inside"])}</a></p><h2 style="font:700 22px K2D,Arial,sans-serif">{e(d["hotelTitle"])}</h2><p>{e(d["receptionPhone"])}<br><a style="color:#1a1614" href="tel:+34922749010">{e(d["receptionExternalPhone"])}</a></p><h2 style="font:700 22px K2D,Arial,sans-serif">{e(d["directTitle"])}</h2><p><a style="color:#1a1614" href="{hotel_url(lang)}#reserve">{e(d["bookingForm"]["title"])}</a></p>'

def reservation_section(d):
    return f'''<section class="content reservation" id="reserve"><div class="wrap"><h2>{e(d['bookingTitle'])}</h2><p id="booking-selected-visit" class="selected-visit" role="status"></p>
<div class="booking-methods">
<details class="booking-method" name="booking-method" id="booking-online"><summary>{icon('ticket')}<span class="method-title">{e(d['onlineTitle'])}</span><span class="fold-arrow">{icon('chevron')}</span></summary><div class="method-content"><div class="experience-links">{button(d['full'],EXPERIENCES['full'])}{button(d['inside'],EXPERIENCES['inside'])}</div></div></details>
<details class="booking-method" name="booking-method" id="booking-hotel"><summary>{icon('reception')}<span class="method-title">{e(d['hotelTitle'])}</span><span class="fold-arrow">{icon('chevron')}</span></summary><div class="method-content"><p>{e(d['receptionCta'])}</p><p>{e(d['receptionPhone'])}<br><a href="tel:+34922749010">{e(d['receptionExternalPhone'])}</a></p><p>{e(d['contactText'])}</p></div></details>
<details class="booking-method" name="booking-method" id="booking-direct"><summary>{icon('email')}<span class="method-title">{e(d['directTitle'])}</span><span class="fold-arrow">{icon('chevron')}</span></summary><div class="method-content">{reservation_form(d)}</div></details>
</div></div></section>'''

def reservation_form(d):
    f = d['bookingForm']
    fields = ''
    for key, auto in [('surname','family-name'),('givenName','given-name'),('room','off')]:
        required = '' if key == 'givenName' else ' required'
        optional=f' <span class="optional">{e(f["optional"])}</span>' if key=='givenName' else ''
        fields += f'<div class="field"><label for="booking-{key}">{e(f[key])}{optional}</label><input id="booking-{key}" name="{key}" type="text" autocomplete="{auto}"{required} maxlength="100" dir="auto" aria-describedby="booking-{key}-error"><p id="booking-{key}-error" class="field-error" hidden></p></div>'
    for key, value in [('adults',1),('children',0)]:
        fields += f'<div class="field"><label for="booking-{key}">{e(f[key])}</label><input id="booking-{key}" name="{key}" type="number" min="0" step="1" value="{value}" inputmode="numeric" required aria-describedby="booking-{key}-error"><p id="booking-{key}-error" class="field-error" hidden></p></div>'
    english_keys = ['fullRequest','insideRequest','surname','givenName','room','adults','children','fullAdults','fullChildren']
    message_labels = {key:DATA['en']['bookingForm'][key] for key in english_keys}
    message_labels.update(full=DATA['en']['bookingForm']['fullShort'], inside=DATA['en']['bookingForm']['insideShort'])
    config = {**f, 'full':d['full'], 'inside':d['inside'], 'fullSchedule':d['fullSchedule'], 'insideSchedule':d['insideSchedule'], 'lang':lang, 'availability':AVAILABILITY, 'messageLabels':message_labels}
    return f'''<p class="intro">{e(f['intro'])}</p><p id="booking-support" class="form-support">{e(f['bookingUnavailable'])} <a href="mailto:{ADDRESS}">{ADDRESS}</a> · <a href="tel:+34922097040">+34 922 097 040</a></p>
<form id="booking-form" method="post">
<div class="booking-first"><div class="field"><label for="booking-option">{e(f['option'])}</label><select id="booking-option" name="option" required aria-describedby="booking-schedule"><option value="full">{e(f['fullShort'])} · 09:30</option><option value="inside">{e(f['insideShort'])} · 11:30</option></select></div>
<div class="field date-field"><label for="booking-date">{e(f['date'])}</label><div class="date-control"><input id="booking-date" name="date" type="text" placeholder="{e(f['datePlaceholder'])}" autocomplete="off" required aria-describedby="booking-schedule booking-date-format"><button id="calendar-toggle" type="button" class="calendar-toggle" aria-label="{e(f['openCalendar'])}" aria-expanded="false" aria-controls="booking-calendar"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v5m10-5v5M3 11h18"/></svg></button></div><small id="booking-date-format" class="date-format">{e(f['dateHint'])}</small><div id="booking-calendar" class="calendar" role="dialog" aria-label="{e(f['openCalendar'])}" hidden><div class="calendar-nav"><button type="button" id="calendar-prev" aria-label="{e(f['previousMonth'])}">{icon('chevron')}</button><strong id="calendar-month" aria-live="polite"></strong><button type="button" id="calendar-next" aria-label="{e(f['nextMonth'])}">{icon('chevron')}</button></div><div id="calendar-grid" role="grid" aria-labelledby="calendar-month"></div></div></div></div><p class="note" id="booking-schedule">{e(d['fullSchedule'])}</p>
<div id="booking-date-error" class="date-error" hidden><p id="booking-date-error-text" role="status"></p><div class="date-alternatives"><div class="date-alternative"><p id="booking-earliest-date"></p><button id="booking-use-date" type="button" class="button" data-date-alternative="earliest" aria-describedby="booking-earliest-date">{e(f['useDate'])}</button></div><div class="date-alternative"><p id="booking-after-selected-date"></p><button id="booking-use-selected-date" type="button" class="button" data-date-alternative="afterSelected" aria-describedby="booking-after-selected-date">{e(f['useDate'])}</button></div></div></div>
<p id="booking-today-notice" class="today-notice" role="status" hidden>{e(f['todayNotice'])}</p>
<div id="booking-today-fallback" class="today-fallback" hidden><p role="status">{e(f['todayClosed'])}</p><div class="fallback-options"><div><span aria-hidden="true">🛎</span> {e(d['receptionCta'])}<small class="reception-phone">{e(d['receptionPhone'])}<br><a href="tel:+34922749010">{e(d['receptionExternalPhone'])}</a></small></div></div></div>
<fieldset id="booking-details" class="booking-details" hidden disabled><div class="form-grid">{fields}</div>
<button class="button" type="submit" id="booking-submit" disabled>{icon('arrow')}<span>{e(f['submit'])}</span></button></fieldset>
</form>
<div id="booking-result" class="booking-result" hidden tabindex="-1" aria-labelledby="booking-summary-title"><div class="review-heading"><h3 id="booking-summary-title">{e(f['summary'])}</h3><button id="booking-edit" type="button" class="edit-request">{e(f['editRequest'])}</button></div><p role="status">{e(f['pending'])}</p><p class="review-note">{e(f['englishMessage'])}</p><pre id="booking-summary"></pre><label class="charge-consent"><input id="booking-consent" type="checkbox" required aria-describedby="booking-consent-hint"><span id="booking-consent-label"></span></label><p id="booking-consent-hint" class="review-note">{e(f['consentHint'])}</p><h4>{e(f['sendChoice'])}</h4><div class="send-options"><button type="button" class="button" data-send-channel="email" disabled>{icon('email')}<span>{e(f['emailSend'])}</span></button><button type="button" class="button" data-send-channel="whatsapp" disabled>{icon('chat')}<span>{e(f['whatsappSend'])}</span></button></div><button type="button" class="button copy-request" id="booking-copy" disabled>{icon('copy')}<span>{e(f['copyRequest'])}</span></button><p id="booking-copy-status" class="copy-status" role="status"></p></div>
<script id="booking-config" type="application/json">{json.dumps(config,ensure_ascii=False).replace('<', chr(92)+'u003c')}</script><script defer src="hotel-booking.js"></script>
'''


def price(d, key, email=False):
    if not email:
        old = '22,50 €' if key == 'full' else '15 €'
        rows = [('rateAdults', '22,50 €', '15 €'), ('rateChildren', '14,50 €', '8 €')] if key == 'full' else [('adultLabel', '15 €', '10 €'), ('rateAllChildren', '15 €', '10 €')]
        lines = ''.join(f'<div class="rate-line"><span>{e(d[label])}</span><span class="rate-values"><del>{e(before)}</del><strong>{e(after)}</strong></span></div>' for label,before,after in rows)
        return f'<div class="option-prices"><div class="price-stack"><span class="price">{e(d[key+"Price"])}</span><del class="price-original"><span class="sr-only">{e(d["nonresidentLabel"])}: </span>{old}</del></div><p class="note rate-caption">{e(d["rateLabel"])}</p><div class="rate-comparison">{lines}</div></div>'
    style = ' style="font:bold 30px Arial,sans-serif;margin:12px 0"' if email else ' class="price"'
    qualifier = ' · ' + d['adultLabel'] if key == 'full' else ''
    rates = d['fullRates']+' · '+d['fullComparison'] if key == 'full' else d['insideRates']
    return f'<p{style}>{e(d[key+"Price"])}</p><p class="note">{e(d["rateLabel"]+qualifier)}</p><p class="rate-comparison">{e(rates)}</p>'

for lang, d in DATA.items():
    name = f'intern_email_2.0_{lang}.html'
    nav = ' '.join(f'<a href="{hotel_url(code)}" lang="{code}" hreflang="{code}" title="{e(v["name"])}" aria-label="{e(v["name"])}"'
                   + (' aria-current="page"' if code == lang else '') + f'><img src="../../assets/flags/{code}.svg" width="32" height="32" alt=""></a>' for code, v in DATA.items())
    alternates = '\n'.join(f'<link rel="alternate" hreflang="{code}" href="{hotel_url(code)}">' for code in DATA)
    cards = ''
    for key, img, alt in [('full', 'hotel-barranco.webp', 'fullAlt'), ('inside', 'hotel-centro.webp', 'insideAlt')]:
        cards += f'''<article class="option" id="{key}">
<img src="../../assets/img/{img}" alt="{e(d[alt])}" width="1200" height="{737 if key == 'full' else 1050}" loading="lazy">
<div class="copy"><p class="tag">{e(d[key+'Tag'])}</p><h3>{e(d[key])}</h3>
{price(d,key)}<p class="schedule"><strong>{e(d[key+'Schedule'])}</strong><br>{e(d['durationLabel'])}: {e(d[key+'Duration'])}<br>{e(d['limited'])}</p>
<p>{e(d[key+'Text'])}</p><p class="note">{e(d[key+'Note'])}</p>
{booking(d,key)}</div></article>'''
    page = f'''<!doctype html>
<html lang="{lang}"><head><meta name="robots" content="noindex, nofollow, noarchive"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(d['title'])} · San Blas Reserva Ambiental</title><meta name="description" content="{e(d['intro'])}">
<link rel="canonical" href="{hotel_url(lang)}">{alternates}
<link rel="icon" type="image/png" href="../../assets/img/logo-reserva.png">{FONTS}<link rel="stylesheet" href="hotel.css">
{social_meta(d,lang,hotel_url(lang))}</head>
<body><a class="skip" href="#main">{e(d['skip'])}</a>
<main id="main"><section class="hero"><img src="../../assets/img/hotel-presa.jpg" alt="{e(d['heroAlt'])}" width="1380" height="900" srcset="../../assets/img/hotel-presa-800.jpg 800w, ../../assets/img/hotel-presa.jpg 1380w" sizes="100vw" fetchpriority="high">
<header class="top"><div class="wrap"><a class="brand" href="{hotel_url(lang)}"><img src="../../assets/img/logo-blanco.png" width="160" height="160" alt="San Blas Reserva Ambiental · Tenerife"></a><nav class="languages" aria-label="{e(d['languagesLabel'])}">{nav}</nav></div></header>
<div class="wrap hero-copy"><p class="kicker">{e(d['kicker'])}</p><h1>{e(d['title'])}</h1><p>{e(d['intro'])}</p><p class="offer">{e(d['offer'])}<small><a href="#discount-note">{e(d['offerNote'])}</a></small></p><p>{e(d['limited'])}</p>{button(d['choose'], '#options')}</div></section>
<section class="content" id="options"><div class="wrap"><div class="intro"><h2>{e(d['choose'])}</h2><p>{e(d['lead'])}</p></div><div class="options">{cards}</div></div></section>
<section class="content practical"><div class="wrap"><h2>{e(d['practical'])}</h2><p><strong>{e(d['meetingLabel'])}:</strong> {e(d['meetingPoint'])}</p><p>{e(d['details'])}</p><p>{e(d['access'])}</p></div></section>
{reservation_section(d)}
<section class="content contact" id="contact"><div class="wrap"><h2>San Blas Reserva Ambiental</h2>
<p style="margin-top:24px"><a href="mailto:{ADDRESS}">{ADDRESS}</a><br><a href="tel:+34922097040">+34 922 097 040</a></p></div></section></main>
<footer>San Blas Reserva Ambiental · Barceló Tenerife<br>Avenida Greñamora 1 · 38639 · San Miguel de Abona · Tenerife<p class="discount-note" id="discount-note"><strong>¹ {e(d['discountTitle'])}.</strong> {e(d['discountNote'])}</p></footer></body></html>'''
    (OUT / name).write_text(page, encoding='utf-8')
    destination = ROOT / 'hotel' / lang
    destination.mkdir(parents=True, exist_ok=True)
    nested_page = page.replace('src="hotel-booking.js"', 'src="../../mailing/emails/hotel-booking.js"').replace('href="hotel.css"', 'href="../../mailing/emails/hotel.css"')
    (destination / 'index.html').write_text(nested_page, encoding='utf-8')
    if lang == 'en':
        english_root = page.replace('../../assets/', '../assets/').replace('src="hotel-booking.js"', 'src="../mailing/emails/hotel-booking.js"').replace('href="hotel.css"', 'href="../mailing/emails/hotel.css"')
        (ROOT / 'hotel' / 'index.html').write_text(english_root, encoding='utf-8')

    if lang not in ('es', 'en'):
        continue
    email_copy = {
        'es': {
            'heading': d['title'],
            'intro': d['intro'],
            'fullTitle': 'Visita completa · Naturaleza e historia',
            'full': 'Paseo guiado por la Reserva Ambiental y visita al Centro de Interpretación, el Museo y el Túnel de la Experiencia Histórica.',
            'insideTitle': 'Solo interiores · La opción cómoda',
            'inside': 'Visita guiada al Centro de Interpretación, el Museo y el Túnel de la Experiencia Histórica, sin recorrido exterior.',
            'cardTitle': 'Dos formas de descubrir San Blas',
            'cardText': 'Conozca las dos modalidades y consulte horarios, disponibilidad y opciones de reserva en la ficha de la actividad.',
            'cta': 'Ver la actividad y reservar',
            'languages': 'La ficha está disponible en ocho idiomas',
            'reviewHeading': '¿Ya nos visitaste?',
            'reviewCta': '¿Qué te pareció? Cuéntanos tu experiencia',
        },
        'en': {
            'heading': d['title'],
            'intro': d['intro'],
            'fullTitle': 'Complete visit · Nature and history',
            'full': 'A guided walk through the Environmental Reserve, followed by the Interpretation Centre, Museum and Historical Experience Tunnel.',
            'insideTitle': 'Indoor visit · The comfortable option',
            'inside': 'A guided visit to the Interpretation Centre, Museum and Historical Experience Tunnel, without the outdoor walk.',
            'cardTitle': 'Two ways to discover San Blas',
            'cardText': 'Explore both options and check schedules, availability and booking options on the activity page.',
            'cta': 'Explore the activity and book',
            'languages': 'The activity page is available in eight languages',
            'reviewHeading': 'Have you already visited us?',
            'reviewCta': 'What did you think? Share your experience',
        },
    }[lang]
    language_links = ' · '.join(f'<a style="font-family:Georgia,serif;font-size:13px;line-height:26px;color:#574c43;text-decoration:underline;" lang="{code}" href="{hotel_url(code)}">{e(v["name"])}</a>' for code,v in DATA.items())
    language_text = '\n'.join(f'{v["name"]}: {hotel_url(code)}' for code,v in DATA.items())
    email_url = 'https://emailing.sanblasreservaambiental.org/hotel/correo/' + lang + '.html'
    # Tablas, tipografía explícita y alternativa VML para Outlook clásico/Word.
    text_style = "font-family:'Source Serif 4',Georgia,'Times New Roman',serif;font-size:16px;line-height:26px;color:#1a1614;"
    heading_style = "font-family:K2D,Arial,Helvetica,sans-serif;color:#1a1614;"
    email_html = f'''<!doctype html>
<html lang="{lang}" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office"><head>
<meta charset="utf-8"><meta name="robots" content="noindex, nofollow, noarchive"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="x-apple-disable-message-reformatting">
<title>{e(email_copy['heading'])}</title>
<!--[if !mso]><!-->{FONTS}<!--<![endif]-->
<!--[if mso]><xml><o:OfficeDocumentSettings><o:AllowPNG/><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml>
<style type="text/css">table{{border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt;}}td,p,a{{font-family:Georgia,'Times New Roman',serif;}}h1,h2,.email-heading{{font-family:Arial,Helvetica,sans-serif !important;}}.email-stars{{font-family:'Segoe UI Symbol',Arial,sans-serif !important;}}</style><![endif]-->
{social_meta(d,lang,email_url)}</head>
<body bgcolor="#faf8f3" style="margin:0;padding:0;background-color:#faf8f3;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;">
<div style="display:none;font-size:1px;line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;mso-hide:all;">{e(d['offer'])} {e(d['limited'])}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#faf8f3" style="width:100%;border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt;"><tr><td align="center" valign="top" style="padding:20px 8px;">
<!--[if mso]><table role="presentation" width="600" align="center" cellpadding="0" cellspacing="0" border="0"><tr><td width="600" valign="top"><![endif]-->
<table role="presentation" width="100%" align="center" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px;border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt;">
<tr><td style="padding:0 0 16px;{text_style}font-size:13px;line-height:20px;"><a href="{email_url}" style="font-family:Georgia,serif;font-size:13px;line-height:20px;color:#574c43;text-decoration:underline;">{e(d['browser'])}</a></td></tr>
<tr><td style="padding:0 0 16px;{text_style}">{e(d['greeting'])}</td></tr>
<tr><td style="padding:0 0 16px;"><h1 class="email-heading" style="margin:0;{heading_style}font-size:26px;line-height:34px;font-weight:700;mso-line-height-rule:at-least;">{e(email_copy['heading'])}</h1></td></tr>
<tr><td style="padding:0 0 20px;{text_style}">{e(email_copy['intro'])}</td></tr>
<tr><td bgcolor="#eee3c9" style="padding:16px;{text_style}background-color:#eee3c9;"><strong>{e(d['offer'])}</strong><br><a href="{hotel_url(lang)}#discount-note" style="font-family:Georgia,serif;font-size:12px;line-height:20px;font-weight:normal;color:#574c43;text-decoration:underline;">{e(d['offerNote'])}</a></td></tr>
<tr><td style="padding:16px 0;{text_style}"><strong>{e(d['limited'])}</strong></td></tr>
<tr><td style="padding:0 0 16px;{text_style}"><strong>{e(email_copy['fullTitle'])}</strong><br>{e(email_copy['full'])}</td></tr>
<tr><td style="padding:0 0 24px;{text_style}"><strong>{e(email_copy['insideTitle'])}</strong><br>{e(email_copy['inside'])}</td></tr>
<tr><td style="padding:0 0 20px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="width:100%;border-collapse:collapse;background-color:#ffffff;mso-table-lspace:0pt;mso-table-rspace:0pt;">
<tr><td style="padding:0;font-size:0;line-height:0;"><a href="{hotel_url(lang)}" style="text-decoration:none;"><img src="{SHARE_IMAGE}" alt="{e(d['heroAlt'])}" width="600" height="315" border="0" style="display:block;border:0;outline:none;text-decoration:none;width:100%;max-width:600px;height:auto;-ms-interpolation-mode:bicubic;"></a></td></tr>
<tr><td style="padding:22px 22px 8px;{text_style}font-size:12px;line-height:18px;color:#574c43;">San Blas Reserva Ambiental · Barceló Tenerife</td></tr>
<tr><td style="padding:0 22px 10px;"><h2 class="email-heading" style="margin:0;{heading_style}font-size:23px;line-height:30px;font-weight:700;mso-line-height-rule:at-least;">{e(email_copy['cardTitle'])}</h2></td></tr>
<tr><td style="padding:0 22px 18px;{text_style}">{e(email_copy['cardText'])}</td></tr>
<tr><td align="left" style="padding:0 22px 22px;">
<!--[if mso]><v:roundrect href="{hotel_url(lang)}" style="height:50px;v-text-anchor:middle;width:310px;" arcsize="96%" strokecolor="#eee3c9" fillcolor="#eee3c9"><w:anchorlock xmlns:w="urn:schemas-microsoft-com:office:word"/><center style="font-family:Arial,Helvetica,sans-serif;font-size:16px;font-weight:bold;color:#1a1614;">{e(email_copy['cta'])} →</center></v:roundrect><![endif]-->
<!--[if !mso]><!--><table role="presentation" cellpadding="0" cellspacing="0" border="0" style="border-collapse:separate;"><tr><td align="center" bgcolor="#eee3c9" style="background-color:#eee3c9;border-radius:24px;"><a href="{hotel_url(lang)}" class="email-heading" style="display:inline-block;border:1px solid #eee3c9;border-radius:24px;padding:12px 20px;{heading_style}font-size:16px;line-height:24px;font-weight:700;text-decoration:none;">{e(email_copy['cta'])} →</a></td></tr></table><!--<![endif]-->
</td></tr></table></td></tr>
<tr><td style="padding:0 0 20px;{text_style}font-size:13px;line-height:24px;"><strong>{e(email_copy['languages'])}</strong><br>{language_links}</td></tr>
<tr><td style="padding:0 0 20px;{text_style}">{e(d['signoff'])}<br><strong>San Blas Reserva Ambiental · Barceló Tenerife</strong><br><a href="mailto:{ADDRESS}" style="font-family:Georgia,serif;font-size:16px;line-height:26px;color:#574c43;text-decoration:underline;">{ADDRESS}</a><br><a href="https://wa.me/34922097040" style="font-family:Georgia,serif;font-size:16px;line-height:26px;color:#574c43;text-decoration:underline;">WhatsApp: +34 922 097 040</a></td></tr>
<tr><td style="border-top:1px solid #d8ccb4;padding:16px 0 0;{text_style}font-size:15px;line-height:24px;"><strong>{e(email_copy['reviewHeading'])}</strong><br>{e(email_copy['reviewCta'])}</td></tr>
<tr><td style="padding:8px 0 16px;"><a href="{REVIEW_URL}" class="email-stars" aria-label="{e(email_copy['reviewCta'])}" title="{e(email_copy['reviewCta'])}" style="font-family:'Segoe UI Symbol','Arial Unicode MS',Arial,sans-serif;font-size:30px;line-height:45px;color:#9a640c;letter-spacing:4px;text-decoration:none;">★★★★★</a></td></tr>
<tr><td style="padding:0 0 16px;{text_style}font-size:12px;line-height:18px;"><a href="mailto:{ADDRESS}?subject=BAJA" style="font-family:Georgia,serif;font-size:12px;line-height:18px;color:#574c43;text-decoration:underline;">{e(d['unsubscribe'])}</a></td></tr>
</table><!--[if mso]></td></tr></table><![endif]--></td></tr></table></body></html>'''
    plain = '\n\n'.join([d['greeting'], email_copy['heading'], email_copy['intro'], d['offer'], d['offerNote']+' '+hotel_url(lang)+'#discount-note', d['limited'], email_copy['fullTitle'], email_copy['full'], email_copy['insideTitle'], email_copy['inside'], email_copy['cardText'], email_copy['cta']+': '+hotel_url(lang), email_copy['languages'], language_text, d['signoff'], 'San Blas Reserva Ambiental · Barceló Tenerife', ADDRESS, 'WhatsApp: +34 922 097 040 · https://wa.me/34922097040', email_copy['reviewHeading'], email_copy['reviewCta']+'\n★★★★★ '+REVIEW_URL, d['unsubscribe']])
    stem = EMAIL_OUT / lang
    stem.with_suffix('.html').write_text(email_html, encoding='utf-8')
    stem.with_suffix('.txt').write_text(plain, encoding='utf-8')
    msg = EmailMessage(policy=policy.SMTP)
    msg['Subject'] = d['subject']
    msg['From'] = f'San Blas Reserva Ambiental <{ADDRESS}>'
    msg['X-Unsent'] = '1'
    msg.set_content(plain)
    msg.add_alternative(email_html, subtype='html')
    stem.with_suffix('.eml').write_bytes(msg.as_bytes())
    # Conservar las direcciones anteriores ya compartidas.
    for suffix in ('.html', '.txt', '.eml'):
        (OUT / f'correo-huespedes-{lang}{suffix}').write_bytes(stem.with_suffix(suffix).read_bytes())

# Índices deliberadamente vacíos; las páginas de idioma conservan su URL directa.
blank_index = '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow, noarchive"><title></title></head><body></body></html>\n'
for path in (ROOT/'index.html', ROOT/'mailing'/'index.html', OUT/'index.html', EMAIL_OUT/'index.html'):
    path.write_text(blank_index, encoding='utf-8')
print(f'Generadas {len(DATA)} páginas online, 2 correos HTML/TXT/EML y 4 índices vacíos.')
