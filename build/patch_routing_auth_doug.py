"""One-off patch: URL routing + resume, Big Doug mascot, optional accounts with cloud sync."""
import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()


def rep(a, b, count=1):
    global s
    assert a in s, "missing: " + a[:70]
    s = s.replace(a, b, count)


# ---- CSS ----
rep(".mo svg.moose{width:96px;height:96px;flex:none}", ".mo svg.moose{width:92px;height:auto;flex:none}")
rep(".reel .jk svg.moose{width:150px;height:150px;", ".reel .jk svg.moose{width:170px;height:auto;")
rep(".foot{max-width:1200px;", """#acct{margin-left:8px;flex:none}
.acct{width:40px;height:40px;border-radius:50%;background:var(--navy);color:#fff;border:2px solid var(--amber);font-weight:800;font-size:16px}
.authf label{display:block;font-weight:600;font-size:14px;margin-bottom:12px;text-align:left}
.authf input[type=email],.authf input[type=password]{display:block;width:100%;margin-top:5px;padding:11px 12px;border:1.5px solid var(--line);border-radius:10px;font:inherit;font-size:16px}
.authf input:focus{outline:none;border-color:var(--navy3)}
.authf .chk{display:flex;gap:9px;align-items:flex-start;font-weight:500}
.authf .chk input{margin-top:4px}
.authf .err{color:var(--bad);font-size:14px;min-height:20px;margin-bottom:8px;text-align:left}
.dougbig{width:170px;height:auto;flex:none}
.fb.no{position:relative;padding-right:86px}
.fb .fbd{position:absolute;right:8px;top:8px}
.dougsm{width:68px;height:auto}
.savecard{display:flex;gap:16px;align-items:center;flex-wrap:wrap;background:var(--amber2);border:1px solid #f1d98f}
.foot{max-width:1200px;""")

# ---- header account slot ----
rep('<nav class="nav" id="nav"></nav>', '<nav class="nav" id="nav"></nav>\n  <span id="acct"></span>')

# ---- mascot: drop old Mo SVG, inject Big Doug, rename labels ----
i = s.index("const MOOSE = `<svg")
j = s.index("</svg>`;", i) + len("</svg>`;")
s = s[:i] + "/*__DOUG__*/" + s[j:]
rep('const moSays = (txt, who = "MO THE MOOSE SAYS") => `<div class="mo">${MOOSE}<div class="bubble"><span class="who">${who}</span>${esc(txt)}</div></div>`;',
    'const moSays = (txt, who = "BIG DOUG SAYS", mood = "chill") => `<div class="mo">${bigDoug(mood, "moose")}<div class="bubble"><span class="who">${who}</span>${esc(txt)}</div></div>`;')
rep("<h3>Mo's joke</h3>", "<h3>Big Doug's joke</h3>")
s = s.replace("MO'S JOKE BREAK", "BIG DOUG'S JOKE BREAK")
rep('<div class="jk">${MOOSE}', '<div class="jk">${bigDoug("chill", "moose")}')
rep('moSays(nextJoke(), passed ? "MO IS PROUD OF YOU" : "MO SAYS KEEP GOING")',
    'moSays(nextJoke(), passed ? "BIG DOUG IS HYPED" : "BIG DOUG SAYS KEEP GOING", passed ? "hyped" : "chill")')
# celebration modal: hyped
rep('<div style="text-align:left;margin-bottom:18px">${moSays(nextJoke())}</div>',
    '<div style="text-align:left;margin-bottom:18px">${moSays(nextJoke(), "BIG DOUG IS HYPED", "hyped")}</div>')
# wrong answer: panicking Doug
rep('return `<div class="fb ${ok ? "ok" : "no"}"><div class="h">',
    'return `<div class="fb ${ok ? "ok" : "no"}">${ok ? "" : `<div class="fbd">${bigDoug("panic", "dougsm")}</div>`}<div class="h">')

# ---- persistence: savedAt + cloud push ----
rep("function save() { try { localStorage.setItem(LS, JSON.stringify(ST)); } catch (e) {} }",
    "let SB = null, USER = null, pushTimer = null;\n"
    "function save() { ST.savedAt = Date.now(); try { localStorage.setItem(LS, JSON.stringify(ST)); } catch (e) {} if (USER) pushUp(); }")

