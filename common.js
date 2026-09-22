const WORDS="the be to of and a in that have it for not on with he as you do at this but his by from they we say her she or an will my one all would there their what so up out if about who get which go me when make can like time no just him know take people into year your good some could them see other than then now look only come its over think also back after use two how our work first well way even new want because any these give day most us love code data type test game fast key line word run file page site web app user list task build net tool log bit byte loop true false null var let class push pull merge ship make fix test speed logic input output stack queue graph tree array table query index cloud batch patch flag mode event state route theme timer clock light quick sharp brave smart clean solid cool exam deadline lecture campus library semester project wifi laptop coffee professor assignment groupchat quiz hostel gpa lecturer seminar tutorial credits result plagiarism scholarship cafeteria password submit upload download server crash allnighter".split(" ");
const $=id=>document.getElementById(id);
const pick=a=>a[Math.floor(Math.random()*a.length)];
function getBest(k){try{return +localStorage.getItem('best_'+k)||0}catch(e){return 0}}
function best(k,v){const o=getBest(k);if(v>o){try{localStorage.setItem('best_'+k,v)}catch(e){}return v}return o}

// ---- lightweight multiplayer room client (used by race + sprint) ----
const ROOM = {
  async create(game, name){
    const r = await fetch('/api/rooms/'+game, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name})});
    if(!r.ok) return null;
    return r.json();
  },
  async join(game, code, name){
    const r = await fetch('/api/rooms/'+game+'/'+code+'/join', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name})});
    if(!r.ok) return {error:(await r.json().catch(()=>({}))).error || 'could not join'};
    return r.json();
  },
  async start(game, code){
    const r = await fetch('/api/rooms/'+game+'/'+code+'/start', {method:'POST'});
    if(!r.ok) return null;
    return r.json();
  },
  async update(game, code, player_id, data){
    const r = await fetch('/api/rooms/'+game+'/'+code+'/update', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({player_id, ...data})});
    if(!r.ok) return null;
    return r.json();
  },
  async state(game, code){
    const r = await fetch('/api/rooms/'+game+'/'+code);
    if(!r.ok) return null;
    return r.json();
  }
};

// brief flash/shake for streak or milestone moments - visual only, no layout shift
function flash(el, cls){
  el.classList.remove(cls); void el.offsetWidth; el.classList.add(cls);
}
