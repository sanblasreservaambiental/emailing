"""Genera páginas estáticas y correos de huéspedes. Python 3, sin dependencias."""
import json
from pathlib import Path
from html import escape as e
from email.message import EmailMessage
from email import policy
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'mailing' / 'emails'
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
            'heading': 'Descubra la Reserva Ambiental de San Blas',
            'intro': 'Durante su estancia, descubra los paisajes y la historia de San Blas con una visita guiada. Como huésped de Barceló Tenerife, disfrute de la tarifa de residente.',
            'full': 'Visita completa: recorrido exterior e interiores. Adultos: 15 € · Niños de 3 a 11 años: 8 €.',
            'inside': 'La opción cómoda: solo interiores, sin caminar por el barranco. 10 € por persona.',
            'cardTitle': 'Dos formas de descubrir San Blas',
            'cardText': 'Conozca las dos modalidades y consulte horarios, disponibilidad y opciones de reserva en la ficha de la actividad.',
            'cta': 'Ver la actividad y reservar',
            'languages': 'La ficha está disponible en ocho idiomas',
        },
        'en': {
            'heading': 'Discover the San Blas Environmental Reserve',
            'intro': 'During your stay, explore the landscapes and history of San Blas on a guided visit. As a Barceló Tenerife guest, enjoy the resident rate.',
            'full': 'Complete visit: outdoor route and indoor spaces. Adults: €15 · Children aged 3–11: €8.',
            'inside': 'The comfortable option: indoor spaces only, without walking through the ravine. €10 per person.',
            'cardTitle': 'Two ways to discover San Blas',
            'cardText': 'Explore both options and check schedules, availability and booking options on the activity page.',
            'cta': 'Explore the activity and book',
            'languages': 'The activity page is available in eight languages',
        },
    }[lang]
    language_links = ' · '.join(f'<a style="color:#574c43;line-height:2" lang="{code}" href="{hotel_url(code)}">{e(v["name"])}</a>' for code,v in DATA.items())
    language_text = '\n'.join(f'{v["name"]}: {hotel_url(code)}' for code,v in DATA.items())
    email_url = 'https://emailing.sanblasreservaambiental.org/mailing/emails/correo-huespedes-' + lang + '.html'
    # Breve presentación y ficha enlazada, con tablas y estilos en línea para correo.
    email_html = f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow, noarchive"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(email_copy['heading'])}</title>{FONTS}{social_meta(d,lang,email_url)}</head>
<body style="margin:0;background:#faf8f3;color:#1a1614;font:16px/1.6 Arial,Helvetica,sans-serif">
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all">{e(email_copy['intro'])}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" style="padding:20px 8px">
<!--[if mso]><table role="presentation" width="600"><tr><td><![endif]-->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:600px">
<tr><td style="padding:0 0 16px;font-size:13px"><a href="{email_url}" style="color:#574c43">{e(d['browser'])}</a></td></tr>
<tr><td><p>{e(d['greeting'])}</p><h1 style="font:700 26px/1.25 Arial,sans-serif">{e(email_copy['heading'])}</h1><p>{e(email_copy['intro'])}</p><ul style="padding-left:22px"><li>{e(email_copy['full'])}</li><li>{e(email_copy['inside'])}</li></ul></td></tr>
<tr><td style="padding:8px 0 16px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border:1px solid #d8ccb4;background:#ffffff">
<tr><td><a href="{hotel_url(lang)}"><img src="{SHARE_IMAGE}" alt="{e(d['heroAlt'])}" width="600" height="315" style="display:block;border:0;width:100%;max-width:600px;height:auto"></a></td></tr>
<tr><td style="padding:22px"><p style="margin:0 0 8px;color:#574c43;font-size:12px">San Blas Reserva Ambiental · Barceló Tenerife</p><h2 style="margin:0 0 10px;font:700 23px/1.3 Arial,sans-serif">{e(email_copy['cardTitle'])}</h2><p style="margin:0 0 18px">{e(email_copy['cardText'])}</p>
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td bgcolor="#eee3c9" style="padding:12px 20px;border-radius:24px"><a href="{hotel_url(lang)}" style="font:bold 16px Arial,sans-serif;color:#1a1614;text-decoration:none">{e(email_copy['cta'])} →</a></td></tr></table>
</td></tr></table></td></tr>
<tr><td><p style="font-size:13px"><b>{e(email_copy['languages'])}</b><br>{language_links}</p><p>{e(d['signoff'])}<br><b>San Blas Reserva Ambiental · Barceló Tenerife</b><br><a href="mailto:{ADDRESS}" style="color:#574c43">{ADDRESS}</a></p><p style="font-size:12px"><a href="mailto:{ADDRESS}?subject=BAJA" style="color:#574c43">{e(d['unsubscribe'])}</a></p></td></tr>
</table><!--[if mso]></td></tr></table><![endif]--></td></tr></table></body></html>'''
    plain = '\n\n'.join([d['greeting'], email_copy['heading'], email_copy['intro'], email_copy['full'], email_copy['inside'], email_copy['cardText'], email_copy['cta']+': '+hotel_url(lang), email_copy['languages'], language_text, d['signoff'], 'San Blas Reserva Ambiental · Barceló Tenerife', ADDRESS, d['unsubscribe']])
    # Fuentes de marca con alternativas para clientes sin fuentes web.
    email_html = email_html.replace('Arial,Helvetica,sans-serif', "'Source Serif 4',Georgia,serif").replace('Arial,sans-serif', 'K2D,Arial,sans-serif').replace('K2D,K2D,', 'K2D,')
    stem = OUT / f'correo-huespedes-{lang}'
    stem.with_suffix('.html').write_text(email_html, encoding='utf-8')
    stem.with_suffix('.txt').write_text(plain, encoding='utf-8')
    msg = EmailMessage(policy=policy.SMTP)
    msg['Subject'] = email_copy['heading'] + (' · Tarifa especial para huéspedes' if lang == 'es' else ' · Special rates for hotel guests')
    msg['From'] = f'San Blas Reserva Ambiental <{ADDRESS}>'
    msg['X-Unsent'] = '1'
    msg.set_content(plain)
    msg.add_alternative(email_html, subtype='html')
    stem.with_suffix('.eml').write_bytes(msg.as_bytes())

# Índices deliberadamente vacíos; las páginas de idioma conservan su URL directa.
blank_index = '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow, noarchive"><title></title></head><body></body></html>\n'
for path in (ROOT/'index.html', ROOT/'mailing'/'index.html', OUT/'index.html'):
    path.write_text(blank_index, encoding='utf-8')
print(f'Generadas {len(DATA)} páginas online, 2 correos HTML/TXT/EML y 3 índices vacíos.')