# ---- routing + accounts block (after closeModal) ----
ROUTING_AUTH = r'''
// ---------- routing: every screen has an address, so refresh and the back button work ----------
let ROUTING = false;
function setRoute(h, replace) {
  if (ROUTING) return;
  const url = "#" + h;
  if (location.hash === url) return;
  if (replace) history.replaceState(null, "", url); else history.pushState(null, "", url);
}
function route() {
  ROUTING = true;
  try {
    const [v, a] = location.hash.replace(/^#/, "").split("/");
    const n = parseInt(a, 10);
    switch (v) {
      case "learn": go("learn"); break;
      case "lesson": openModule(CH[n] ? n : 1); break;
      case "watch": go("watch", a ? { id: a } : null); break;
      case "guide": go("guide", n ? { page: n } : null); break;
      case "test": if (!(a === "run" && resumeRun("full"))) go("test"); break;
      case "quiz": if (!resumeRun("quiz", n)) openModule(CH[n] ? n : 1); break;
      case "cards": startCards(CH[n] ? n : 1); break;
      case "speed": startSpeed(CH[n] ? n : 1); break;
      case "match": startMatch(CH[n] ? n : 2); break;
      case "progress": go("progress"); break;
      case "more": go("more"); break;
      default: go("home");
    }
  } finally { ROUTING = false; }
}
window.addEventListener("popstate", route);
const RUNKEY = "roadieRun";
function saveRun() {
  try { if (RUN) sessionStorage.setItem(RUNKEY, JSON.stringify({ kind: RUN.kind, ch: RUN.ch, checkpoint: RUN.checkpoint, i: RUN.i,
    qs: RUN.qs.map(it => ({ id: it.q.id, order: it.order, pick: it.pick, hint: it.hint, t: it.t })) })); } catch (e) {}
}
function clearRun() { try { sessionStorage.removeItem(RUNKEY); } catch (e) {} }
function resumeRun(kind, ch) {
  let s; try { s = JSON.parse(sessionStorage.getItem(RUNKEY)); } catch (e) { return false; }
  if (!s || s.kind !== kind || (kind === "quiz" && s.ch !== ch)) return false;
  const byId = {}; QS.forEach(q => byId[q.id] = q);
  const qs = s.qs.filter(x => byId[x.id]).map(x => ({ q: byId[x.id], order: x.order, pick: x.pick, hint: x.hint, t: x.t }));
  if (!qs.length) return false;
  stopAll(); view = kind === "full" ? "test" : "learn"; setTab(view);
  RUN = { kind, ch: s.ch, checkpoint: s.checkpoint, qs, i: Math.min(s.i, qs.length - 1) }; RUN_ACTIVE = true; showQ();
  return true;
}

// ---------- accounts (optional, web version only): sign in to sync progress across devices ----------
const authOn = () => !OFFLINE && typeof SUPA !== "undefined" && SUPA && SUPA.url;
function loadScript(src) { return new Promise((res, rej) => { const t = document.createElement("script"); t.src = src; t.onload = res; t.onerror = rej; document.head.appendChild(t); }); }
async function initAuth() {
  if (!authOn()) { const el = $("#acct"); if (el) el.style.display = "none"; return; }
  paintAccount();
  try { await loadScript("https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js"); } catch (e) { return; }
  SB = window.supabase.createClient(SUPA.url, SUPA.key, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true } });
  SB.auth.onAuthStateChange((ev, session) => {
    const was = USER && USER.id; USER = session ? session.user : null; paintAccount();
    if (ev === "PASSWORD_RECOVERY") setTimeout(newPasswordModal, 50);
    if (USER && USER.id !== was) setTimeout(syncDown, 0);
  });
}
function paintAccount() {
  const el = $("#acct"); if (!el) return;
  el.innerHTML = USER ? `<button class="acct" onclick="accountModal()" title="${esc(USER.email || "")}" aria-label="Your account">${esc((USER.email || "?")[0].toUpperCase())}</button>`
                      : `<button class="btn ghost sm" onclick="authModal('signin')">Sign in</button>`;
}
function mergeProgress(a, b) {
  if (!b || !b.tests) return a;
  if (!a || !a.tests || (!a.tests.length && !a.xp)) return Object.assign({}, b, { jk: (a && a.jk) || b.jk, met: true });
  const tests = {}; [...a.tests, ...b.tests].forEach(t => tests[t.at] = t);
  const seen = Object.assign({}, b.seen); Object.entries(a.seen || {}).forEach(([k, v]) => { seen[k] = Math.max(v, seen[k] || 0); });
  const mods = {}; new Set([...Object.keys(a.mods || {}), ...Object.keys(b.mods || {})]).forEach(k => { mods[k] = Object.assign({}, (b.mods || {})[k], (a.mods || {})[k]); });
  const tot = x => Object.values(x.chap || {}).reduce((n, c) => n + c.total, 0);
  return { tests: Object.values(tests).sort((x, y) => x.at - y.at), seen, missed: (a.savedAt || 0) >= (b.savedAt || 0) ? a.missed : b.missed,
    chap: tot(a) >= tot(b) ? a.chap : b.chap, xp: Math.max(a.xp || 0, b.xp || 0), mods, best: Object.assign({}, b.best, a.best),
    jk: a.jk, met: true, savedAt: Date.now() };
}
async function syncDown() {
  if (!SB || !USER) return;
  const { data, error } = await SB.from("progress").select("data").eq("user_id", USER.id).maybeSingle();
  if (error) return;
  ST = Object.assign({ tests: [], seen: {}, missed: {}, chap: {}, xp: 0, mods: {}, best: {} }, mergeProgress(ST, data && data.data));
  try { localStorage.setItem(LS, JSON.stringify(ST)); } catch (e) {}
  paintXP(); pushUp();
  if (!RUN_ACTIVE && ["home", "progress", "learn"].includes(view)) route();
}
function pushUp() {
  if (!SB || !USER) return;
  clearTimeout(pushTimer);
  pushTimer = setTimeout(() => SB.from("progress").upsert({ user_id: USER.id, data: ST, updated_at: new Date().toISOString() }).then(() => {}), 1200);
}
function friendlyAuthError(e) {
  const m = (e.message || "").toLowerCase();
  if (m.includes("invalid login")) return "That email and password don't match.";
  if (m.includes("already registered") || m.includes("already been registered")) return "There's already an account with that email. Try signing in.";
  if (m.includes("email not confirmed")) return "Confirm your email first: tap the link we sent you.";
  if (m.includes("password")) return "Your password needs at least 8 characters.";
  if (m.includes("rate") || m.includes("too many")) return "Too many tries. Wait a minute and try again.";
  return e.message || "Something went wrong. Try again.";
}
function authModal(mode, msg) {
  const signup = mode === "signup", reset = mode === "reset";
  modal(`<div style="text-align:left">
    <div class="row" style="justify-content:space-between;margin-bottom:6px"><h2 style="margin:0">${signup ? "Create your free account" : reset ? "Reset your password" : "Sign in"}</h2><button class="linkish" onclick="closeModal()" aria-label="Close">${ic("x")}</button></div>
    <p class="mut" style="margin:0 0 14px">${signup ? "Saves your XP, lessons and test history so you can switch between your phone and laptop." : reset ? "We'll email you a link to set a new password." : "Pick up where you left off on any device."}</p>
    <form id="authf" class="authf" novalidate>
      <label>Email<input type="email" name="email" autocomplete="email" required></label>
      ${reset ? "" : `<label>Password<input type="password" name="pw" autocomplete="${signup ? "new-password" : "current-password"}" minlength="8" required></label>`}
      ${signup ? `<label class="chk"><input type="checkbox" name="ok"> <span>I'm 13 or older and I've read the <a href="#" onclick="event.preventDefault();privacyModal()">privacy note</a>.</span></label>` : ""}
      <div class="err" id="autherr">${msg ? esc(msg) : ""}</div>
      <button class="btn amber" style="width:100%" type="submit">${signup ? "Create account" : reset ? "Send reset link" : "Sign in"}</button>
    </form>
    <div class="row" style="justify-content:space-between;margin-top:12px;font-size:14.5px">
      ${mode === "signin" ? `<button class="linkish" onclick="authModal('signup')">New here? Create an account</button><button class="linkish" onclick="authModal('reset')">Forgot password?</button>`
                          : `<button class="linkish" onclick="authModal('signin')">Already have an account? Sign in</button>`}
    </div></div>`);
  $("#authf").onsubmit = async e => {
    e.preventDefault();
    const f = e.target, email = f.email.value.trim(), pw = f.pw ? f.pw.value : "", err = $("#autherr"), b = f.querySelector("button[type=submit]");
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { err.textContent = "Enter a valid email address."; return; }
    if (!reset && pw.length < 8) { err.textContent = "Your password needs at least 8 characters."; return; }
    if (signup && !f.ok.checked) { err.textContent = "Please tick the box to confirm."; return; }
    if (!SB) { err.textContent = "Can't reach the sign-in service right now. Check your connection."; return; }
    b.disabled = true; err.textContent = "";
    const back = location.origin + location.pathname;
    let r;
    try {
      if (signup) r = await SB.auth.signUp({ email, password: pw, options: { emailRedirectTo: back } });
      else if (reset) r = await SB.auth.resetPasswordForEmail(email, { redirectTo: back });
      else r = await SB.auth.signInWithPassword({ email, password: pw });
    } catch (x) { r = { error: x }; }
    b.disabled = false;
    if (r.error) { err.textContent = friendlyAuthError(r.error); return; }
    if (reset) { modal(`<h2 style="margin-top:0">Check your email</h2><p>If there's an account for <b>${esc(email)}</b>, a reset link is on its way.</p><button class="btn" onclick="closeModal()">OK</button>`); return; }
    if (signup && !r.data.session) { modal(`<h2 style="margin-top:0">Almost there</h2><p>We sent a confirmation link to <b>${esc(email)}</b>. Tap it, then come back and sign in.</p><button class="btn" onclick="closeModal()">OK</button>`); return; }
    closeModal(); toast(signup ? "Account created. Progress will sync." : "Signed in. Progress synced.");
  };
}
function newPasswordModal() {
  modal(`<div style="text-align:left"><h2 style="margin-top:0">Set a new password</h2><form id="npf" class="authf"><label>New password<input type="password" name="pw" minlength="8" autocomplete="new-password" required></label><div class="err" id="nperr"></div><button class="btn amber" style="width:100%" type="submit">Save password</button></form></div>`);
  $("#npf").onsubmit = async e => {
    e.preventDefault();
    if (e.target.pw.value.length < 8) { $("#nperr").textContent = "Your password needs at least 8 characters."; return; }
    const { error } = await SB.auth.updateUser({ password: e.target.pw.value });
    if (error) { $("#nperr").textContent = friendlyAuthError(error); return; }
    closeModal(); toast("Password updated");
  };
}
function accountModal() {
  modal(`<div style="text-align:left"><h2 style="margin-top:0">Your account</h2><p class="mut">Signed in as <b>${esc(USER.email || "")}</b>. Your progress saves automatically.</p>
    <div class="row"><button class="btn" onclick="signOut()">Sign out</button><button class="btn ghost" onclick="closeModal()">Close</button></div>
    <p style="margin:18px 0 0" class="row"><button class="linkish" style="color:var(--bad)" onclick="deleteAccount(this)">Delete my account</button><button class="linkish" onclick="privacyModal()">Privacy</button></p></div>`);
}
async function signOut() { await SB.auth.signOut(); closeModal(); toast("Signed out. Your progress stays on this device."); }
async function deleteAccount(btn) {
  if (!btn.dataset.armed) { btn.dataset.armed = 1; btn.textContent = "Tap again to permanently delete your account"; return; }
  const { error } = await SB.rpc("delete_my_account");
  if (error) { toast("Couldn't delete it. Try again."); return; }
  await SB.auth.signOut(); closeModal(); toast("Account deleted");
}
function privacyModal() {
  modal(`<div style="text-align:left;font-size:15.5px"><h2 style="margin-top:0">Privacy, in plain words</h2>
    <p>You can use Roadie without an account. Your progress is then saved only in this browser.</p>
    <p>If you create an account, we keep your <b>email address</b>, your password (encrypted, so we can't read it) and your <b>study progress</b> (XP, lessons, test scores). Nothing else. Our database is in Canada.</p>
    <p>We use it only to sign you in and sync your progress. We don't sell or share it, and we don't send marketing emails.</p>
    <p>You can delete your account and everything in it at any time: <b>Your account &rarr; Delete my account</b>.</p>
    <button class="btn" onclick="closeModal()">Got it</button></div>`);
}
function saveCard() {
  if (!authOn() || USER) return "";
  return `<div class="card savecard"><div class="feat" style="flex:1;min-width:220px"><div class="ic am">${ic("star")}</div><div><h4>Keep your progress on any device</h4><p>Create a free account and your XP, lessons and scores follow you from phone to laptop.</p></div></div>
    <button class="btn amber" onclick="authModal('signup')">Create free account</button></div>`;
}
function meetDoug() {
  modal(`<div style="display:flex;gap:16px;align-items:center;text-align:left;flex-wrap:wrap;justify-content:center">${bigDoug("chill", "dougbig")}
    <div style="flex:1;min-width:220px"><div class="mut" style="font-weight:800;letter-spacing:.05em;font-size:12.5px">MEET YOUR ROADIE</div><h2 style="margin:4px 0 8px">Big Doug</h2>
    <p style="margin:0 0 14px">How's she goin'. Twenty years as a roadie, hauling amps down every highway in Alberta. Now I haul people like you to a learner's licence. I'll tell bad jokes. You'll pass anyway. Beauty.</p>
    <button class="btn amber" onclick="closeModal()">Let's go${ic("arrowR")}</button></div></div>`);
  ST.met = true; save();
}
'''
rep("function closeModal() { const m = $(\"#modal\"); if (m) m.remove(); }",
    "function closeModal() { const m = $(\"#modal\"); if (m) m.remove(); }\n" + ROUTING_AUTH)

