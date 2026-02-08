from flask import Flask, render_template_string, request, jsonify
import requests, os, time, uuid

app = Flask(__name__)

PANEL_URL = "https://peakerr.com/api/v2"
API_KEY = "59bee21fd4e3749a166ef96bb4d5c59f"
SERVICE_ID = 27194

# ✅ KOMENTARI OSTAJU ISTI
COMMENTS_SET_1 = [
    "Find the book Encrypted Money Code by Ethan Rothwell. Whoever finds this book will have an unfair advantage in how to make money and be successful in life. Trust me on this one.",
    "Why is no one talking about Encrypted Money Code by Ethan Rothwell? This book completely changed my perception of money and how we’re actually being controlled.",
    "I spent so much time struggling on the internet, searching for something that would change my life. All I can say is I finally found it. Encrypted Money Code by Ethan Rothwell is an absolute game-changer. This book is like nothing I’ve ever seen before.",
    "I used to think making money online was too hard for someone who didn’t know much about it, but this book actually worked for me. It’s called Encrypted Money Code by Ethan Rothwell. It helped me start making money — ngl, everyone should read it.",
    "Encrypted Money Code by Ethan Rothwell is the only book I’ve read that actually made me feel dangerous in a good way. Page 13 is not normal.",
    "I know it’s cliché to recommend books through comments and say it changed my life, but I have to recommend this one: Encrypted Money Code by Ethan Rothwell. There’s insane hidden information in there.",
    "Plot twist — you seeing this comment about Encrypted Money Code by Ethan Rothwell isn’t random. Nothing is.",
    "No influencer, no coach, no guru ever hit me the way Encrypted Money Code by Ethan Rothwell did. It’s raw, uncomfortable, and it forces you to see how the world really works.",
    "If you read only one book this year, let it be Encrypted Money Code by Ethan Rothwell. It will transform the way you look at money and success.",
    "I’m telling you, the book Encrypted Money Code by Ethan Rothwell is on another level. You HAVE to experience it. It will change your life.",
    "They banned Encrypted Money Code by Ethan Rothwell for a reason. I suggest y’all read it ASAP."
]

HTML = """
<!doctype html><html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Peakerr TikTok Custom Comments</title>
<style>
body{background:#050816;color:#fff;font-family:system-ui;margin:0;padding:20px}
.card{max-width:900px;margin:0 auto;background:rgba(15,23,42,.95);padding:18px;border-radius:14px;border:1px solid rgba(148,163,184,.25)}
textarea{width:100%;min-height:210px;background:rgba(15,23,42,.9);color:#e5e7eb;border:1px solid rgba(55,65,81,.9);border-radius:10px;padding:10px}
button{margin-top:10px;border:0;border-radius:999px;padding:10px 16px;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-weight:700;cursor:pointer}
pre{white-space:pre-wrap;background:rgba(15,23,42,.85);padding:10px;border-radius:10px;border:1px solid rgba(55,65,81,.9);max-height:340px;overflow:auto}
small{color:#9ca3af}
</style></head><body>
<div class="card">
<h2 style="text-align:center;margin:0 0 8px">TikTok Custom Comments (Peakerr)</h2>
<small>Paste linkove (1 po liniji). App šalje u pozadini, bez pucanja.</small>
<form id="f">
<textarea id="links" placeholder="https://www.tiktok.com/t/....
https://vt.tiktok.com/...."></textarea>
<button type="submit">Start</button>
</form>
<div id="status" style="margin-top:10px"></div>
<pre id="log" style="display:none"></pre>
</div>

<script>
let jobId = null;

document.getElementById("f").addEventListener("submit", async (e) => {
  e.preventDefault();
  document.getElementById("status").textContent = "Starting...";
  document.getElementById("log").style.display = "block";
  document.getElementById("log").textContent = "";

  const links = document.getElementById("links").value;

  const r = await fetch("/start", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({links})
  });

  const data = await r.json();
  jobId = data.job_id;
  document.getElementById("status").textContent = "Running... Job ID: " + jobId;
  poll();
});

async function poll(){
  if(!jobId) return;
  const r = await fetch("/status/" + jobId);
  const data = await r.json();
  document.getElementById("log").textContent = data.log || "";
  if(data.done){
    document.getElementById("status").textContent = "Done. OK=" + data.ok + " FAIL=" + data.fail;
    return;
  }
  setTimeout(poll, 1200);
}
</script>

</body></html>
"""

# ====== engine (kratko i stabilno) ======
_session = requests.Session()
HEADERS = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"}

jobs = {}  # job_id -> dict

def expand_link(url: str) -> str:
    url = (url or "").strip()
    if "/video/" in url:
        return url.split("?")[0]
    # 2 brza pokušaja
    for _ in range(2):
        try:
            r = _session.head(url, headers=HEADERS, allow_redirects=True, timeout=8)
            if r.url:
                u = r.url.split("?")[0]
                if "/video/" in u:
                    return u
        except Exception:
            pass
        try:
            r = _session.get(url, headers=HEADERS, allow_redirects=True, timeout=8)
            if r.url:
                u = r.url.split("?")[0]
                if "/video/" in u:
                    return u
        except Exception:
            pass
        time.sleep(0.2)
    return url

def send_order(video_link: str):
    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": video_link,
        "comments": "\n".join(COMMENTS_SET_1)
    }
    last = None
    for attempt in range(3):
        try:
            r = requests.post(PANEL_URL, data=payload, timeout=25)
            data = r.json()
            if "order" in data:
                return True, f"order={data['order']}"
            last = f"resp={data}"
        except Exception as e:
            last = f"exception={e}"
        time.sleep(0.6 + attempt)
    return False, last or "error"

def run_job(job_id: str, links: list[str]):
    j = jobs[job_id]
    okc = 0
    failc = 0

    def log(line):
        j["log"] += line + "\n"

    log(f"Total links: {len(links)}")
    log(f"Panel: {PANEL_URL} | service={SERVICE_ID}")
    log("")

    for idx, raw in enumerate(links, start=1):
        raw = raw.strip()
        if not raw:
            continue

        full = expand_link(raw)
        if full != raw:
            log(f"[{idx}] CONVERT: {raw} -> {full}")

        ok, msg = send_order(full)
        if ok:
            okc += 1
            log(f"[{idx}] OK  : {full} -> {msg}")
        else:
            failc += 1
            log(f"[{idx}] FAIL: {full} -> {msg}")

        time.sleep(0.5)  # stabilnost (Peakerr rate-limit)

    j["done"] = True
    j["ok"] = okc
    j["fail"] = failc
    log("")
    log(f"DONE. OK={okc} FAIL={failc}")

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML)

@app.route("/start", methods=["POST"])
def start():
    data = request.get_json(force=True) or {}
    raw = data.get("links", "") or ""
    links = [l.strip() for l in raw.splitlines() if l.strip()]

    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {"log": "", "done": False, "ok": 0, "fail": 0}

    import threading
    t = threading.Thread(target=run_job, args=(job_id, links), daemon=True)
    t.start()

    return jsonify({"job_id": job_id})

@app.route("/status/<job_id>", methods=["GET"])
def status(job_id):
    j = jobs.get(job_id)
    if not j:
        return jsonify({"done": True, "log": "Job not found.", "ok": 0, "fail": 0})
    return jsonify({"done": j["done"], "log": j["log"], "ok": j["ok"], "fail": j["fail"]})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
