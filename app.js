const API = {
  name(){ return localStorage.getItem('typerName') || ''; },
  async submit(game, wpm, accuracy, text){
    const n = document.getElementById('playerName');
    const name = n ? n.value.trim() : this.name();
    if (name) localStorage.setItem('typerName', name);
    try {
      const r = await fetch('/api/scores/' + game, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, wpm, accuracy, text})
      });
      return r.ok;
    } catch { return false; }
  },
  async board(game, el){
    try {
      const rows = await (await fetch('/api/scores/' + game)).json();
      el.innerHTML = rows.length ? '<b>Top scores</b><br>' + rows.map((r,i)=>`${i+1}. ${r.name.replace(/</g,'&lt;')} — ${r.wpm} WPM, ${r.accuracy}%`).join('<br>') : 'No scores yet.';
    } catch { el.textContent = 'Leaderboard needs the Flask server running.'; }
  }
};