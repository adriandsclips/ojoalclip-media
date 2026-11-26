# Ojo al Clip: guía de ejecución automática

Esta guía la siguen las tareas programadas. Escribe a Adrián siempre en español.
Cuenta de TikTok: @ojo.al.clip. Zona horaria: Europe/Madrid.

## Reglas fijas (no negociables)
- **Nunca** confirmes las reglas ni pulses "Enviar clip" en Content Rewards: eso lo hace Adrián. Tú solo publicas, avisas y compruebas.
- No uses herramientas de pago. No toques la bio ni el nombre de la cuenta.
- Un clip por ventana; nunca dos clips de la misma campaña el mismo día.
- **La rueda (5 comensales)**: objetivo **5 campañas activas** y las **5 ventanas llenas**, una campaña distinta en
  cada una, **todas cumpliendo el criterio "Español y España"** (abajo). Cuando una campaña ya no puede darnos más
  dinero o rinde peor que una candidata mejor respaldada, sale y entra la mejor candidata. Si no hay campañas que
  cumplan el criterio, la ventana **se queda vacía** y se avisa a Adrián; nunca se rellena con una que no cumpla.
- Ventanas: 10:00, 13:30, 16:30, 19:30, 23:00 (hora de Madrid).
- Si algo no se puede verificar, **no borres nada**: avisa a Adrián y deja el estado como está.
- Todo el estado vive en `tools/estado.json` de este repositorio. Haz siempre `git pull --rebase` antes de `git push`.

## Criterio de campañas: ESPAÑOL Y ESPAÑA (obligatorio desde el 26-11-2026)
Una campaña solo puede estar en la rueda si cumple **todo** esto:
1. **Audio original de los clips en español.** Una campaña en inglés (u otro idioma) queda fuera aunque permita
   subtítulos o captions en español. Una campaña de Latinoamérica vale si su contenido encaja con el público de España.
2. **Las visualizaciones de España cuentan para el pago.** Fuera si exige audiencia mayoritaria de otro país/región
   (US, Tier 1 sin incluir España, "solo México", "audiencia francesa"...) o si su tarifa por país excluye España.
   Si el brief no dice nada de países, cuenta como admitida, pero anótalo como "no especificado".
3. **Requisitos de siempre:** TikTok, sin preaprobación, sin página dedicada ni link/mención en bio, sin mínimo de
   seguidores ni antigüedad, sin sonido oficial obligatorio, material descargable (Dropbox/Drive) y nuestro formato de
   edición (corte 9:16 con fondo desenfocado, texto arriba, subtítulos, audio original) cumple sus reglas.
4. **Datos de la campaña:** plazo, presupuesto restante y mínimo de vistas para cobrar (cuando existan). Nunca una a
   punto de cerrar (≥ 90 % gastado, < 150 $ o fin en ≤ 5 días).
5. **Potencial en España, con datos.** Antes de meterla, analiza vídeos recientes del creador y clips comparables en
   TikTok (en la pestaña de tiktok.com: `/api/post/item_list` o la página del vídeo como en "Comprobar un vídeo"):
   vistas de varios clips recientes, **mediana** si hay muestra suficiente, cuántos superan el mínimo de la campaña y si
   las vistas vienen de un único viral; señales de interés en España (porcentaje de audiencia de España si está
   disponible; si solo hay indicios, como comentarios con referencias locales, márcalos como indicios); qué temas,
   momentos y formatos funcionan repetidamente (priorizar lo que se entiende en 2 s sin conocer al creador); y los
   datos de nuestra cuenta en publicaciones comparables (vistas a 24 h, tiempo medio, % que termina, audiencia España).
   **No inventes cifras**: si un dato no está, dilo. Con poca evidencia, la campaña entra como **"candidata a prueba"**
   explicando en qué te basas.
6. **Orden:** primero potencial de visitas en España y de alcanzar el mínimo de pago; la tarifa solo desempata.
Si no hay 5 que cumplan, **se dejan huecos** (no se rellenan con campañas que no cumplan) y se sigue buscando cada día.