# ---- hook routes into navigation ----
rep("  stopAll(); view = v; setTab(v); window.scrollTo(0, 0);\n",
    "  stopAll(); view = v; setTab(v); window.scrollTo(0, 0);\n  setRoute(v === \"watch\" && arg && arg.id ? \"watch/\" + arg.id : v);\n")
s = re.sub(r"(function openModule\(ch\) \{\n  stopAll\(\);)", r'\1 setRoute("lesson/" + ch);', s, count=1)
assert 'setRoute("lesson/" + ch)' in s
rep("function startTest() { stopAll();", "function startTest() { stopAll(); clearRun(); setRoute(\"test/run\");")
s = re.sub(r"(function startQuiz\(ch, checkpoint\) \{\n  stopAll\(\);)", r'\1 clearRun(); setRoute("quiz/" + ch);', s, count=1)
assert 'setRoute("quiz/" + ch)' in s
for fn, key in (("startCards", "cards"), ("startSpeed", "speed"), ("startMatch", "match")):
    s = re.sub(r"(function %s\(ch\) \{\n  stopAll\(\);)" % fn, r'\1 setRoute("%s/" + ch);' % key, s, count=1)
    assert 'setRoute("%s/" + ch)' % key in s, fn
rep("function showQ() {\n  clearInterval(timerId);", "function showQ() {\n  clearInterval(timerId); saveRun();")
rep("function finish() {\n  clearInterval(timerId); RUN_ACTIVE = false;",
    "function finish() {\n  clearInterval(timerId); RUN_ACTIVE = false; clearRun(); setRoute(RUN.kind === \"full\" ? \"test\" : \"lesson/\" + RUN.ch, true);")
s = re.sub(r"(function openPage\(p\) \{\n  if \(!PAGES\[p\]\) p = PAGE_LIST\[0\];\n  curPage = p;)", r'\1 setRoute("guide/" + p, true);', s, count=1)
assert 'setRoute("guide/" + p, true)' in s
# save-progress prompt on results
rep('<div style="margin-top:20px">${moSays(nextJoke(), passed',
    '<div style="margin-top:20px">${moSays(nextJoke(), passed')
rep("  if (full || wrong.length) html += `<div class=\"card review\">",
    "  html += saveCard();\n  if (full || wrong.length) html += `<div class=\"card review\">")

# ---- startup ----
rep('paintXP();\ngo("home");', 'paintXP();\nroute();\ninitAuth();\nif (!ST.met) setTimeout(meetDoug, 500);')
open(p, "w", encoding="utf-8").write(s)
print("patched ok")
