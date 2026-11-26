from pathlib import Path
r=Path(__file__).resolve().parents[3];p=r/'src/main/webapp/WEB-INF/views/librarian/dashboard.jsp';s=p.read_text()
s=s.replace('<aside class="sidebar">','<aside class="sidebar" aria-label="Library navigation">').replace('<aside class="dashboard-right">','<aside class="dashboard-right" aria-label="Library tools">')
s=s.replace('data-theme-toggle aria-label="Toggle theme"','data-theme-toggle role="switch" aria-checked="false" aria-label="Toggle theme"')
s=s.replace('<h3 class="panel-card__title">','<h2 class="panel-card__title">').replace('</h3>','</h2>')
s=s.replace('</head>','''<style>
:root { --text-muted: #526174; }
.dash-stat-card__label { color: #526174 !important; }
.sidebar__brand-sub, .sidebar__profile-id, .sidebar__quote, .sidebar__quote span { color: #dbe6f5 !important; opacity: 1 !important; }
[data-theme="dark"] { --text-muted: #b8c7db; }
[data-theme="dark"] .dash-stat-card__label { color: #b8c7db !important; }
</style>
</head>''')
p.write_text(s)
