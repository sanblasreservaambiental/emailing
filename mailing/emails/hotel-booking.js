const DAYS = {full: [2, 3, 4, 5, 6], inside: [2, 4, 5]};
// El equipo sale a la Reserva: solicitudes directas para hoy solo hasta las 09:00.
const DIRECT_CUTOFF_MINUTES = 9 * 60;
const EMPTY_AVAILABILITY = {closedDates: [], fullyBookedDates: {full: [], inside: []}};
const hasOption = option => Object.prototype.hasOwnProperty.call(DAYS,option);

function parseISODate(value) {
  if(typeof value!=='string' || !/^\d{4}-\d{2}-\d{2}$/.test(value))return null;
  const parsed=new Date(`${value}T12:00:00Z`);
  return !Number.isNaN(parsed.valueOf()) && parsed.toISOString().slice(0,10)===value ? parsed : null;
}

function validCounts(adults,children) {
  return [adults,children].every(value=>typeof value==='number' && Number.isSafeInteger(value) && value>=0)
    && Number.isSafeInteger((adults+children)*2250);
}

function canaryToday(now = new Date()) {
  const parts = new Intl.DateTimeFormat('en-GB', {timeZone: 'Atlantic/Canary', year: 'numeric', month: '2-digit', day: '2-digit'}).formatToParts(now);
  const value = type => parts.find(part => part.type === type).value;
  return `${value('year')}-${value('month')}-${value('day')}`;
}

function scheduledDate(option, date, now = new Date(), availability = EMPTY_AVAILABILITY) {
  const today = canaryToday(now);
  const parsed=parseISODate(date);
  if (!hasOption(option) || !parsed || date < today || !DAYS[option].includes(parsed.getUTCDay())) return false;
  if (availability.closedDates.includes(date) || availability.fullyBookedDates[option].includes(date)) return false;
  return true;
}

function canaryMinutes(now) {
  const clock = new Intl.DateTimeFormat('en-GB', {timeZone: 'Atlantic/Canary', hourCycle: 'h23', hour: '2-digit', minute: '2-digit', second: '2-digit'}).formatToParts(now);
  const value = type => Number(clock.find(part => part.type === type).value);
  return value('hour') * 60 + value('minute') + value('second') / 60 + now.getMilliseconds() / 60000;
}

function availableDate(option, date, now = new Date(), availability = EMPTY_AVAILABILITY) {
  if (!scheduledDate(option, date, now, availability)) return false;
  if (date !== canaryToday(now)) return true;
  return canaryMinutes(now) <= DIRECT_CUTOFF_MINUTES;
}

function receptionOnly(option, date, now = new Date(), availability = EMPTY_AVAILABILITY) {
  return option === 'inside' && date === canaryToday(now) && scheduledDate(option, date, now, availability) && !availableDate(option, date, now, availability) && canaryMinutes(now) < 11 * 60;
}

function selectableDate(option, date, now = new Date(), availability = EMPTY_AVAILABILITY) {
  return availableDate(option, date, now, availability) || receptionOnly(option, date, now, availability);
}

function suggestedDate(option, now = new Date(), availability = EMPTY_AVAILABILITY) {
  const today = canaryToday(now);
  return selectableDate(option, today, now, availability) ? today : nextAvailableDate(option, now, availability);
}

function nextAvailableDate(option, now = new Date(), availability = EMPTY_AVAILABILITY) {
  if (!hasOption(option)) return null;
  const candidate = new Date(`${canaryToday(now)}T12:00:00Z`);
  const searchDays = 8 + 7 * (availability.closedDates.length + availability.fullyBookedDates[option].length);
  for (let offset = 0; offset < searchDays; offset++) {
    const date = candidate.toISOString().slice(0, 10);
    if (availableDate(option, date, now, availability)) return date;
    candidate.setUTCDate(candidate.getUTCDate() + 1);
  }
  return null;
}