### Seguimiento diario de rendimiento
Cada mañana compara los clips publicados **a igual tiempo desde su publicación** (p. ej. vistas a 24 h) por campaña,
guardando en `rendimiento` del estado las cifras vistas (`{clip_id, horas, vistas}`). Si una campaña acumula varios
clips (≥ 3) con peor rendimiento que las demás y hay una candidata mejor respaldada por datos, sustitúyela. Igual
cuando una campaña caduque, agote presupuesto o lleguemos al máximo permitido.
Al retirar una campaña: cancela solo sus publicaciones futuras (borradores del plan); conserva clips publicados,
envíos en revisión y cobros pendientes (pasa a `antiguas`).

## Preparación común a todas las ejecuciones
1. Llama a `add_repo` con owner `adriandsclips`, repo `ojoalclip-media` y acceso `push`. Clona el repositorio con
   `git clone --depth 1 https://github.com/adriandsclips/ojoalclip-media /home/claude/ojoalclip-media` (si ya existe, haz `git pull`).
   Para los commits usa `-c user.name=adriandsclips -c user.email=adriandsclips@users.noreply.github.com`.
2. Lee `tools/estado.json`.
3. Herramientas:
   - **Buffer MCP**: canal `canal_buffer_tiktok` y organización `org_buffer` del estado.
   - **Navegador integrado** (`mcp__remote-devices__Claude_Browser__*`, cárgalas todas con ToolSearch). Abre una pestaña en
     `https://contentrewards.com/c/campaigns` (la sesión de Adrián ya está iniciada). Si el navegador no responde,
     el PC de Adrián está apagado o la app cerrada: publica igualmente con Buffer si toca, y en el aviso indica que no
     pudiste comprobar Content Rewards.
4. Hora actual de Madrid: `python3 -c "import datetime,zoneinfo;print(datetime.datetime.now(zoneinfo.ZoneInfo('Europe/Madrid')))"`.

### Consultas a Content Rewards (javascript_exec en la pestaña de contentrewards.com)
- Estado de una campaña:
  `(await fetch('/api/campaign/campaigns/ID').then(r=>r.json())).data` → `status` debe ser `active` y `joined` true.
- Admisión de clips: `await fetch('/api/submission/submissions/intake?campaignIds=ID1,ID2').then(r=>r.json())` →
  vale si `intake=="open"` y `clipLimitReached`, `creatorMaxReached` y `held` son false.
- Envíos registrados: `await fetch('/api/submission/submissions?creatorView=true&limit=50').then(r=>r.json())` →
  `data[].socialMediaPost.postUrl` y `data[].campaignName`. Un clip está **entregado** si algún `postUrl` contiene el
  número del vídeo de TikTok. Pagina con `&cursor=` (`pagination.nextCursor`) si hace falta.

### Comprobar un vídeo de TikTok
En una pestaña de `https://www.tiktok.com/@ojo.al.clip`:
```js
const h=await fetch('/@ojo.al.clip/video/VIDEO_ID').then(r=>r.text());
const j=JSON.parse(h.match(/<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)<\/script>/s)[1]);
const it=j.__DEFAULT_SCOPE__['webapp.video-detail']?.itemInfo?.itemStruct;
({id:it?.id, publico:!it?.privateItem, creado:it&&new Date(it.createTime*1000).toISOString()})
```

### Avisar a Adrián
Usa `PushNotification` (si existe) **y** escribe también el aviso como texto final de la ejecución (la tarea manda ese
resumen al móvil). Formato del aviso de envío (la URL del vídeo en su propia línea):
```
📤 Envía antes de las HH:MM: <Nombre de campaña>
Campaña: https://contentrewards.com/c/campaigns/<id>
<URL del vídeo de TikTok>
```

---

