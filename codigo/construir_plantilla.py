"""Arma codigo/plantilla_departamento.html a partir de los estilos base y el cuerpo del mapa.
Uso: python codigo/construir_plantilla.py   (luego dep_3_preparar_web.py)"""
from pathlib import Path

C = Path(__file__).resolve().parent
css = (C / '_css_base.txt').read_text()
extra = """
.rankhead{display:flex;justify-content:space-between;align-items:baseline;gap:8px;flex-wrap:wrap}
.rankhead h2{margin:0}
.tabs{display:flex;border:1px solid var(--line);border-radius:6px;overflow:hidden}
.tabs button{font:inherit;font-size:12px;padding:4px 10px;border:0;background:var(--panel);color:var(--fg);cursor:pointer}
.tabs button[aria-pressed="true"]{background:var(--accent-soft);color:var(--accent);font-weight:600}
.tabs button:disabled{color:var(--muted);cursor:not-allowed}
ol.rank{margin-top:8px}
.lbl-p{font-family:var(--f-display);font-weight:700;font-size:13px;letter-spacing:.02em}
#mun{font-weight:600}
.streetbox{display:grid;grid-template-columns:18px 1fr;gap:4px 8px;align-items:start;font-size:12.5px;border:1px solid var(--line);border-radius:8px;padding:8px 10px}
.streetbox .sw{width:18px;height:5px;border-radius:3px;background:var(--sel);margin-top:7px}
.streetbox .linkbtn{grid-column:2;margin:0}

.seg button:last-child:nth-child(3n+2){grid-column:span 2}
/* Botones */
.hbtns{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.btn{font:inherit;font-size:13px;font-weight:600;padding:7px 12px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--fg);cursor:pointer}
.btn:hover{border-color:var(--accent)}
.btn.primary{background:var(--accent);border-color:var(--accent);color:var(--panel)}
.btn:disabled{opacity:.5;cursor:default}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}

/* Chat */
.zchip{left:50%!important;transform:translateX(-50%)}
.chatpill{position:absolute;left:max(12px,env(safe-area-inset-left,0px));bottom:max(22px,env(safe-area-inset-bottom,0px));z-index:820;font:inherit;font-size:13px;font-weight:600;
  background:var(--accent);color:var(--panel);border:0;border-radius:999px;padding:9px 16px;box-shadow:0 4px 16px rgb(0 0 0 / .18);cursor:pointer}
.chat{position:absolute;left:max(12px,env(safe-area-inset-left,0px));bottom:max(12px,env(safe-area-inset-bottom,0px));z-index:850;width:360px;max-height:calc(100% - 96px);
  display:flex;flex-direction:column;background:var(--panel);border:1px solid var(--line);border-radius:10px;box-shadow:0 6px 24px rgb(0 0 0 / .16)}
.chat[hidden]{display:none!important}
.chathead{display:flex;justify-content:space-between;align-items:center;padding:10px 12px;border-bottom:1px solid var(--line);font-family:var(--f-display);font-size:14px}
.chatlog{overflow-y:auto;padding:10px 12px;display:flex;flex-direction:column;gap:8px;min-height:120px;flex:1}
.chatlog p{margin:0 0 6px}
.chatlog ul,.chatlog ol{margin:0 0 6px;padding-left:18px}
.msg{font-size:13px;line-height:1.45;padding:8px 10px;border-radius:10px;max-width:92%}
.msg.user{align-self:flex-end;background:var(--accent-soft);color:var(--fg)}
.msg.bot{align-self:flex-start;background:var(--bg);border:1px solid var(--line)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font:inherit;font-size:12px;text-align:left;padding:5px 9px;border:1px solid var(--line);border-radius:999px;background:var(--panel);color:var(--fg);cursor:pointer}
.chip:hover{border-color:var(--accent);color:var(--accent)}
.chatform{border-top:1px solid var(--line);padding:8px 10px;display:flex;flex-direction:column;gap:6px}
.chatform textarea{font:inherit;font-size:13px;resize:vertical;min-height:40px;padding:7px 8px;border:1px solid var(--line);border-radius:6px;background:var(--panel);color:var(--fg)}
.chatact{display:flex;align-items:center;gap:6px}
.chatact .hint{flex:1;min-width:0}

/* Recorrido guiado */
.tour{position:absolute;top:12px;left:56px;z-index:900;width:min(380px,calc(100% - 68px));background:var(--panel);border:2px solid var(--accent);border-radius:12px;
  box-shadow:0 10px 30px rgb(0 0 0 / .22);padding:12px 14px 14px}
.tour[hidden]{display:none!important}
.tourhead{display:flex;justify-content:space-between;align-items:center}
.tourn{font-family:var(--f-data);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent)}
.tour h3{font-family:var(--f-display);font-size:17px;margin:4px 0 6px;text-wrap:balance}
.tour p{margin:0 0 12px;font-size:13.5px;line-height:1.5}
.tourbtns{display:flex;justify-content:flex-end;gap:8px}
.tour-focus{outline:3px solid var(--accent)!important;outline-offset:3px;border-radius:8px;animation:tf 1.4s ease-in-out 2}
@keyframes tf{50%{outline-offset:7px}}

@media (max-width:860px){
  .chatpill{display:none}
  #map{order:0} .chat{order:1;position:static;width:auto;max-height:70vh;border-radius:0;border-width:1px 0 0;box-shadow:none} .ficha{order:2}
  .tour{position:fixed;top:auto;left:0;right:0;bottom:0;width:auto;border-radius:12px 12px 0 0;border-width:2px 0 0;padding-bottom:max(14px,env(safe-area-inset-bottom,0px))}
}
"""
head = """<title>Oportunidades Cochabamba</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800&family=Public+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
"""
(C / 'plantilla_departamento.html').write_text(head + css.replace('</style>', extra + '</style>') + '\n' + (C / '_cuerpo_departamento.html').read_text())
print('plantilla_departamento.html lista')
