// Worker da Cloudflare: jogada do jogo da velha com um clique + contador de visitas.
//   GET /jogar?casa=5   → grava a jogada (e a resposta do bot) num commit e volta pro perfil
//   GET /visitas.svg    → badge do contador (sem cache, para o GitHub buscar a cada visita)
// Segredo: GITHUB_TOKEN (fine-grained, só Contents read/write em TheDougg/TheDougg). KV: VISITAS.
import { atualizarReadme, jogar, novoEstado, REPO } from "../../velha/jogo.mjs";

const PERFIL = `https://github.com/${REPO.split("/")[0]}`;
const VOLTA = `${PERFIL}#-jogue-comigo-jogo-da-velha-contra-meu-bot`;
const ROBOS = /bot|crawl|spider|slurp|preview|fetch|curl|wget|python|httpclient/i;
const ultimaJogada = new Map(); // freio por IP (melhor esforço, por instância)

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (url.pathname === "/jogar") {
      // qualquer falha (token ausente, GitHub fora) só devolve o visitante pro perfil
      return jogada(req, env, url).catch((e) => (console.error(e), Response.redirect(VOLTA, 302)));
    }
    if (url.pathname === "/visitas.svg") return visitas(env);
    if (url.pathname === "/robots.txt") return new Response("User-agent: *\nDisallow: /\n");
    return Response.redirect(PERFIL, 302);
  },
};

async function jogada(req, env, url) {
  const casa = Number(url.searchParams.get("casa"));
  const ip = req.headers.get("cf-connecting-ip") ?? "?";
  const agora = Date.now();
  // robôs que seguem links não jogam; e cada IP espera 3s entre jogadas
  if (ROBOS.test(req.headers.get("user-agent") ?? "") || agora - (ultimaJogada.get(ip) ?? 0) < 3000) {
    return Response.redirect(VOLTA, 302);
  }
  ultimaJogada.set(ip, agora);

  for (let tentativa = 0; tentativa < 4; tentativa++) {
    const gh = github(env.GITHUB_TOKEN);
    const ref = await gh(`git/ref/heads/main`);
    const base = await gh(`git/commits/${ref.object.sha}`);
    const [estadoArq, readmeArq] = await Promise.all([
      gh(`contents/data/velha.json?ref=${ref.object.sha}`).catch(() => null),
      gh(`contents/README.md?ref=${ref.object.sha}`),
    ]);
    const estado = estadoArq ? JSON.parse(base64(estadoArq.content)) : novoEstado();
    const { mudou } = jogar(estado, casa, null);
    if (!mudou) break;

    const arvore = await gh("git/trees", "POST", {
      base_tree: base.tree.sha,
      tree: [
        { path: "data/velha.json", mode: "100644", type: "blob", content: JSON.stringify(estado, null, 2) + "\n" },
        { path: "README.md", mode: "100644", type: "blob", content: atualizarReadme(base64(readmeArq.content), estado) },
      ],
    });
    // autor fictício (.invalid) para as jogadas dos visitantes não contarem como contribuição sua
    const commit = await gh("git/commits", "POST", {
      message: `velha: jogada anônima na casa ${casa}`,
      tree: arvore.sha,
      parents: [ref.object.sha],
      author: { name: "bot da velha", email: "bot@velha.invalid" },
    });
    try {
      await gh("git/refs/heads/main", "PATCH", { sha: commit.sha });
      break;
    } catch (e) {
      if (e.status !== 422) throw e; // 422 = alguém commitou antes: refaz em cima do novo main
    }
  }
  return Response.redirect(VOLTA, 302);
}

function github(token) {
  return async (caminho, method = "GET", corpo) => {
    const r = await fetch(`https://api.github.com/repos/${REPO}/${caminho}`, {
      method,
      headers: {
        authorization: `Bearer ${token}`,
        accept: "application/vnd.github+json",
        "user-agent": "velha-doug-worker",
        "x-github-api-version": "2022-11-28",
      },
      body: corpo ? JSON.stringify(corpo) : undefined,
    });
    if (!r.ok) throw Object.assign(new Error(`${method} ${caminho}: ${r.status}`), { status: r.status });
    return r.json();
  };
}

function base64(conteudo) {
  const bytes = Uint8Array.from(atob(conteudo.replace(/\n/g, "")), (c) => c.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

async function visitas(env) {
  const total = Number((await env.VISITAS.get("total")) ?? 0) + 1;
  await env.VISITAS.put("total", String(total));
  const n = total.toLocaleString("pt-BR");
  const largura = 92 + n.length * 10;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${largura}" height="28" role="img" aria-label="visitas: ${n}">
<rect width="${largura}" height="28" rx="4" fill="#0d1117"/><rect x="${largura - 18 - n.length * 10}" width="${18 + n.length * 10}" height="28" rx="4" fill="#00c853"/>
<rect x="${largura - 18 - n.length * 10}" width="6" height="28" fill="#00c853"/>
<g font-family="Verdana,DejaVu Sans,sans-serif" font-size="11" font-weight="700" letter-spacing="1.2">
<text x="12" y="18" fill="#00ff41">VISITAS</text><text x="${largura - 9 - n.length * 5}" y="18" fill="#02130a" text-anchor="middle">${n}</text></g></svg>`;
  return new Response(svg, {
    headers: {
      "content-type": "image/svg+xml; charset=utf-8",
      "cache-control": "max-age=0, no-cache, no-store, must-revalidate",
      expires: "0",
    },
  });
}