function dateProblem(option, date, now = new Date(), availability = EMPTY_AVAILABILITY) {
  const parsed=parseISODate(date);
  if (!parsed) return 'invalidDate';
  if (!hasOption(option)) return 'noSessionDate';
  if (date < canaryToday(now)) return 'pastDate';
  if (availability.closedDates.includes(date) || availability.fullyBookedDates[option].includes(date)) return 'closedDate';
  if (!DAYS[option].includes(parsed.getUTCDay())) return 'noSessionDate';
  if (!selectableDate(option,date,now,availability)) return 'todayCutoff';
  return null;
}

function nextSelectableDate(option, fromDate, now = new Date(), availability = EMPTY_AVAILABILITY) {
  const today = canaryToday(now);
  if(!hasOption(option))return null;
  const start = parseISODate(fromDate) && fromDate > today ? fromDate : today;
  const candidate = new Date(`${start}T12:00:00Z`);
  if (Number.isNaN(candidate.valueOf())) return suggestedDate(option,now,availability);
  const searchDays = 8 + 7 * (availability.closedDates.length + availability.fullyBookedDates[option].length);
  for (let offset=0;offset<searchDays;offset++) {
    const value = candidate.toISOString().slice(0,10);
    if (selectableDate(option,value,now,availability)) return value;
    candidate.setUTCDate(candidate.getUTCDate()+1);
  }
  return null;
}

function dateAlternatives(option, selectedDate, now = new Date(), availability = EMPTY_AVAILABILITY) {
  const earliest=nextSelectableDate(option,canaryToday(now),now,availability);
  const proposals=earliest ? [{kind:'earliest',date:earliest}] : [];
  const selected=parseISODate(selectedDate);
  if(!selected)return proposals;
  selected.setUTCDate(selected.getUTCDate()+1);
  if(selected.getUTCFullYear()>9999)return proposals;
  const afterSelected=nextSelectableDate(option,selected.toISOString().slice(0,10),now,availability);
  if(afterSelected && afterSelected!==earliest)proposals.push({kind:'afterSelected',date:afterSelected});
  return proposals;
}

function fullTotals(adults, children) {
  if(!validCounts(adults,children))throw new RangeError('Invalid visitor counts');
  const guest=adults*1500+children*800, nonresident=adults*2250+children*1450;
  return {guest:guest/100,nonresident:nonresident/100,saving:(nonresident-guest)/100};
}

function totals(option, adults, children) {
  if (option === 'full') return fullTotals(adults, children);
  if(option!=='inside' || !validCounts(adults,children))throw new RangeError('Invalid visitor counts');
  const count = adults + children;
  return {guest: count * 10, nonresident: count * 15, saving: count * 5};
}

function message(data, labels) {
  const english=labels.messageLabels;
  const date = new Intl.DateTimeFormat('en', {dateStyle: 'long', timeZone: 'UTC'}).format(new Date(`${data.date}T12:00:00Z`));
  const lines = [english[data.option+'Request'].replace('{date}', date),
    `${english.surname}: ${data.surname}`, `${english.givenName}: ${data.givenName}`, `${english.room}: ${data.room}`,
    `${data.option === 'full' ? english.fullAdults : english.adults}: ${data.adults}`, `${data.option === 'full' ? english.fullChildren : english.children}: ${data.children}`,
    `userlanguage: ${labels.lang}`];
  return lines.join('\n');
}

function chargeConsent(data, labels) {
  const amount = totals(data.option, Number(data.adults), Number(data.children)).guest;
  const money = new Intl.NumberFormat(labels.lang, {style:'currency', currency:'EUR'}).format(amount);
  return labels.chargeConsent.replace('{room}', data.room).replace('{amount}', money);
}

function destination(channel, data, labels, text) {
  const encode=value=>encodeURIComponent(String(value).replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]|[\uD800-\uDFFF]/g,part=>part.length===2?part:'\uFFFD'));
  if (channel === 'email') return `mailto:tenerife.ambiental-res@barcelo.com?subject=${encode('San Blas · '+labels.messageLabels[data.option])}&body=${encode(text)}`;
  if (channel === 'whatsapp') return `https://wa.me/34922097040?text=${encode(text)}`;
  return null;
}

