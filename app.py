from flask import Flask, jsonify, request, Response
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

app = Flask(__name__)
DATA_FILE = Path(__file__).with_name("notes_data.json")

HTML_PAGE = """
<!doctype html>
<html lang="tr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Advanced Note Studio</title>
  <style>
    :root {
      --bg: #0f172a;
      --bg-soft: #111827;
      --panel: rgba(15, 23, 42, 0.88);
      --panel-strong: #1f2937;
      --panel-alt: #0b1220;
      --text: #e5eefb;
      --muted: #94a3b8;
      --border: rgba(148, 163, 184, 0.2);
      --primary: #7c3aed;
      --primary-soft: rgba(124, 58, 237, 0.15);
      --success: #22c55e;
      --warning: #f59e0b;
      --danger: #ef4444;
      --shadow: 0 18px 50px rgba(2, 6, 23, 0.5);
    }

    body.light {
      --bg: #eef4ff;
      --bg-soft: #edf2ff;
      --panel: rgba(255,255,255,0.78);
      --panel-strong: #ffffff;
      --panel-alt: #f8fbff;
      --text: #162033;
      --muted: #5e6f8b;
      --border: rgba(15, 23, 42, 0.08);
      --primary: #6d28d9;
      --primary-soft: rgba(109, 40, 217, 0.12);
      --success: #16a34a;
      --warning: #d97706;
      --danger: #dc2626;
      --shadow: 0 15px 40px rgba(15, 23, 42, 0.14);
    }

    * { box-sizing: border-box; }
    html, body {
      margin: 0;
      font-family: Inter, "Segoe UI", Arial, sans-serif;
      background:
        radial-gradient(circle at top left, rgba(124,58,237,0.4), transparent 35%),
        radial-gradient(circle at bottom right, rgba(59,130,246,0.3), transparent 25%),
        var(--bg);
      color: var(--text);
      min-height: 100vh;
    }
    body {
      padding: 22px;
      transition: background 0.25s ease, color 0.25s ease;
    }
    .app-shell { max-width: 1400px; margin: 0 auto; }
    .topbar {
      display: flex; justify-content: space-between; align-items: center; gap: 16px;
      background: var(--panel); backdrop-filter: blur(18px); border: 1px solid var(--border);
      border-radius: 22px; padding: 18px 20px; box-shadow: var(--shadow);
      position: sticky; top: 10px; z-index: 50;
    }
    .brand {
      display: flex; align-items: center; gap: 12px; font-weight: 800;
      font-size: clamp(1.1rem, 1.8vw, 2rem); letter-spacing: -0.04em;
    }
    .brand-badge {
      width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center;
      background: linear-gradient(135deg, var(--primary), #3b82f6); color: white;
      box-shadow: 0 10px 22px rgba(124, 58, 237, 0.4); font-size: 1.2rem;
    }
    .toolbar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
    .search-wrap { position: relative; min-width: min(100%, 320px); flex: 1; }
    .search-wrap input {
      width: 100%; background: var(--panel-alt); color: var(--text); border: 1px solid var(--border);
      border-radius: 14px; height: 46px; padding: 0 16px 0 44px; font-size: 1rem; outline: none;
    }
    .search-icon {
      position: absolute; left: 14px; top: 50%; transform: translateY(-50%); opacity: 0.8; font-size: 1.05rem;
    }
    .primary-btn, .ghost-btn, .action-btn, .mini-btn {
      appearance: none; border: 1px solid var(--border); border-radius: 12px; cursor: pointer;
      transition: transform 0.2s ease, opacity 0.2s ease, background 0.2s ease; font-weight: 700;
    }
    .primary-btn:hover, .ghost-btn:hover, .action-btn:hover, .mini-btn:hover { transform: translateY(-1px); }
    .primary-btn {
      background: linear-gradient(135deg, var(--primary), #3b82f6); color: white; border: none;
      padding: 0 18px; height: 46px; min-width: 120px; box-shadow: 0 12px 24px rgba(124, 58, 237, 0.25);
    }
    .ghost-btn {
      background: transparent; color: var(--text); padding: 0 16px; height: 40px;
    }
    .action-btn {
      background: var(--panel-alt); color: var(--text); padding: 0 16px; height: 40px;
    }
    .mini-btn {
      background: transparent; color: var(--text); width: 34px; height: 34px; display: grid; place-items: center; font-size: 1rem;
    }
    .layout {
      display: grid; grid-template-columns: 320px minmax(0, 1fr); gap: 22px; margin-top: 22px;
    }
    .sidebar, .content-panel {
      background: var(--panel); border: 1px solid var(--border); border-radius: 24px; box-shadow: var(--shadow);
      backdrop-filter: blur(14px);
    }
    .sidebar { padding: 20px; }
    .panel-section { margin-top: 18px; }
    .section-title {
      display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;
      color: var(--muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.09em; font-weight: 700;
    }
    .stat-boxes { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 12px; }
    .stat-box {
      background: var(--panel-alt); border: 1px solid var(--border); border-radius: 16px; padding: 14px;
    }
    .stat-label {
      color: var(--muted); font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;
    }
    .stat-value { font-weight: 800; font-size: 1.6rem; letter-spacing: -0.04em; }
    .category-list { display: flex; flex-direction: column; gap: 10px; }
    .category-btn {
      width: 100%; text-align: left; background: var(--panel-alt); border: 1px solid var(--border); color: var(--text);
      padding: 12px 14px; border-radius: 12px; cursor: pointer; transition: all 0.2s ease; font-weight: 700;
    }
    .category-btn.active { background: var(--primary-soft); border-color: rgba(124,58,237,0.4); }
    .content-panel { padding: 20px; min-height: 700px; }
    .content-header {
      display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 18px;
    }
    .content-header h2 { margin: 0; font-size: clamp(1.3rem,2.2vw,2rem); letter-spacing: -0.04em; }
    .sort-controls { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
    select {
      background: var(--panel-alt); color: var(--text); border: 1px solid var(--border); border-radius: 12px;
      padding: 10px 14px; height: 40px; font-size: 0.95rem; outline: none;
    }
    .notes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 18px; }
    .note-card {
      position: relative; background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.00));
      border: 1px solid var(--border); border-radius: 18px; padding: 16px; min-height: 240px; display: flex; flex-direction: column; gap: 12px;
      transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease; overflow: hidden;
    }
    .note-card:hover { transform: translateY(-2px); border-color: rgba(124,58,237,0.45); box-shadow: 0 12px 24px rgba(124,58,237,0.08); }
    .note-card.pinned { border-color: rgba(245,158,11,0.55); }
    .note-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
    .note-title { font-weight: 800; font-size: 1.1rem; letter-spacing: -0.02em; line-height: 1.3; margin: 0; overflow-wrap: anywhere; }
    .note-status { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
    .status-dot {
      width: 8px; height: 8px; border-radius: 50%; background: var(--success); box-shadow: 0 0 12px var(--success);
    }
    .note-category {
      display: inline-flex; align-items: center; padding: 6px 10px; border-radius: 999px; background: var(--primary-soft);
      color: var(--text); font-size: 0.72rem; font-weight: 700; width: max-content; border: 1px solid rgba(124,58,237,0.15);
    }
    .note-content {
      color: var(--text); font-size: 0.96rem; line-height: 1.6; flex: 1; white-space: pre-wrap; overflow-wrap: anywhere; opacity: 0.96;
    }
    .note-meta {
      display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-top: auto; color: var(--muted); font-size: 0.78rem;
    }
    .note-actions { display: flex; align-items: center; gap: 8px; justify-content: flex-end; }
    .mini-btn.active { background: rgba(245, 158, 11, 0.12); border-color: rgba(245,158,11,0.35); color: #fbbf24; }
    .mini-btn.favorite.active { background: rgba(251,191,36,0.12); border-color: rgba(251,191,36,0.35); }
    .empty-state {
      display: grid; place-items: center; min-height: 300px; background: var(--panel-alt); border: 1px dashed var(--border);
      border-radius: 20px; text-align: center; color: var(--muted); padding: 24px;
    }
    .modal-backdrop {
      display: none; position: fixed; inset: 0; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(8px); z-index: 100;
      align-items: center; justify-content: center; padding: 20px;
    }
    .modal-backdrop.open { display: flex; }
    .modal {
      width: min(100%, 720px); background: var(--panel-strong); border: 1px solid var(--border); border-radius: 24px;
      box-shadow: var(--shadow); overflow: hidden;
    }
    .modal-header {
      display: flex; align-items: center; justify-content: space-between; padding: 18px 20px; border-bottom: 1px solid var(--border);
      background: rgba(124,58,237,0.08);
    }
    .modal-header h3 { margin: 0; font-size: 1.25rem; }
    .close-btn {
      background: transparent; border: 1px solid var(--border); color: var(--text); width: 40px; height: 40px; border-radius: 12px; cursor: pointer; font-size: 1.2rem;
    }
    .modal-body { padding: 20px; display: grid; gap: 16px; }
    .field { display: grid; gap: 8px; }
    .field label {
      color: var(--muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700;
    }
    .field input, .field textarea {
      background: var(--panel-alt); border: 1px solid var(--border); border-radius: 14px; color: var(--text); padding: 12px 14px;
      font-size: 1rem; outline: none; resize: vertical; min-height: 46px;
    }
    .field textarea { min-height: 200px; }
    .modal-footer {
      display: flex; justify-content: flex-end; align-items: center; gap: 10px; padding: 0 20px 20px;
    }
    .small { font-size: 0.8rem; color: var(--muted); }
    @media (max-width: 980px) { .layout { grid-template-columns: 1fr; } }
    @media (max-width: 560px) {
      body { padding: 14px; }
      .topbar { padding: 14px 16px; }
      .toolbar { width: 100%; }
      .search-wrap { min-width: 100%; }
      .stat-boxes { grid-template-columns: 1fr 1fr; }
      .notes-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <div class="brand-badge">✒️</div>
        <div>Advanced Note Studio</div>
      </div>
      <div class="toolbar">
        <div class="search-wrap">
          <span class="search-icon">⌕</span>
          <input id="searchInput" type="search" placeholder="Not ara..." aria-label="Not ara" />
        </div>
        <button class="ghost-btn" id="themeToggle" aria-label="Tema değiştir">🌙</button>
        <button class="primary-btn" id="openEditor">Yeni Not</button>
      </div>
    </header>

    <div class="layout">
      <aside class="sidebar">
        <div class="panel-section">
          <div class="section-title"><span>İstatistik</span></div>
          <div class="stat-boxes">
            <div class="stat-box"><div class="stat-label">Toplam</div><div class="stat-value" id="statTotal">0</div></div>
            <div class="stat-box"><div class="stat-label">Sabit</div><div class="stat-value" id="statPinned">0</div></div>
            <div class="stat-box"><div class="stat-label">Favoriler</div><div class="stat-value" id="statFavorite">0</div></div>
            <div class="stat-box"><div class="stat-label">Kategoriler</div><div class="stat-value" id="statCategories">0</div></div>
          </div>
        </div>

        <div class="panel-section">
          <div class="section-title"><span>Kategoriler</span></div>
          <div class="category-list" id="categoryList"></div>
        </div>
      </aside>

      <main class="content-panel">
        <div class="content-header">
          <h2 id="contentTitle">Tüm Notlar</h2>
          <div class="sort-controls">
            <label class="small" for="sortSelect">Sırala:</label>
            <select id="sortSelect">
              <option value="updated-desc">En yeni</option>
              <option value="created-desc">Eklenme</option>
              <option value="title-asc">Başlık A-Z</option>
              <option value="favorite-first">Favoriler öncelikli</option>
            </select>
          </div>
        </div>

        <div id="notesGrid" class="notes-grid"></div>
      </main>
    </div>
  </div>

  <div class="modal-backdrop" id="editorModal" aria-hidden="true">
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
      <div class="modal-header">
        <h3 id="modalTitle">Not Düzenle</h3>
        <button class="close-btn" id="closeModal" aria-label="Kapat">✕</button>
      </div>
      <div class="modal-body">
        <div class="field">
          <label for="titleInput">Başlık</label>
          <input id="titleInput" type="text" placeholder="Not başlığı" maxlength="120" />
        </div>
        <div class="field">
          <label for="categoryInput">Kategori</label>
          <input id="categoryInput" type="text" placeholder="Örn: İş, Kişisel, Fikirler" maxlength="60" />
        </div>
        <div class="field">
          <label for="contentInput">İçerik</label>
          <textarea id="contentInput" placeholder="Notunuzun içeriğini yazın..."></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button class="ghost-btn" id="cancelBtn">İptal</button>
        <button class="primary-btn" id="saveBtn">Kaydet</button>
      </div>
    </div>
  </div>

  <script>
    const state = {
      notes: [],
      selectedCategory: 'all',
      search: '',
      sortBy: 'updated-desc',
      editingId: null,
      theme: localStorage.getItem('note-theme') || 'dark'
    };

    const els = {
      notesGrid: document.getElementById('notesGrid'),
      categoryList: document.getElementById('categoryList'),
      searchInput: document.getElementById('searchInput'),
      sortSelect: document.getElementById('sortSelect'),
      themeToggle: document.getElementById('themeToggle'),
      openEditor: document.getElementById('openEditor'),
      editorModal: document.getElementById('editorModal'),
      titleInput: document.getElementById('titleInput'),
      categoryInput: document.getElementById('categoryInput'),
      contentInput: document.getElementById('contentInput'),
      modalTitle: document.getElementById('modalTitle'),
      saveBtn: document.getElementById('saveBtn'),
      cancelBtn: document.getElementById('cancelBtn'),
      closeModal: document.getElementById('closeModal'),
      contentTitle: document.getElementById('contentTitle'),
      statTotal: document.getElementById('statTotal'),
      statPinned: document.getElementById('statPinned'),
      statFavorite: document.getElementById('statFavorite'),
      statCategories: document.getElementById('statCategories')
    };

    function formatDate(dateString) {
      const d = new Date(dateString);
      return new Intl.DateTimeFormat('tr-TR', {
        day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
      }).format(d);
    }

    function applyTheme() {
      document.body.classList.toggle('light', state.theme === 'light');
      els.themeToggle.textContent = state.theme === 'light' ? '☀️' : '🌙';
      localStorage.setItem('note-theme', state.theme);
    }

    async function fetchNotes() {
      const response = await fetch('/api/notes');
      const data = await response.json();
      state.notes = data.notes || [];
      render();
    }

    function getFilteredNotes() {
      let notes = [...state.notes];
      if (state.selectedCategory !== 'all') {
        notes = notes.filter(note => note.category === state.selectedCategory);
      }
      if (state.search.trim()) {
        const q = state.search.trim().toLowerCase();
        notes = notes.filter(note => {
          return note.title.toLowerCase().includes(q) || note.content.toLowerCase().includes(q) || note.category.toLowerCase().includes(q);
        });
      }
      notes.sort((a, b) => {
        if (state.sortBy === 'title-asc') return a.title.localeCompare(b.title, 'tr');
        if (state.sortBy === 'created-desc') return new Date(b.created_at) - new Date(a.created_at);
        if (state.sortBy === 'favorite-first') return Number(b.favorite) - Number(a.favorite) || new Date(b.updated_at) - new Date(a.updated_at);
        return new Date(b.updated_at) - new Date(a.updated_at);
      });
      return notes;
    }

    function renderStats() {
      const total = state.notes.length;
      const pinned = state.notes.filter(n => n.pinned).length;
      const favorite = state.notes.filter(n => n.favorite).length;
      const categories = new Set(state.notes.map(n => n.category)).size;

      els.statTotal.textContent = total;
      els.statPinned.textContent = pinned;
      els.statFavorite.textContent = favorite;
      els.statCategories.textContent = categories;
    }

    function renderCategories() {
      const categories = ['all', ...new Set(state.notes.map(note => note.category))];
      els.categoryList.innerHTML = categories.map(category => {
        const isActive = state.selectedCategory === category;
        const label = category === 'all' ? 'Tümü' : category;
        return `<button class="category-btn ${isActive ? 'active' : ''}" data-category="${category}">${label}</button>`;
      }).join('');

      els.categoryList.querySelectorAll('.category-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          state.selectedCategory = btn.dataset.category;
          render();
        });
      });
    }

    function renderNotes() {
      const filtered = getFilteredNotes();
      els.notesGrid.innerHTML = '';
      if (!filtered.length) {
        els.notesGrid.innerHTML = '<div class="empty-state"><div><h3>Not bulunamadı</h3><p>Arama kriterine uygun kayıt yok veya hiç not eklenmemiş.</p></div></div>';
        return;
      }

      filtered.forEach(note => {
        const card = document.createElement('article');
        card.className = `note-card ${note.pinned ? 'pinned' : ''}`;
        card.innerHTML = `
          <div class="note-header">
            <h3 class="note-title">${escapeHtml(note.title)}</h3>
            <div class="note-status"><span class="status-dot" title="Aktif"></span></div>
          </div>
          <span class="note-category">${escapeHtml(note.category || 'Genel')}</span>
          <div class="note-content">${escapeHtml(note.content)}</div>
          <div class="note-meta">
            <span>${formatDate(note.updated_at)}</span>
            <div class="note-actions">
              <button class="mini-btn favorite ${note.favorite ? 'active' : ''}" data-action="favorite" data-id="${note.id}" title="Favori">★</button>
              <button class="mini-btn ${note.pinned ? 'active' : ''}" data-action="pin" data-id="${note.id}" title="Sabitle">📌</button>
              <button class="mini-btn" data-action="edit" data-id="${note.id}" title="Düzenle">✎</button>
              <button class="mini-btn" data-action="delete" data-id="${note.id}" title="Sil">🗑</button>
            </div>
          </div>
        `;
        els.notesGrid.appendChild(card);
      });

      els.notesGrid.querySelectorAll('[data-action]').forEach(button => {
        button.addEventListener('click', async () => {
          const id = button.dataset.id;
          const action = button.dataset.action;
          if (action === 'delete') { await deleteNote(id); return; }
          if (action === 'edit') { const note = state.notes.find(item => item.id === id); openEditor(note); return; }
          if (action === 'pin' || action === 'favorite') { await toggleNoteFlag(id, action); }
        });
      });
    }

    function render() {
      renderStats();
      renderCategories();
      els.contentTitle.textContent = state.selectedCategory === 'all' ? 'Tüm Notlar' : `${state.selectedCategory} Kategorisi`;
      renderNotes();
    }

    function openEditor(note = null) {
      state.editingId = note ? note.id : null;
      els.modalTitle.textContent = note ? 'Notu Düzenle' : 'Yeni Not';
      els.titleInput.value = note ? note.title : '';
      els.categoryInput.value = note ? note.category : '';
      els.contentInput.value = note ? note.content : '';
      els.editorModal.classList.add('open');
      setTimeout(() => els.titleInput.focus(), 60);
    }

    function closeEditor() {
      els.editorModal.classList.remove('open');
      state.editingId = null;
      els.titleInput.value = '';
      els.categoryInput.value = '';
      els.contentInput.value = '';
    }

    async function saveNote() {
      const title = els.titleInput.value.trim() || 'Başlıksız Not';
      const category = els.categoryInput.value.trim() || 'Genel';
      const content = els.contentInput.value.trim();
      if (!content) {
        alert('Not içeriği boş olamaz.');
        return;
      }

      const payload = { title, category, content };
      if (state.editingId) {
        await fetch(`/api/notes/${state.editingId}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      } else {
        await fetch('/api/notes', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      }
      closeEditor();
      await fetchNotes();
    }

    async function deleteNote(id) {
      const ok = confirm('Bu notu silmek istediğinize emin misiniz?');
      if (!ok) return;
      await fetch(`/api/notes/${id}`, { method: 'DELETE' });
      await fetchNotes();
    }

    async function toggleNoteFlag(id, action) {
      const note = state.notes.find(item => item.id === id);
      if (!note) return;
      const field = action === 'pin' ? 'pinned' : 'favorite';
      const update = { [field]: !note[field] };
      await fetch(`/api/notes/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(update) });
      await fetchNotes();
    }

    function escapeHtml(value) {
      return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    els.searchInput.addEventListener('input', (e) => { state.search = e.target.value; render(); });
    els.sortSelect.addEventListener('change', (e) => { state.sortBy = e.target.value; render(); });
    els.themeToggle.addEventListener('click', () => { state.theme = state.theme === 'dark' ? 'light' : 'dark'; applyTheme(); });
    els.openEditor.addEventListener('click', () => openEditor());
    els.cancelBtn.addEventListener('click', closeEditor);
    els.closeModal.addEventListener('click', closeEditor);
    els.editorModal.addEventListener('click', (e) => { if (e.target === els.editorModal) closeEditor(); });
    els.saveBtn.addEventListener('click', saveNote);
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && els.editorModal.classList.contains('open')) closeEditor();
      if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
        event.preventDefault();
        openEditor();
      }
    });

    applyTheme();
    fetchNotes();
  </script>
</body>
</html>
"""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")


