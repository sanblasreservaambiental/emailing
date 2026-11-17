import test from 'node:test';
import assert from 'node:assert/strict';
import bookingFunctions from '../mailing/emails/hotel-booking.js';
const {parseISODate,validCounts,availableDate, nextAvailableDate, receptionOnly, selectableDate, suggestedDate, dateProblem, nextSelectableDate, dateAlternatives, canaryToday, totals, message, chargeConsent, destination} = bookingFunctions;

test('fechas según cada modalidad y sin días pasados o inexistentes', () => {
  const today = new Date('2026-11-17T08:00:00Z'); // Martes
  for (const [date, full, inside] of [
    ['2026-11-17',true,true], ['2026-11-18',true,false], ['2026-11-19',true,true],
    ['2026-11-20',true,true], ['2026-11-21',true,false], ['2026-11-22',false,false], ['2026-11-23',false,false],
  ]) {
    assert.equal(availableDate('full',date,today),full);
    assert.equal(availableDate('inside',date,today),inside);
  }
  for (const date of ['2026-11-13','2026-11-31','2027-02-30','','bad']) assert.equal(availableDate('full',date,today),false);
  assert.equal(availableDate('unknown','2026-11-17',today),false);
  assert.equal(canaryToday(new Date('2026-06-10T23:30:00Z')),'2026-06-11');
});

test('tarifas y ahorros para adultos y niños', () => {
  assert.deepEqual(totals('full',1,1),{guest:23,nonresident:37,saving:14});
  assert.deepEqual(totals('inside',1,1),{guest:20,nonresident:30,saving:10});
  assert.deepEqual(totals('full',2,3),{guest:54,nonresident:88.5,saving:34.5});
});

test('rechaza fechas deformadas y cantidades que producirían importes inválidos', () => {
  for(const value of ['2027-02-29','2026-13-01','2026-02-30','2026-1-01','2026-01-01extra','',null])assert.equal(parseISODate(value),null);
  assert.equal(parseISODate('2028-02-29').toISOString().slice(0,10),'2028-02-29');
  for(const [a,c] of [[-1,0],[1.5,0],[Infinity,0],[NaN,0],[1,1e308],[Number.MAX_SAFE_INTEGER,0]]){
    assert.equal(validCounts(a,c),false);
    assert.throws(()=>totals('full',a,c),RangeError);
    assert.throws(()=>totals('inside',a,c),RangeError);
  }
  assert.equal(validCounts(20,30),true);
  assert.throws(()=>totals('unknown',1,0),RangeError);
  assert.equal(nextSelectableDate('unknown','2026-11-18'),null);
  assert.deepEqual(dateAlternatives('inside','9999-12-31',new Date('2026-11-17T12:00:00Z')),[{kind:'earliest',date:'2026-11-19'}]);
});

test('cierre diario a las 09:00 y próxima fecha hábil según hora de Canarias', () => {
  assert.equal(availableDate('full','2026-11-17',new Date('2026-11-17T09:00:00Z')),true);
  assert.equal(availableDate('full','2026-11-17',new Date('2026-11-17T09:00:00.001Z')),false);
  assert.equal(availableDate('inside','2026-11-17',new Date('2026-11-17T09:00:00Z')),true);
  assert.equal(availableDate('inside','2026-11-17',new Date('2026-11-17T09:00:00.001Z')),false);
  assert.equal(nextAvailableDate('full',new Date('2026-11-17T09:01:00Z')),'2026-11-18');
  assert.equal(nextAvailableDate('inside',new Date('2026-11-17T09:01:00Z')),'2026-11-19');
  assert.equal(nextAvailableDate('full',new Date('2026-11-21T09:01:00Z')),'2026-11-24');
  assert.equal(nextAvailableDate('inside',new Date('2026-11-20T09:01:00Z')),'2026-11-24');
  // En verano Canarias va una hora por delante de UTC.
  assert.equal(availableDate('full','2026-06-09',new Date('2026-06-09T08:00:00Z')),true);
  assert.equal(availableDate('full','2026-06-09',new Date('2026-06-09T08:00:01Z')),false);
  assert.equal(nextAvailableDate('full',new Date('2026-06-09T08:00:01Z')),'2026-06-10');
});

