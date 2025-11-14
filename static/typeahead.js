async function attachTypeahead(inputSelector, hiddenFields){
  const input = document.querySelector(inputSelector);
  if(!input) return;
  const list = document.createElement('div');
  list.className = 'typeahead-list card p-2';
  list.style.position = 'absolute';
  list.style.zIndex = 2000;
  list.style.display = 'none';
  input.parentNode.style.position = 'relative';
  input.parentNode.appendChild(list);

  let timer;
  input.addEventListener('input', (e)=>{
    clearTimeout(timer);
    const q = e.target.value;
    timer = setTimeout(async ()=>{
      if(!q) { list.style.display='none'; return; }
      const res = await fetch('/api/fabrics?q='+encodeURIComponent(q));
      const items = await res.json();
      list.innerHTML = '';
      if(items.length===0){ list.style.display='none'; return; }
      items.forEach(item=>{
        const el = document.createElement('div');
        el.className='typeahead-item p-1';
        el.style.cursor='pointer';
        el.innerText = `${item.fabric_type} (${item.fabric_code}) - ${item.composition}`;
        el.addEventListener('click', ()=>{
          input.value = item.fabric_type;
          // fill hidden fields if present
          if(hiddenFields.fabric_code) document.querySelector(hiddenFields.fabric_code).value = item.fabric_code || '';
          if(hiddenFields.composition) document.querySelector(hiddenFields.composition).value = item.composition || '';
          list.style.display='none';
        });
        list.appendChild(el);
      });
      list.style.display='block';
    }, 250);
  });
  document.addEventListener('click', (e)=>{ if(!input.parentNode.contains(e.target)) list.style.display='none'; });
}

// auto-attach on pages
window.addEventListener('DOMContentLoaded', ()=>{
  attachTypeahead('input[name="fabric_type"]', {fabric_code: 'input[name="fabric_code"]', composition: 'input[name="composition"]'}).catch(()=>{});
});