def ensure_data_file():
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps({"notes": []}, ensure_ascii=False, indent=2), encoding="utf-8")


def load_notes():
    ensure_data_file()
    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return data.get("notes", [])


def save_notes(notes):
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump({"notes": notes}, file, ensure_ascii=False, indent=2)
        file.write("\n")


@app.get("/")
def index():
    return Response(HTML_PAGE, mimetype="text/html")


@app.get("/api/notes")
def get_notes():
    return jsonify({"notes": load_notes()})


@app.post("/api/notes")
def create_note():
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "Başlıksız Not").strip() or "Başlıksız Not"
    content = (payload.get("content") or "").strip()
    if not content:
        return jsonify({"error": "Not içeriği boş olamaz."}), 400

    category = (payload.get("category") or "Genel").strip() or "Genel"
    now = utc_now_iso()
    note = {
        "id": str(uuid.uuid4()),
        "title": title,
        "content": content,
        "category": category,
        "favorite": bool(payload.get("favorite", False)),
        "pinned": bool(payload.get("pinned", False)),
        "created_at": now,
        "updated_at": now,
    }
    notes = load_notes()
    notes.insert(0, note)
    save_notes(notes)
    return jsonify({"note": note}), 201


@app.put("/api/notes/<note_id>")
def update_note(note_id):
    payload = request.get_json(silent=True) or {}
    notes = load_notes()
    for note in notes:
        if note["id"] == note_id:
            if "title" in payload:
                note["title"] = (payload.get("title") or note["title"]).strip() or note["title"]
            if "content" in payload:
                content_value = (payload.get("content") or "").strip()
                if not content_value:
                    return jsonify({"error": "Not içeriği boş olamaz."}), 400
                note["content"] = content_value
            if "category" in payload:
                note["category"] = (payload.get("category") or note["category"]).strip() or note["category"]
            if "favorite" in payload:
                note["favorite"] = bool(payload.get("favorite"))
            if "pinned" in payload:
                note["pinned"] = bool(payload.get("pinned"))
            note["updated_at"] = utc_now_iso()
            save_notes(notes)
            return jsonify({"note": note})
    return jsonify({"error": "Not bulunamadı."}), 404


@app.delete("/api/notes/<note_id>")
def delete_note(note_id):
    notes = load_notes()
    updated = [note for note in notes if note["id"] != note_id]
    if len(updated) == len(notes):
        return jsonify({"error": "Not bulunamadı."}), 404
    save_notes(updated)
    return jsonify({"success": True})


@app.get("/health")
def health_check():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
