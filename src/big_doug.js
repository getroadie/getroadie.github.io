// Big Doug, the Roadie's moose. bigDoug(mood) -> SVG string. mood: "chill" | "panic" | "hyped"
function bigDoug(mood, cls) {
  mood = mood || "chill";
  const O = "#4a2e17";  // outline
  const defs = `<defs>
    <radialGradient id="bdFace" cx="50%" cy="38%" r="65%"><stop offset="0" stop-color="#a26c45"/><stop offset=".7" stop-color="#7d4f2f"/><stop offset="1" stop-color="#5e3a21"/></radialGradient>
    <radialGradient id="bdMuz" cx="50%" cy="30%" r="70%"><stop offset="0" stop-color="#c08a5e"/><stop offset="1" stop-color="#94613d"/></radialGradient>
    <linearGradient id="bdAnt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f1d6a6"/><stop offset="1" stop-color="#c99a5e"/></linearGradient>
    <pattern id="bdPlaid" width="16" height="16" patternUnits="userSpaceOnUse"><rect width="16" height="16" fill="#b8322a"/><rect width="16" height="6" y="5" fill="#7d1f1a" opacity=".85"/><rect width="6" height="16" x="5" fill="#7d1f1a" opacity=".85"/><rect width="16" height="1.4" y="7.3" fill="#16202e" opacity=".55"/><rect width="1.4" height="16" x="7.3" fill="#16202e" opacity=".55"/></pattern>
  </defs>`;
  const antler = `<path d="M96 66 C76 70 52 64 38 50 C28 40 22 26 24 10 L33 22 L36 6 L45 22 L50 6 L57 26 L64 12 L68 32 L76 22 L76 42 C84 50 92 56 100 58 Z" fill="url(#bdAnt)" stroke="${O}" stroke-width="3.2" stroke-linejoin="round"/>
    <path d="M44 44 C56 52 72 56 88 58" fill="none" stroke="#fff" stroke-width="2" opacity=".45" stroke-linecap="round"/>`;
  const ear = `<path d="M90 92 C70 78 50 80 40 92 C52 104 74 106 92 100 Z" fill="#7d4f2f" stroke="${O}" stroke-width="3" stroke-linejoin="round"/><path d="M84 95 C70 88 58 89 50 94 C60 99 72 100 84 98 Z" fill="#c98f74"/>`;
  const body = `<path d="M30 270 C34 236 52 220 84 212 L106 206 L134 206 L156 212 C188 220 206 236 210 270 Z" fill="url(#bdPlaid)" stroke="${O}" stroke-width="3" stroke-linejoin="round"/>
    <path d="M104 207 L120 246 L136 207 Z" fill="#16202e"/><path d="M104 207 L96 228 L112 230 Z M136 207 L144 228 L128 230 Z" fill="#922a23" stroke="${O}" stroke-width="2" stroke-linejoin="round"/>`;
  const head = `<rect x="98" y="182" width="44" height="34" fill="#6a4228"/>
    <path d="M88 70 C88 46 152 46 152 70 L160 116 C167 132 172 146 173 160 C176 194 150 210 120 210 C90 210 64 194 67 160 C68 146 73 132 80 116 Z" fill="url(#bdFace)" stroke="${O}" stroke-width="3.2" stroke-linejoin="round"/>
    <path d="M110 214 C104 232 112 246 120 246 C128 246 136 232 130 214 Z" fill="#6a4228" stroke="${O}" stroke-width="2.6"/>`;
  const muzzle = `<path d="M74 146 C74 124 166 124 166 146 C174 182 154 202 120 202 C86 202 66 182 74 146 Z" fill="url(#bdMuz)" stroke="${O}" stroke-width="3" stroke-linejoin="round"/>
    <ellipse cx="104" cy="166" rx="7.5" ry="11.5" transform="rotate(16 104 166)" fill="#3a2211"/><ellipse cx="136" cy="166" rx="7.5" ry="11.5" transform="rotate(-16 136 166)" fill="#3a2211"/>
    <path d="M92 138 C102 132 118 131 130 134" fill="none" stroke="#fff" stroke-width="3" opacity=".35" stroke-linecap="round"/>`;
  // cap: navy crown, front seam, top button, curved bill, and the real Roadie plate as the front patch
  const plate = (typeof BD_PLATE !== "undefined" && BD_PLATE)
    ? BD_PLATE.replace(/<svg[^>]*>/, '<svg x="101" y="45" width="30" height="15.6" viewBox="0 0 200 104">')
    : `<rect x="101" y="45" width="30" height="15.6" rx="3" fill="#fff"/>`;
  const cap = `<path d="M86 66 C84 34 156 34 154 66 Z" fill="#12305b" stroke="${O}" stroke-width="3" stroke-linejoin="round"/>
    <path d="M120 40 V64" stroke="#0b1f3d" stroke-width="1.6" opacity=".6"/><circle cx="120" cy="40" r="2.6" fill="#0b1f3d"/>
    <path d="M80 66 C96 58 144 58 162 66 C156 76 88 76 80 66 Z" fill="#0b1f3d" stroke="${O}" stroke-width="3" stroke-linejoin="round"/>
    <rect x="99.5" y="43.5" width="33" height="18.6" rx="3.5" fill="#fff" stroke="#0b1f3d" stroke-width="1.2"/>${plate}`;
  // headset: earpiece sits on the ear, mic boom runs outside the face line to the corner of the mouth
  const headset = `<path d="M64 98 C52 126 56 168 92 190" fill="none" stroke="#16202e" stroke-width="3.4" stroke-linecap="round"/><circle cx="94" cy="191" r="5" fill="#16202e"/>
    <circle cx="64" cy="94" r="9.5" fill="#16202e" stroke="#3a4356" stroke-width="2.5"/>`;
  const badge = `<path d="M108 210 L114 244 M132 210 L126 244" stroke="#f5b301" stroke-width="4"/>
    <g transform="rotate(-4 120 252)"><rect x="94" y="240" width="52" height="26" rx="4" fill="#fff" stroke="${O}" stroke-width="2.4"/><rect x="94" y="240" width="52" height="8" rx="3" fill="#f5b301"/><text x="120" y="260.5" font-family="Arial Black,Arial,sans-serif" font-weight="900" font-size="8.6" text-anchor="middle" fill="#16202e">CO-PILOT</text></g>`;
  let eyes, mouth, extra = "";
  if (mood === "panic") {
    eyes = `<ellipse cx="100" cy="106" rx="14" ry="15" fill="#fff" stroke="${O}" stroke-width="2"/><ellipse cx="140" cy="106" rx="14" ry="15" fill="#fff" stroke="${O}" stroke-width="2"/>
      <circle cx="101" cy="108" r="3.6" fill="#16202e"/><circle cx="139" cy="108" r="3.6" fill="#16202e"/>
      <path d="M84 82 Q98 72 112 82 M128 82 Q142 72 156 82" fill="none" stroke="${O}" stroke-width="4.5" stroke-linecap="round"/>`;
    mouth = `<path d="M106 194 C108 188 132 188 134 194 C132 200 108 200 106 194 Z" fill="#3a2211"/><path d="M110 192 h20" stroke="#fff" stroke-width="2.2"/>`;
    extra = `<path d="M166 92 C171 102 175 106 170 113 C165 118 158 113 160 106 Z" fill="#a9dbff" stroke="#3f86c4" stroke-width="1.6"/>
      <path d="M182 74 l4 -10 M190 82 l9 -6 M186 92 l10 0" stroke="#b42318" stroke-width="3" stroke-linecap="round"/>`;
  } else if (mood === "hyped") {
    eyes = `<path d="M84 98 C84 116 112 118 114 100 Z M126 100 C128 118 156 116 156 98 Z" fill="#16202e" stroke="${O}" stroke-width="2"/>
      <path d="M114 100 Q120 95 126 100 M84 98 L74 94 M156 98 L166 94" stroke="#16202e" stroke-width="3.2" fill="none" stroke-linecap="round"/>
      <path d="M90 102 l8 6 M132 102 l8 6" stroke="#8da2c0" stroke-width="2.6" stroke-linecap="round"/>
      <path d="M84 86 Q98 80 112 86 M128 86 Q142 80 156 86" fill="none" stroke="${O}" stroke-width="4" stroke-linecap="round"/>`;
    mouth = `<path d="M98 190 C104 206 136 206 142 190 Z" fill="#3a2211" stroke="${O}" stroke-width="2"/><path d="M104 191 H136 L134 196 H106 Z" fill="#fff"/>`;
    extra = `<g fill="#f5b301" stroke="#c98d00" stroke-width="1.4"><path d="M190 120 l4 9 l9 1 l-7 6 l2 9 l-8 -5 l-8 5 l2 -9 l-7 -6 l9 -1 z"/><path d="M40 130 l3 7 l7 1 l-5 5 l1 7 l-6 -4 l-6 4 l1 -7 l-5 -5 l7 -1 z"/><path d="M200 60 l2.4 5 l5 .7 l-3.7 3.5 l.9 5 l-4.6 -2.4 l-4.6 2.4 l.9 -5 l-3.7 -3.5 l5 -.7 z"/></g>`;
  } else {
    eyes = `<ellipse cx="100" cy="106" rx="11" ry="12" fill="#fff" stroke="${O}" stroke-width="2"/><ellipse cx="140" cy="106" rx="11" ry="12" fill="#fff" stroke="${O}" stroke-width="2"/>
      <circle cx="102" cy="110" r="5.2" fill="#16202e"/><circle cx="142" cy="110" r="5.2" fill="#16202e"/><circle cx="103.6" cy="108.4" r="1.4" fill="#fff"/><circle cx="143.6" cy="108.4" r="1.4" fill="#fff"/>
      <path d="M88 105 C88 92 112 92 112 105 Z M128 105 C128 92 152 92 152 105 Z" fill="#7d4f2f"/><path d="M88 105 H112 M128 105 H152" stroke="${O}" stroke-width="3" stroke-linecap="round"/>
      <path d="M86 90 Q100 86 114 92 M126 92 Q140 86 154 90" fill="none" stroke="${O}" stroke-width="4" stroke-linecap="round"/>`;
    mouth = `<path d="M104 194 Q122 200 138 190" fill="none" stroke="${O}" stroke-width="3.2" stroke-linecap="round"/>`;
  }
  return `<svg class="${cls || "doug"}" viewBox="0 0 240 272" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Big Doug the moose">${defs}
    ${body}${antler}<g transform="translate(240 0) scale(-1 1)">${antler}</g>${ear}<g transform="translate(240 0) scale(-1 1)">${ear}</g>
    ${head}${eyes}${muzzle}${mouth}${cap}${badge}${extra}</svg>`;
}