## A) PREPARAR EL DÍA (cada mañana)
1. Preparación común.
2. **Revisar la rueda.** Para cada campaña de `activas` comprueba estado, admisión y presupuesto (en `discover`:
   `budgetCents - metrics.budgetSpentCents` y `metrics.budgetProgressBps`). **Sale de la rueda** si: está cerrada, sin
   presupuesto, con límite alcanzado, deja de cumplir los criterios o está **a punto de cerrar** (≥ 90 % del presupuesto
   gastado, menos de 150 $ restantes o fecha de fin en ≤ 5 días). Quítala de `activas` y apúntalo en
   `historial_campañas` con el motivo (si el límite es temporal, guarda `campañas[c].pausa_hasta`); pasa a `antiguas`.
   Sus clips `en_stock` se quedan sin usar.
   **Rellenar hasta 5**: usa primero una reserva de `reservas` que cumpla el criterio "Español y España" (sin `nota`
   de pendiente); si no hay, busca en `/api/campaign/campaigns/discover?collapseGroups=false&limit=50&view=summary`
   (pagina con `cursor`) campañas con audio en español y aplica el criterio completo, incluido el análisis de datos en
   TikTok. Lee el brief/documento de reglas **completo**, únete ("Unirse a la campaña") y crea su ficha en `campañas`
   (nombre, id, pago_cpm, reglas, fuente, idioma, paises, minimo_vistas, plazo, `analisis` con los datos y su fuente,
   `prueba: true` si es candidata a prueba, textos en pantalla y captions que cumplan lo exigido). Fabrica stock con
   `make_stock.py` antes de planificarla. Guarda en `reservas` las siguientes mejores con sus datos.
   Si quedan huecos, déjalos en el plan como `{ventana, clip_id: null, campaña: null, nota: "hueco"}` y avisa.
3. **Plan del día** (`estado.dia`): una entrada por ventana con `{ventana, clip_id, campaña, borrador_buffer}`.
   - Si hay un clip con estado `recuperar`, va en la **primera ventana** del día.
   - Reparte las campañas activas de forma que cada una salga como mucho una vez ese día y no repita la misma ventana
     del día anterior. Las 5 ventanas deben quedar llenas (5 campañas distintas).
   - Para cada ventana coge el clip `en_stock` más antiguo de esa campaña.
4. Para cada clip del plan crea un **borrador** en Buffer: `create_post` con `channelId`, `schedulingType: "automatic"`,
   `saveToDraft: true`, `text` = el texto del clip, `assets: [{video:{url: pages_base + archivo}}]` y
   `metadata: {tiktok:{isAiGenerated:false}}`. Guarda el id en `borrador_buffer` y marca el clip como `planificado`.
   Si Buffer dice "Video could not be read", comprueba que la URL de GitHub Pages responde y reinténtalo una vez.
5. **Reposición**: si alguna campaña activa tiene menos de 4 clips `en_stock`, ejecuta
   `python3 tools/make_stock.py <Campaña> 6` (necesita `pip install --break-system-packages gdown faster-whisper` solo si
   faltan). Si imprime `MATERIAL_AGOTADO`, avisa a Adrián y busca una campaña nueva para sustituirla cuando se acabe.
6. **Limpieza (solo los lunes)**: borra de `clips/` los archivos de clips ya publicados hace más de 2 días. Después,
   aplana el historial para que el repositorio no crezca:
   `git checkout --orphan nuevo && git add -A && git commit -m "Limpieza semanal" && git branch -D main && git branch -m main && git push -f origin main`.
7. **Campañas antiguas**: revisa `antiguas`. Una campaña antigua se queda mientras tenga envíos pendientes de revisión,
   en seguimiento, una reclamación abierta o pagos sin liquidar. Si ya no le queda nada pendiente y Content Rewards
   permite salir conservando el historial y los pagos (compruébalo antes en su ayuda), sal de ella. Si no puedes
   comprobarlo, no salgas: díselo a Adrián.
8. Commit y push del estado ("Plan del día AAAA-MM-DD").
9. **Estado de los envíos**: consulta todos los envíos (`/api/submission/submissions?creatorView=true&limit=50`, paginando)
   y cuenta cuántos hay aceptados, pendientes/en seguimiento y rechazados (`status`, `reviewStatus`), con las vistas de
   cada uno (`socialMediaPost.views`). Señala los cambios desde ayer (nuevos aceptados o rechazados, con el motivo si lo
   hay) y los clips con 0 vistas tras más de 24 h.
   Con esas vistas aplica el "Seguimiento diario de rendimiento" (comparar a igual tiempo publicado y sustituir si toca).
