# Ojo al Clip: guía de ejecución automática

Esta guía la siguen las tareas programadas. Escribe a Adrián siempre en español.
Cuenta de TikTok: @ojo.al.clip. Zona horaria: Europe/Madrid.

## Reglas fijas (no negociables)
- **Nunca** confirmes las reglas ni pulses "Enviar clip" en Content Rewards: eso lo hace Adrián. Tú solo publicas, avisas y compruebas.
- No uses herramientas de pago. No toques la bio ni el nombre de la cuenta.
- Un clip por ventana. **Dos ventanas al día: 16:30 y 23:00** (hora peninsular). Una misma campaña puede ocupar las
  dos ventanas del día si sus reglas lo permiten y los dos cortes son **escenas realmente distintas** (otro momento,
  otro concursante u otra prueba; nunca el mismo momento recortado de otra forma).
- **La rueda**: objetivo **2 publicaciones diarias**. Las campañas activas (`activas`) se ordenan por prioridad; las
  ventanas se rellenan con la primera que tenga un corte válido en stock. Si una campaña se agota o deja de encajar,
  sale y se busca sustituta automáticamente (A2). Si solo hay un corte que cumpla las reglas y merezca publicarse, se
  usa esa ventana y la otra queda vacía mientras se sigue buscando (se avisa en el resumen).
- **Prueba en curso (desde el 26-11-2026)**: se mantienen 2 publicaciones diarias. Cuando haya **10 clips con datos a
  72 h**, se revisa qué campañas y formatos funcionan. Solo se **propone** a Adrián subir a 3 ventanas si al menos 3
  clips han cumplido todos los mínimos de su campaña (vistas e interacción) **y** hay algún envío aprobado. No subas a
  3 sin su confirmación.
- Si algo no se puede verificar, **no borres nada**: avisa a Adrián y deja el estado como está.
- Todo el estado vive en `tools/estado.json` de este repositorio. Haz siempre `git pull --rebase` antes de `git push`.

## Criterio de campañas (desde el 26-11-2026; sustituye al filtro de solo español)
Se admiten campañas en **inglés y en español**. Una campaña entra en la rueda solo si cumple **todo** esto:
1. **Publicación y envío automatizables con lo que tenemos**: TikTok; sin preaprobación; sin página dedicada, nombre
   de usuario ni bio/enlace en bio; sin sonido oficial obligatorio (Buffer no puede añadirlo); sin etiqueta de
   colaboración pagada ni comentario fijado obligatorio; sin mínimo de seguidores/antigüedad que no cumplamos; material
   descargable de Dropbox o Google Drive. La cuenta (entretenimiento/clips general, sin contenido explícito) debe
   encajar en el tipo de página que pide la campaña.
2. **Qué vistas cuentan**: si exige audiencia mayoritaria de un país/región (US, Tier 1...) que no podemos acreditar,
   queda fuera. Si tiene tarifa por país (`configuration.geoRates`), las vistas del resto del mundo deben pagar > 0.
3. **Datos de pago**: tarifa, mínimo por clip (`minPayout / rate * 1000` = vistas para cobrar), tope, mínimo de
   interacción si existe, presupuesto restante y plazo. Nunca una a punto de cerrar (≥ 90 % gastado, < 150 $ o fin en
   ≤ 5 días).
4. **Nuestro montaje cumple sus reglas** (hashtags, descripción, música, texto en pantalla, duración, marcas).
5. **Evidencia de que el mínimo se alcanza**: prioridad a las campañas cuyo mínimo de pago alcanzan con cierta
   regularidad otros clippers **pequeños** (cuentas de < 1.000 seguidores) en clips recientes: mira la página del
   hashtag obligatorio o del creador en TikTok, anota vistas, mediana, cuántos superan el mínimo y cuántos cumplen
   además la interacción. Avisa de que la página del hashtag sesga hacia lo popular. **No inventes cifras.**
6. **Orden**: primero la probabilidad de alcanzar el mínimo (evidencia del punto 5 y umbral bajo), luego el presupuesto
   restante, y la tarifa como desempate.
**Prioridad actual: SourJacks** ("Clip JasonTheWeen", ficha `SourJacks`).

## Montaje por escenas (obligatorio para clips nuevos)
Herramienta: `tools/escenas.py` (ver su cabecera). Flujo:
1. `python3 tools/escenas.py transcribir <Campaña>` → transcripción con tiempos de todo el material.
2. Elige escenas leyendo la transcripción **y mirando fotogramas** (`ffmpeg -ss T -i fuente -frames:v 1 -vf scale=270:-1 x.png`
   y léelos): una escena que se entienda sola, que **empiece con la acción o con una frase que dé contexto desde el
   primer segundo** y que **conserve el desenlace**. Duración la de la escena (sin relleno), dentro de las reglas.
   Evita tramos donde se nombren otras marcas si la campaña lo prohíbe. No repitas escenas (`campañas[c].escenas_usadas`).
3. `python3 tools/escenas.py cortar <Campaña> <archivo> <inicio> <fin> "<texto pantalla>" "<caption>"`: subtítulos en
   el idioma original (`campañas[c].idioma`), texto de gancho arriba (sin emojis; `texto_seg` lo limita a los
   primeros segundos si el material ya trae rótulos), caption con los hashtags/menciones exigidos en el orden exigido,
   sin música añadida salvo que la campaña la permita.