test('interiores hoy tras el cierre permite solo recepción; futuras fechas recuperan el formulario', () => {
  const before = new Date('2026-11-17T08:59:00Z');
  const after = new Date('2026-11-17T09:01:00Z');
  assert.equal(receptionOnly('inside','2026-11-17',before),false);
  assert.equal(receptionOnly('inside','2026-11-17',after),true);
  assert.equal(selectableDate('inside','2026-11-17',after),true);
  assert.equal(availableDate('inside','2026-11-17',after),false);
  assert.equal(suggestedDate('inside',after),'2026-11-17');
  assert.equal(receptionOnly('inside','2026-11-19',after),false);
  assert.equal(availableDate('inside','2026-11-19',after),true);
  assert.equal(receptionOnly('full','2026-11-17',after),false);
  assert.equal(suggestedDate('full',after),'2026-11-18');
  // Los días sin sesión interior no se ofrecen como visita para hoy.
  assert.equal(suggestedDate('inside',new Date('2026-11-18T10:00:00Z')),'2026-11-19');
  assert.equal(receptionOnly('inside','2026-11-18',new Date('2026-11-18T10:00:00Z')),false);
});

test('después de las 11:00 interiores pasa a la siguiente fecha hábil', () => {
  const atEleven = new Date('2026-11-17T11:00:00Z');
  const afterEleven = new Date('2026-11-17T11:00:00.001Z');
  assert.equal(receptionOnly('inside','2026-11-17',new Date('2026-11-17T10:59:59Z')),true);
  assert.equal(receptionOnly('inside','2026-11-17',atEleven),false);
  assert.equal(suggestedDate('inside',atEleven),'2026-11-19');
  assert.equal(receptionOnly('inside','2026-11-17',afterEleven),false);
  assert.equal(selectableDate('inside','2026-11-17',afterEleven),false);
  assert.equal(suggestedDate('inside',afterEleven),'2026-11-19');
  assert.equal(suggestedDate('inside',new Date('2026-11-20T11:01:00Z')),'2026-11-24');
  assert.equal(suggestedDate('inside',new Date('2026-06-09T10:01:00Z')),'2026-06-11');
});

test('fechas llenas y cierres se saltan sin ofrecer recepción en un día bloqueado', () => {
  const now = new Date('2026-11-17T10:00:00Z');
  const availability = {closedDates:['2026-11-20'], fullyBookedDates:{full:['2026-11-18'],inside:['2026-11-17','2026-11-19','2026-11-24']}};
  assert.equal(receptionOnly('inside','2026-11-17',now,availability),false);
  assert.equal(selectableDate('inside','2026-11-17',now,availability),false);
  assert.equal(suggestedDate('inside',now,availability),'2026-11-26');
  assert.equal(suggestedDate('full',now,availability),'2026-11-19');
  assert.equal(availableDate('full','2026-11-20',now,availability),false);
  assert.equal(availableDate('inside','2026-11-20',now,availability),false);
  assert.equal(availableDate('full','2026-11-24',now,availability),true);
  assert.equal(availableDate('inside','2026-11-24',now,availability),false);
});

test('fecha incompatible explica el motivo y ofrece una alternativa posterior sin cambiar la entrada', () => {
  const now=new Date('2026-11-17T12:00:00Z');
  const input='2026-11-23'; // Lunes
  assert.equal(dateProblem('inside',input,now),'noSessionDate');
  assert.equal(nextSelectableDate('inside',input,now),'2026-11-24');
  assert.equal(dateProblem('inside','2026-11-18',now),'noSessionDate');
  assert.equal(nextSelectableDate('inside','2026-11-18',now),'2026-11-19');
  assert.equal(dateProblem('inside','2026-11-17',now),'todayCutoff');
  assert.equal(dateProblem('full','2026-11-16',now),'pastDate');
  assert.equal(dateProblem('full','2026-11-31',now),'invalidDate');
  const availability={closedDates:['2026-11-24'],fullyBookedDates:{full:[],inside:['2026-11-26']}};
  assert.equal(dateProblem('inside','2026-11-24',now,availability),'closedDate');
  assert.equal(nextSelectableDate('inside',input,now,availability),'2026-11-27');
  for(const date of ['2026-11-18','2026-11-21','2026-11-22','2026-11-23'])assert.equal(selectableDate('inside',date,now),false);
  for(const date of ['2026-11-22','2026-11-23'])assert.equal(selectableDate('full',date,now),false);
});

