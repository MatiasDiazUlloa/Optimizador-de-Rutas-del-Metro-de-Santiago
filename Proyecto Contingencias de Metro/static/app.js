async function api(url, method = 'GET', body = null) {
    const options = { method };
    if (body) {
        options.headers = { 'Content-Type': 'application/json' };
        options.body = JSON.stringify(body);
    }
    const res = await fetch(url, options);
    return res.json();
}

async function loadEstaciones() {
    try {
        const data = await api('/api/estaciones');
        const stations = data.estaciones;
        const selects = ['routeOrigin', 'routeDest', 'stationName', 'tramoE1', 'tramoE2'];
        selects.forEach(id => {
            const sel = document.getElementById(id);
            sel.innerHTML = '<option value="">Seleccionar...</option>';
            stations.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s;
                opt.textContent = s;
                sel.appendChild(opt);
            });
        });
    } catch (err) {
        toast('Error cargando estaciones');
    }
}

async function updateState() {
    try {
        const state = await api('/api/state');
        document.getElementById('totalStations').textContent = state.total_estaciones;
        const closedEl = document.getElementById('closedStations');
        const tramosEl = document.getElementById('blockedTramos');
        closedEl.textContent = state.fallas_estaciones.length > 0
            ? state.fallas_estaciones.join(', ') : 'Ninguna';
        tramosEl.textContent = state.fallas_tramos.length > 0
            ? state.fallas_tramos.length + ' tramo(s)' : 'Ninguno';
    } catch (e) {}
}

function toast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3000);
}

function showResult(elId, text) {
    const el = document.getElementById(elId);
    const cls = text.includes('Error') ? 'error' : text.includes('Diagnostico') ? 'info' : 'success';
    el.innerHTML = `<div class="result-box ${cls}">${escHtml(text)}</div>`;
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function escHtml(t) {
    const d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
}

// Tabs principales
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById('panel-' + tab.dataset.tab).classList.add('active');
    });
});

// Sub-tabs contingencia
document.querySelectorAll('.cont-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.cont-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.cont-panel').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById('cont-' + tab.dataset.cont).classList.add('active');
    });
});

// Calcular ruta
document.getElementById('btnCalculate').addEventListener('click', async () => {
    const origen = document.getElementById('routeOrigin').value;
    const destino = document.getElementById('routeDest').value;
    const criterio = document.querySelector('input[name="criterio"]:checked').value;
    if (!origen || !destino) { toast('Selecciona ambas estaciones'); return; }

    const btn = document.getElementById('btnCalculate');
    btn.disabled = true;
    btn.textContent = 'Calculando...';
    try {
        const data = await api('/api/route', 'POST', { origen, destino, criterio });
        showResult('routeResult', data.resultado);
    } catch (e) { toast('Error en la conexión'); }
    finally {
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-text">Calcular Ruta</span><span class="btn-arrow">→</span>';
    }
});

// Cerrar estación
document.getElementById('btnCloseStation').addEventListener('click', async () => {
    const nombre = document.getElementById('stationName').value;
    if (!nombre) { toast('Selecciona una estación'); return; }
    try {
        const data = await api('/api/contingency/station', 'POST', { nombre });
        if (data.success) {
            toast(data.mensaje);
            await updateState();
            showResult('contingencyResult', data.mensaje);
            await api('/api/diagnostico').then(d => showResult('statusResult', d.resultado));
        } else {
            toast(data.mensaje);
        }
    } catch (e) { toast('Error en la conexión'); }
});

// Cerrar tramo
document.getElementById('btnCloseTramo').addEventListener('click', async () => {
    const e1 = document.getElementById('tramoE1').value;
    const e2 = document.getElementById('tramoE2').value;
    if (!e1 || !e2) { toast('Selecciona ambas estaciones'); return; }

    const btn = document.getElementById('btnCloseTramo');
    btn.disabled = true;
    btn.textContent = 'Cerrando...';
    try {
        const data = await api('/api/contingency/tramo', 'POST', { e1, e2 });
        if (data.success) {
            toast(data.mensaje);
            await updateState();
            showResult('contingencyResult', data.mensaje + '\nTrayecto: ' + data.trayecto);
            await api('/api/diagnostico').then(d => showResult('statusResult', d.resultado));
        } else {
            toast(data.mensaje);
        }
    } catch (e) { toast('Error en la conexión'); }
    finally { btn.disabled = false; btn.textContent = 'Cerrar Tramo'; }
});

// Diagnóstico
document.getElementById('btnCheckStatus').addEventListener('click', async () => {
    try {
        const data = await api('/api/diagnostico');
        showResult('statusResult', data.resultado);
    } catch (e) { toast('Error en la conexión'); }
});

// Reset
document.getElementById('btnReset').addEventListener('click', async () => {
    const btn = document.getElementById('btnReset');
    btn.disabled = true;
    btn.textContent = 'Reiniciando...';
    try {
        await api('/api/reset', 'POST');
        toast('Sistema reiniciado');
        await updateState();
        ['routeResult', 'contingencyResult', 'statusResult'].forEach(id =>
            document.getElementById(id).innerHTML = '');
    } catch (e) { toast('Error al reiniciar'); }
    btn.disabled = false;
    btn.textContent = '🔄 Reiniciar';
});

loadEstaciones();
updateState();