4. Revisa 2-3 fotogramas del clip final antes de planificarlo.
`make_stock.py` (ventana de más energía) queda solo como último recurso.

## Seguimiento a 72 h (registro de la prueba)
En `estado.rendimiento` guarda, para cada clip publicado cuando cumpla 72 h (±12 h): `{clip_id, campaña, formato
(escena/tema), publicado, medido, horas, vistas, likes, comentarios, compartidos, interaccion = (likes+comentarios)/
vistas, cumple_vistas, cumple_interaccion, envio_estado (status/reviewStatus de Content Rewards), aprobado, pagado}`.
Datos de vistas/likes/comentarios: página del vídeo en TikTok ("Comprobar un vídeo", `stats`). Estado del envío: la
consulta de envíos de Content Rewards. "Cumple mínimos" (vistas e interacción) y "aprobado/pagado" se anotan **por
separado**. Si un dato no está, déjalo en `null`; no lo inventes.
Cuando haya 10 clips con datos a 72 h, el resumen de la mañana incluye la revisión (qué campañas y escenas funcionan)
y, si se cumple la condición de "Prueba en curso", la propuesta de pasar a 3 ventanas.
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
   **Rellenar**: si no hay ninguna campaña activa con cortes válidos para las 2 ventanas, usa una reserva de
   `reservas` que cumpla el "Criterio de campañas" o busca en
   `/api/campaign/campaigns/discover?collapseGroups=false&limit=50&view=summary` (pagina con `cursor`) y aplica el
   criterio completo, incluida la evidencia de clippers pequeños. Lee el brief **completo**, únete ("Unirse a la
   campaña"), crea su ficha en `campañas` (nombre, id, pago_cpm, idioma, minimo_vistas, minimo_pago_usd,
   maximo_pago_usd, interaccion_minima, paises, reglas, fuente, analisis con datos y fuente, texto_y/texto_seg) y
   produce cortes por escenas antes de planificarla. Guarda en `reservas` las siguientes mejores con sus datos.
3. **Plan del día** (`estado.dia`): una entrada por ventana con `{ventana, clip_id, campaña, borrador_buffer}`.
   - Si hay un clip con estado `recuperar`, va en la **primera ventana** del día.
   - Ventanas 16:30 y 23:00. Rellena por orden de `activas` (prioridad) con el clip `en_stock` más antiguo; puede ser
     la misma campaña en las dos ventanas si son escenas distintas. Si una ventana no tiene corte válido, déjala como
     `{ventana, clip_id: null, campaña: null, nota: "hueco"}` y sigue buscando.
4. Para cada clip del plan crea un **borrador** en Buffer: `create_post` con `channelId`, `schedulingType: "automatic"`,
   `saveToDraft: true`, `text` = el texto del clip, `assets: [{video:{url: pages_base + archivo}}]` y
   `metadata: {tiktok:{isAiGenerated:false}}`. Guarda el id en `borrador_buffer` y marca el clip como `planificado`.
   Si Buffer dice "Video could not be read", comprueba que la URL de GitHub Pages responde y reinténtalo una vez.
5. **Reposición**: si entre todas las campañas activas hay menos de 4 clips `en_stock`, produce cortes nuevos con el
   "Montaje por escenas" (necesita `pip install --break-system-packages gdown faster-whisper` solo si faltan). Si no
   quedan escenas válidas en el material, avisa a Adrián y busca otra campaña.
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
   Después aplica el "Seguimiento a 72 h" (registro de los clips que cumplen 72 h y revisión al llegar a 10).
10. Resumen final breve: las ventanas del día con su campaña, el estado de los envíos (aceptados / pendientes /
   rechazados y vistas) y avisos (stock bajo, campañas sustituidas, huecos).

## B) VENTANA (16:28 y 22:58)
1. Preparación común. Calcula la ventana: la más cercana de 16:30 o 23:00.
2. **Plazos vencidos** (antes de nada): para cada clip `publicado` cuyo plazo (`limite`) ya pasó:
   - Si figura en los envíos de Content Rewards, márcalo `entregado`.
   - Si no figura, comprueba que la campaña sigue activa y admite clips, y que sus reglas permiten volver a publicar el
     clip. Si todo se cumple, **borra solo ese vídeo** en TikTok: abre la página del vídeo en el navegador integrado,
     menú "..." → "Eliminar" → confirmar, y verifica después que la página ya no lo muestra. Luego pon el clip en
     `recuperar` y vuelve a la cola con el **mismo archivo**: tiene prioridad en esta ventana; el clip que tocaba ahora
     pasa a la siguiente ventana y el resto se desplaza en orden (después de las 23:00 viene las 16:30 del día
     siguiente).
   - Si no puedes verificar que no se envió, o si se puede volver a publicar, **no borres**: avisa a Adrián.
3. Busca en `estado.dia` el clip de esta ventana. Si no hay ninguno, termina sin aviso.
4. Comprueba que su campaña sigue activa y admite clips. Si no, sácala de la rueda (como en A2) y usa el siguiente clip
   `en_stock` de otra campaña activa (escena distinta a la de la otra ventana del día; crea su borrador como en A4), y
   anótalo. Si no queda ninguno, mete una campaña nueva siguiendo A2 (Criterio de campañas) si da tiempo; si no, deja
   el hueco y avisa.
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