test('ofrece la próxima desde hoy y la próxima posterior a la seleccionada, sin duplicarlas', () => {
  const now=new Date('2026-11-17T12:00:00Z');
  assert.deepEqual(dateAlternatives('inside','2026-11-23',now),[
    {kind:'earliest',date:'2026-11-19'},
    {kind:'afterSelected',date:'2026-11-24'}
  ]);
  assert.deepEqual(dateAlternatives('inside','2026-11-18',now),[{kind:'earliest',date:'2026-11-19'}]);
  assert.deepEqual(dateAlternatives('inside','bad date',now),[{kind:'earliest',date:'2026-11-19'}]);
  assert.deepEqual(dateAlternatives('inside','2026-11-16',now),[{kind:'earliest',date:'2026-11-19'}]);
  const availability={closedDates:['2026-11-19'],fullyBookedDates:{full:[],inside:['2026-11-24']}};
  assert.deepEqual(dateAlternatives('inside','2026-11-23',now,availability),[
    {kind:'earliest',date:'2026-11-20'},
    {kind:'afterSelected',date:'2026-11-26'}
  ]);
  assert.deepEqual(dateAlternatives('full','2026-11-29',now),[
    {kind:'earliest',date:'2026-11-18'},
    {kind:'afterSelected',date:'2026-12-01'}
  ]);
});

test('resumen conserva datos y enlaces codifican el mensaje sin transmisión a Experiences', async () => {
  const {readFile} = await import('node:fs/promises');
  const data = JSON.parse(await readFile(new URL('../mailing/emails/hotel-content.json',import.meta.url),'utf8'));
  for (const [lang,d] of Object.entries(data)) {
    const labels = {...d.bookingForm,lang,messageLabels:{...data.en.bookingForm,full:data.en.full,inside:data.en.inside},full:d.full,inside:d.inside,fullSchedule:d.fullSchedule,insideSchedule:d.insideSchedule,experiences:{full:'https://example.com/full',inside:'https://example.com/inside'}};
    const booking = {option:'full',surname:'Muñoz & García',givenName:'Zoë',room:'A-12',adults:'1',children:'1',date:'2026-11-17'};
    const text = message(booking,labels);
    assert.ok(text.includes(booking.surname));
    assert.ok(!text.includes(labels.pending));
    assert.ok(!text.includes(labels.saving+':'));
    assert.ok(chargeConsent(booking,labels).includes('23'));
    assert.ok(chargeConsent(booking,labels).includes('A-12'));
    assert.ok(text.includes(data.en.bookingForm.fullChildren));
    assert.ok(text.startsWith("I'd like to book the complete visit 09:30 for November 17, 2026"));
    assert.ok(text.endsWith('userlanguage: '+lang));
    const email = new URL(destination('email',booking,labels,text));
    assert.equal(email.searchParams.get('body'),text);
    assert.equal(new URL(destination('whatsapp',booking,labels,text)).searchParams.get('text'),text);
    const special='Łódź · 李 · مرحبا · 🙂 & ? # <script>\n'+String.fromCharCode(0xD800);
    assert.equal(new URL(destination('whatsapp',booking,labels,special)).searchParams.get('text'),special.slice(0,-1)+'�');
    assert.equal(destination('experiences',booking,labels,text),null);
    assert.equal(destination('reception',booking,labels,text),null);
    assert.equal(destination('gem',booking,labels,text),null);
    booking.option='inside';
    assert.ok(chargeConsent(booking,labels).includes('20'));
    assert.ok(message(booking,labels).includes('11:30'));
    assert.equal(destination('experiences',booking,labels,text),null);
  }
});

test('mensaje inglés y aceptación del cargo coinciden con el formato de envío', async () => {
  const {readFile} = await import('node:fs/promises');
  const {en} = JSON.parse(await readFile(new URL('../mailing/emails/hotel-content.json',import.meta.url),'utf8'));
  const labels = {...en.bookingForm, lang:'en',messageLabels:{...en.bookingForm,full:en.full,inside:en.inside}};
  const data = {option:'full',date:'2026-11-18',surname:'Test',givenName:'',room:'220',adults:'1',children:'0'};
  assert.equal(message(data,labels), "I'd like to book the complete visit 09:30 for November 18, 2026\nSurname: Test\nFirst name: \nRoom: 220\nAdults (aged 12 and over): 1\nChildren (aged 3–11): 0\nuserlanguage: en");
  assert.equal(chargeConsent(data,labels),'I agree that room 220 will be charged after the visit for €15.00.');
});