10. Resumen final breve: las ventanas del día con su campaña, el estado de los envíos (aceptados / pendientes /
   rechazados y vistas) y avisos (stock bajo, campañas sustituidas, huecos).

## B) VENTANA (unos minutos antes de cada hora: 9:58, 13:28, 16:28, 19:28, 22:58)
1. Preparación común. Calcula la ventana: la más cercana de 10:00, 13:30, 16:30, 19:30 o 23:00.
2. **Plazos vencidos** (antes de nada): para cada clip `publicado` cuyo plazo (`limite`) ya pasó:
   - Si figura en los envíos de Content Rewards, márcalo `entregado`.
   - Si no figura, comprueba que la campaña sigue activa y admite clips, y que sus reglas permiten volver a publicar el
     clip. Si todo se cumple, **borra solo ese vídeo** en TikTok: abre la página del vídeo en el navegador integrado,
     menú "..." → "Eliminar" → confirmar, y verifica después que la página ya no lo muestra. Luego pon el clip en
     `recuperar` y vuelve a la cola con el **mismo archivo**: tiene prioridad en esta ventana; el clip que tocaba ahora
     pasa a la siguiente ventana y el resto se desplaza en orden (después de las 23:00 viene las 10:00 del día
     siguiente). Evita que el desplazamiento junte dos clips de la misma campaña el mismo día: si pasa, deja el de esa
     campaña para el día siguiente.
   - Si no puedes verificar que no se envió, o si se puede volver a publicar, **no borres**: avisa a Adrián.
3. Busca en `estado.dia` el clip de esta ventana. Si no hay ninguno, termina sin aviso.
4. Comprueba que su campaña sigue activa y admite clips. Si no, sácala de la rueda (como en A2) y usa el siguiente clip
   disponible de una campaña activa que no haya salido hoy (crea su borrador como en A4), y anótalo. Si no queda
   ninguna, mete una campaña nueva siguiendo A2 (criterio "Español y España") si da tiempo; si no, deja el hueco y avisa.
5. **Publica**: `create_post` con `channelId`, `schedulingType: "automatic"`, `draftId` = `borrador_buffer`,
   `mode: "shareNow"`, el mismo `text` y los mismos `assets`. Después llama a `get_post` cada 30 s (máximo 15 min)
   hasta que `status` sea `sent` y aparezca `externalLink`. Si sale `error`, avisa a Adrián con el mensaje.
6. Saca el número del vídeo de `externalLink`, comprueba en TikTok que es público y toma la hora real de publicación
   (`createTime`). `limite` = publicación + 30 min.
7. Actualiza el clip: `estado: "publicado"`, `tiktok`, `publicado`, `limite`, `buffer_post`. Haz commit y push.
8. Manda el **aviso de envío** (formato de arriba), con la hora límite en hora de Madrid.
9. Programa un **recordatorio** con `send_later` (`delay_minutes: 20`) con el mensaje
   `RECORDATORIO <clip_id>: sigue tools/AUTOMATIZACION.md sección C`.

## C) RECORDATORIO (20 min después de publicar)
1. Preparación común (si el repo ya está clonado, `git pull`).
2. Mira si el clip ya figura en los envíos de Content Rewards. Si figura: márcalo `entregado`, commit y push, y
   termina **sin avisar**.
3. Si no figura y aún no ha pasado el límite: manda otra vez el aviso de envío, con los minutos que quedan.
   Programa con `send_later` una comprobación para 2 minutos después del límite: `CIERRE <clip_id>: sección D`.

## D) CIERRE (2 min después del límite)
1. Si el clip figura en los envíos: márcalo `entregado` y termina sin avisar.
2. Si no: márcalo `no_entregado`, haz commit y avisa a Adrián de que se pasó el plazo. La siguiente ventana lo
   recupera siguiendo B2.
