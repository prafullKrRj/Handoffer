const $ = (selector) => document.querySelector(selector);
const state = { agents: [], policy: { threshold_percent: 95, auto_delegate: false } };

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character]));
}

function usage(agent) {
  const five = agent.five_hour || {};
  const weekly = agent.weekly || {};
  return { remaining: Math.max(0, Math.round(Math.min(Number(five.remaining_percent ?? 0), Number(weekly.remaining_percent ?? 0)))), five, weekly };
}

function render() {
  const trigger = Number(state.policy.threshold_percent ?? 95);
  const remainingRequired = 100 - trigger;
  const ready = (agent) => agent.available && usage(agent).remaining > remainingRequired;
  const available = state.agents.filter(ready).length;
  const healthy = state.agents.length ? Math.round((available / state.agents.length) * 100) : 0;
  $('#available-count').textContent = available;
  $('#agent-count').textContent = state.agents.length;
  $('#healthy-percent').textContent = `${healthy}%`;
  $('#auto-delegate-summary').textContent = state.policy.auto_delegate ? 'On' : 'Off';
  $('#agent-total-pill').textContent = `${state.agents.length} agents`;
  $('#threshold').value = trigger;
  $('#threshold-output').value = `${trigger}%`;
  $('#threshold-output').textContent = `${trigger}%`;
  $('#auto-delegate').checked = Boolean(state.policy.auto_delegate);
  $('#agents-list').innerHTML = state.agents.length ? state.agents.map((agent) => {
    const info = usage(agent);
    const status = ready(agent) ? 'Ready' : agent.available ? 'Limit reached' : 'Unavailable';
    const statusClass = ready(agent) ? 'ready' : agent.available ? 'busy' : 'offline';
    const level = info.remaining <= remainingRequired ? 'low' : info.remaining <= remainingRequired + 15 ? 'warn' : '';
    return `<article class="agent-row"><div><div class="agent-name">${escapeHtml(agent.name || agent.id)}</div><div class="agent-kind">${escapeHtml(agent.kind || 'agent')}</div></div><div class="capacity"><div class="capacity-head"><span>Usable capacity</span><span class="capacity-value">${info.remaining}%</span></div><div class="meter"><div class="meter-fill ${level}" style="width:${info.remaining}%"></div></div><div class="agent-kind">5h ${info.five.remaining_percent ?? '—'}% · weekly ${info.weekly.remaining_percent ?? '—'}%</div></div><span class="agent-status ${statusClass}">${status}</span></article>`;
  }).join('') : '<div class="empty-state">No agents connected.</div>';
}

async function request(path, options) {
  const response = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...options });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.status === 204 ? null : response.json();
}

function setConnection(stateName, label) {
  const status = $('#connection-status');
  status.dataset.state = stateName;
  status.querySelector('span:last-child').textContent = label;
}

async function refresh() {
  const button = $('#refresh-button');
  button.classList.add('is-refreshing');
  try {
    const data = await request('/api/refresh', { method: 'POST' });
    state.agents = data.agents || [];
    state.policy = data.policy || state.policy;
    render();
    setConnection('ready', 'Live');
    $('#last-updated').textContent = `Updated ${new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}`;
  } catch (error) {
    setConnection('offline', 'Offline');
    console.error(error);
  } finally {
    button.classList.remove('is-refreshing');
  }
}

$('#threshold').addEventListener('input', (event) => { $('#threshold-output').textContent = `${event.target.value}%`; });
$('#refresh-button').addEventListener('click', refresh);
$('#settings-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const feedback = $('#settings-feedback');
  const payload = { threshold_percent: Number($('#threshold').value), auto_delegate: $('#auto-delegate').checked };
  try {
    state.policy = await request('/api/settings', { method: 'PUT', body: JSON.stringify(payload) });
    render();
    feedback.textContent = 'Settings saved';
  } catch (error) {
    feedback.textContent = 'Could not save settings';
    console.error(error);
  }
});
refresh();