function initializeBooking() {
  const form = document.getElementById('booking-form');
  const labels = JSON.parse(document.getElementById('booking-config').textContent);
  const availability = labels.availability;
  if(!labels.messageLabels || !Array.isArray(availability?.closedDates) || !Array.isArray(availability?.fullyBookedDates?.full) || !Array.isArray(availability?.fullyBookedDates?.inside))throw new Error('Missing booking configuration');
  const option = form.elements.option;
  const date = form.elements.date;
  const result = document.getElementById('booking-result');
  const sendButtons = document.querySelectorAll('[data-send-channel]');
  const consent = document.getElementById('booking-consent');
  const copyButton=document.getElementById('booking-copy');
  let preparedData = null;
  let preparedText = '';
  const schedule = document.getElementById('booking-schedule');
  const details = document.getElementById('booking-details');
  const todayNotice = document.getElementById('booking-today-notice');
  const fallback = document.getElementById('booking-today-fallback');
  const errorBox = document.getElementById('booking-date-error');
  const errorText = document.getElementById('booking-date-error-text');
  const proposalButtons = document.querySelectorAll('[data-date-alternative]');
  const picker = document.getElementById('booking-calendar');
  const pickerToggle = document.getElementById('calendar-toggle');
  const dateField=date.closest('.date-field');
  // Los desplegables pueden crear contenedores que recortan elementos fijos.
  document.body.appendChild(picker);
  const grid = document.getElementById('calendar-grid');
  const monthTitle = document.getElementById('calendar-month');
  let month = null;
  let proposedDates = [];
  let calendarState = '';
  let openingApp = false;
  const touched=new Set();
  const copyStatus=document.getElementById('booking-copy-status');
  const updateText=(el,value)=>{if(el.textContent!==value)el.textContent=value;};
  const collectBooking=()=>Object.fromEntries(['option','date','surname','givenName','room','adults','children'].map(key=>[key,['adults','children'].includes(key)?String(Number(form.elements[key].value)):form.elements[key].value.trim()]));
  const sameBooking=(left,right)=>left && Object.keys(right).every(key=>left[key]===right[key]);
  const invalidateReview=()=>{
    result.hidden=true;preparedData=null;preparedText='';consent.checked=false;
    for(const button of sendButtons)button.disabled=true;
    copyButton.disabled=true;
    updateText(copyStatus,'');
  };
  const calendarSignature=now=>[canaryToday(now),canaryMinutes(now)<=540?'early':canaryMinutes(now)<660?'reception':'late',option.value,month?.toISOString().slice(0,7),date.value].join('|');
  function fieldError(key,error,reveal) {
    const input=form.elements[key],visible=!!error&&(reveal||touched.has(key));
    input.setCustomValidity(error);
    input.setAttribute('aria-invalid',String(visible));
    const hint=document.getElementById(`booking-${key}-error`);hint.hidden=!visible;updateText(hint,visible?error:'');
  }
  const formatDate = value => new Intl.DateTimeFormat(labels.lang,{dateStyle:'full',timeZone:'UTC'}).format(new Date(`${value}T12:00:00Z`));
  const validate = (reveal=false) => {
    const now = new Date();
    const problem = date.value ? dateProblem(option.value,date.value,now,availability) : null;
    date.setCustomValidity(problem ? labels[problem] : '');
    date.setAttribute('aria-invalid',problem ? 'true' : 'false');
    errorBox.hidden = !problem;
    proposedDates = problem ? dateAlternatives(option.value,date.value,now,availability) : [];
    if (problem) {
      updateText(errorText,labels[problem]+' '+labels[option.value+'Schedule']);
      for(const button of proposalButtons){
        const proposal=proposedDates.find(item=>item.kind===button.dataset.dateAlternative);
        button.closest('.date-alternative').hidden=!proposal;
        if(proposal){
          updateText(document.getElementById(button.getAttribute('aria-describedby')),labels[proposal.kind+'Date'].replace('{date}',formatDate(proposal.date)));
          button.dataset.date=proposal.date;
          button.setAttribute('aria-label',labels.useDate+' · '+formatDate(proposal.date));
        }else delete button.dataset.date;
      }
      result.hidden = true;
    }
    const onlyReception = receptionOnly(option.value, date.value, now, availability);
    details.hidden = onlyReception;
    details.disabled = onlyReception;
    fallback.hidden = !onlyReception;
    todayNotice.hidden = date.value !== canaryToday(now) || !availableDate(option.value, date.value, now, availability);
    updateText(todayNotice,option.value === 'full' ? labels.fullTodayNotice : labels.todayNotice);
    date.setAttribute('aria-describedby','booking-schedule booking-date-format'+(problem ? ' booking-date-error-text' : '')+(!todayNotice.hidden ? ' booking-today-notice' : ''));
    if (onlyReception) result.hidden = true;
    const a=Number(form.elements.adults.value),c=Number(form.elements.children.value);
    for(const key of ['adults','children']){
      const input=form.elements[key],value=Number(input.value);
      const error=!input.value ? labels.required : !Number.isSafeInteger(value)||value<0||!validCounts(a,c) ? labels.invalidCount : key==='adults'&&a+c<1 ? labels.peopleError : '';
      fieldError(key,error,reveal===true);
    }
    for (const field of ['surname', 'givenName', 'room']) {
      const input = form.elements[field];
      fieldError(field,input.required&&!input.value.trim()?labels.required:input.value.length>input.maxLength?labels.tooLong:'',reveal===true);
    }
    updateText(schedule,labels[option.value+'Schedule']);
    updateText(document.getElementById('booking-selected-visit'),labels.chosenVisit+': '+labels[option.value+'Short']+' · '+(option.value==='full'?'09:30':'11:30'));
    updateText(document.querySelector('label[for="booking-adults"]'),option.value === 'full' ? labels.fullAdults : labels.adults);
    updateText(document.querySelector('label[for="booking-children"]'),option.value === 'full' ? labels.fullChildren : labels.children);
    if(!picker.hidden && calendarState!==calendarSignature(now))renderCalendar(grid.contains(document.activeElement)?document.activeElement.dataset.date:null);
  };
  const choose = value => {
    if (!hasOption(value)) return;
    option.value = value;
    invalidateReview();
    validate();
  };
  const requested = new URLSearchParams(location.search).get('modalidad');
  if (hasOption(requested)) option.value=requested;
  if (!date.value) date.value=suggestedDate(option.value,new Date(),availability);
  choose(option.value);
  for (const link of document.querySelectorAll('[data-option]')) {
    link.addEventListener('click', () => {
      choose(link.dataset.option);
    });
  }
  document.getElementById('booking-direct').addEventListener('toggle', event => {
    if (!event.currentTarget.open) return;
    validate();
  });
  // Se valida en submit para incluir también fechas cuyo día no tiene visita.
  form.noValidate = true;
  for (const event of ['input', 'change']) form.addEventListener(event, () => {invalidateReview();validate();});
  for(const key of ['surname','givenName','room','adults','children'])form.elements[key].addEventListener('blur',()=>{touched.add(key);validate();});
  option.addEventListener('change', () => choose(option.value));
  window.addEventListener('focus', validate);
  // Actualizar el aviso y ocultar los datos aunque la página siga abierta al cerrar.
  window.setInterval(() => {
    if (document.visibilityState === 'visible') {
      validate();
    }
  }, 15000);
  for(const button of proposalButtons)button.addEventListener('click',() => {
    const requestedDate=button.dataset.date;
    validate();
    const proposal=proposedDates.find(item=>item.kind===button.dataset.dateAlternative && item.date===requestedDate);
    if (!proposal) return;
    date.value=proposal.date;
    invalidateReview();
    validate();
    closeCalendar();
    date.focus();
  });
  function closeCalendar() {picker.hidden=true;pickerToggle.setAttribute('aria-expanded','false');}
  function positionCalendar() {
    if(picker.hidden)return;
    const compact=window.matchMedia('(max-width:700px),(max-height:500px) and (pointer:coarse)').matches;
    for(const property of ['top','left','right','bottom','width','max-height'])picker.style.removeProperty(property);
    if(compact)return;
    const rect=dateField.getBoundingClientRect(),vw=document.documentElement.clientWidth,vh=window.innerHeight;
    const width=Math.min(23*parseFloat(getComputedStyle(document.documentElement).fontSize),vw-32);
    picker.style.width=width+'px';picker.style.maxHeight=Math.max(100,vh-32)+'px';
    const height=picker.getBoundingClientRect().height;
    picker.style.left=Math.max(16,Math.min(rect.right-width,vw-width-16))+'px';
    picker.style.right='auto';picker.style.bottom='auto';
    const below=rect.bottom+8,above=rect.top-height-8;
    picker.style.top=Math.max(16,Math.min(below+height<=vh-16?below:above>=16?above:16,vh-height-16))+'px';
  }
  function renderCalendar(focusDate=null) {
    const now=new Date();
    if (!month) month=new Date(`${canaryToday(now).slice(0,7)}-01T12:00:00Z`);
    monthTitle.textContent=new Intl.DateTimeFormat(labels.lang,{month:'long',year:'numeric',timeZone:'UTC'}).format(month);
    grid.replaceChildren();
    const headings=document.createElement('div');headings.className='calendar-row';headings.setAttribute('role','row');
    for(let i=0;i<7;i++) {const el=document.createElement('span');el.setAttribute('role','columnheader');el.textContent=new Intl.DateTimeFormat(labels.lang,{weekday:'short',timeZone:'UTC'}).format(new Date(Date.UTC(2026,10,16+i,12)));headings.append(el);}
    grid.append(headings);
    const cursor=new Date(month);cursor.setUTCDate(cursor.getUTCDate()-(cursor.getUTCDay()+6)%7);
    for(let week=0;week<6;week++) {
      const row=document.createElement('div');row.className='calendar-row';row.setAttribute('role','row');
      for(let day=0;day<7;day++) {
        const value=cursor.getUTCFullYear()<=9999 ? cursor.toISOString().slice(0,10) : '';const cell=document.createElement('button');cell.type='button';cell.dataset.date=value;cell.setAttribute('role','gridcell');cell.textContent=cursor.getUTCDate();
        const allowed=cursor.getUTCMonth()===month.getUTCMonth()&&selectableDate(option.value,value,now,availability);
        cell.disabled=!allowed;cell.setAttribute('aria-selected',String(value===date.value));cell.setAttribute('aria-label',value?formatDate(value):labels.invalidDate);
        if(value===canaryToday(now))cell.setAttribute('aria-current','date');
        if(cursor.getUTCMonth()!==month.getUTCMonth())cell.className='calendar-outside';
        cell.addEventListener('click',()=>{date.value=value;invalidateReview();validate();closeCalendar();pickerToggle.focus();});
        row.append(cell);cursor.setUTCDate(cursor.getUTCDate()+1);
      }
      grid.append(row);
    }
    document.getElementById('calendar-prev').disabled=month.toISOString().slice(0,7)<=canaryToday(now).slice(0,7);
    document.getElementById('calendar-next').disabled=month.getUTCFullYear()>=9999&&month.getUTCMonth()===11;
    for(const button of grid.querySelectorAll('button'))button.tabIndex=-1;
    const active=(focusDate && grid.querySelector(`[data-date="${focusDate}"]:not(:disabled)`))||grid.querySelector('[aria-selected="true"]:not(:disabled)')||grid.querySelector('button:not(:disabled)');
    if(active)active.tabIndex=0;
    calendarState=calendarSignature(now);
    positionCalendar();
    if(focusDate)(active||document.getElementById('calendar-next')).focus();
  }
  pickerToggle.addEventListener('click',()=>{
    if(!picker.hidden){closeCalendar();return;}
    const value=parseISODate(date.value)&&date.value>=canaryToday() ? date.value : canaryToday();
    month=new Date(`${value.slice(0,7)}-01T12:00:00Z`);
    if(Number.isNaN(month.valueOf()))month=null;
    picker.hidden=false;pickerToggle.setAttribute('aria-expanded','true');renderCalendar();
    (grid.querySelector('[aria-selected="true"]:not(:disabled)')||grid.querySelector('button:not(:disabled)')||document.getElementById('calendar-next')).focus();
  });
  for(const [id,delta] of [['calendar-prev',-1],['calendar-next',1]])document.getElementById(id).addEventListener('click',()=>{month.setUTCMonth(month.getUTCMonth()+delta);renderCalendar();});
  picker.addEventListener('keydown',event=>{
    if(event.key==='Escape'){event.preventDefault();closeCalendar();pickerToggle.focus();return;}
    const delta={ArrowLeft:-1,ArrowRight:1,ArrowUp:-7,ArrowDown:7}[event.key];
    if(!delta||!event.target.dataset.date)return;
    event.preventDefault();const target=new Date(`${event.target.dataset.date}T12:00:00Z`);const now=new Date();
    for(let i=0;i<370;i++){target.setUTCDate(target.getUTCDate()+delta);const value=target.toISOString().slice(0,10);if(value<canaryToday(now))break;if(selectableDate(option.value,value,now,availability)){month=new Date(`${value.slice(0,7)}-01T12:00:00Z`);renderCalendar(value);break;}}
  });
  document.addEventListener('click',event=>{if(!dateField.contains(event.target)&&!picker.contains(event.target))closeCalendar();});
  document.addEventListener('focusin',event=>{if(!dateField.contains(event.target)&&!picker.contains(event.target))closeCalendar();});
  window.addEventListener('resize',positionCalendar);
  window.addEventListener('scroll',positionCalendar,{passive:true});
  // Una solicitud preparada antes del cierre también debe revisarse al continuar.
  for (const button of sendButtons) button.addEventListener('click', () => {
    if(openingApp)return;
    validate(true);
    if (details.disabled || !form.reportValidity() || !consent.checked || !preparedData) {
      result.hidden = true;
      return;
    }
    if(!sameBooking(preparedData,collectBooking())){prepareRequest(collectBooking());updateText(copyStatus,labels.reviewChanged);return;}
    const url = destination(button.dataset.sendChannel, preparedData, labels, preparedText);
    if (url) {
      openingApp=true;for(const action of sendButtons){action.disabled=true;action.setAttribute('aria-busy','true');}
      updateText(copyStatus,labels.externalHelp);
      try{window.location.assign(url);}catch{updateText(copyStatus,labels.externalHelp);}
      window.setTimeout(()=>{openingApp=false;for(const action of sendButtons){action.removeAttribute('aria-busy');action.disabled=!consent.checked||!preparedData||result.hidden;}},1500);
    }
  });
  consent.addEventListener('change', () => {
    for (const button of sendButtons) button.disabled = !consent.checked||openingApp;
    copyButton.disabled=!consent.checked;
  });
  document.getElementById('booking-edit').addEventListener('click',()=>{
    invalidateReview();
    closeCalendar();
    option.focus();
    form.scrollIntoView({block:'start',behavior:'auto'});
  });
  copyButton.addEventListener('click',async()=>{
    validate(true);
    if(!preparedText||!consent.checked||details.disabled||!form.reportValidity())return;
    if(!sameBooking(preparedData,collectBooking())){prepareRequest(collectBooking());updateText(copyStatus,labels.reviewChanged);return;}
    try{if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');await navigator.clipboard.writeText(preparedText);updateText(copyStatus,labels.copied);}
    catch{const range=document.createRange();range.selectNodeContents(document.getElementById('booking-summary'));const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);updateText(copyStatus,labels.copyManually);}
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    validate(true);
    if (details.disabled) return;
    if (!form.reportValidity()) return;
    prepareRequest(collectBooking());
  });
  function prepareRequest(data) {
    const text = message(data, labels);
    document.getElementById('booking-summary').textContent = text;
    document.getElementById('booking-summary').lang='en';
    document.getElementById('booking-consent-label').textContent = chargeConsent(data, labels);
    consent.checked = false;
    copyButton.disabled=true;
    for (const button of sendButtons) button.disabled = true;
    preparedData = data;
    preparedText = text;
    updateText(copyStatus,'');
    result.hidden = false;
    result.focus();
  }
  validate();
  document.getElementById('booking-submit').disabled = false;
  document.getElementById('booking-support').hidden=true;
}

if(typeof document!=='undefined'){
  try{initializeBooking();}catch(error){console.error('Booking initialization unavailable',error);}
}
if (typeof module !== "undefined") module.exports = {parseISODate,validCounts,canaryToday, availableDate, nextAvailableDate, receptionOnly, selectableDate, suggestedDate, dateProblem, nextSelectableDate, dateAlternatives, fullTotals, totals, message, chargeConsent, destination};
