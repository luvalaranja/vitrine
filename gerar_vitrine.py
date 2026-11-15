#!/usr/bin/env python3
"""Gera a vitrine pública da Luva Laranja (busca por código) a partir de produtos.json.
Uso: python3 gerar_vitrine.py produtos.json vitrine.html
produtos.json: lista de {codigo, nome, tema, carrossel, data (AAAA-MM-DD), loja, preco, de, data_preco,
                         detalhe, link, status: ativo|esgotado, thumb: "fotos/COD.jpg" (600×750, 4:5)}
Regras: produto da Amazon nunca mostra preço; esgotado fica na lista com aviso e sem link.
O HTML é autônomo (fotos por caminho relativo): serve no Claude e em hospedagem própria.
"""
import json, sys

src, dst = sys.argv[1], sys.argv[2]
itens = json.load(open(src, encoding="utf8"))
itens.sort(key=lambda p: p.get("codigo", ""))
itens.sort(key=lambda p: p.get("data", ""), reverse=True)
for p in itens:
    if p.get("loja") == "Amazon":
        p["preco"] = None; p["de"] = None
dados = json.dumps(itens, ensure_ascii=False).replace("</", "<\\/")

PAGE = r"""<title>Achados Luva Laranja</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="Os achados da @luvalaranja por código: digite o código da etiqueta e abra o anúncio.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,600&family=Cormorant+SC:wght@700&family=Manrope:wght@500;700;800&display=swap">
<style>
/* Layout: arara de etiquetas — fotos 4:5 em duas colunas, cada uma com a etiqueta laranja do carrossel pendurada; busca em forma de etiqueta de papel.
   Mundo único e escuro (o café das faixas do carrossel), escolhido de propósito: não muda com o tema do aparelho. */
:root{
  color-scheme:dark;
  --cafe:#211B17;      /* fundo: o café das faixas */
  --cafe-2:#2E2621;    /* fundo das fotos enquanto carregam */
  --creme:#F6EDE1;     /* texto */
  --areia:#C9B9A6;     /* texto secundário */
  --papel:#F3EEE6;     /* etiqueta de busca */
  --tinta:#2A2420;     /* texto sobre papel */
  --laranja:#D0682A;   /* etiqueta de preço */
  --serif:"Cormorant Garamond",Georgia,"Times New Roman",serif;
  --versal:"Cormorant SC","Cormorant Garamond",Georgia,serif;
  --sans:"Manrope",system-ui,-apple-system,"Segoe UI",sans-serif;
}
*{box-sizing:border-box}
body{background:var(--cafe);color:var(--creme);font:500 15px/1.5 var(--sans)}
.wrap{max-width:720px;margin:0 auto;padding-left:max(18px,env(safe-area-inset-left,0px));padding-right:max(18px,env(safe-area-inset-right,0px));padding-block:28px 56px;display:flex;flex-direction:column;gap:26px}
header{display:flex;flex-direction:column;gap:2px}
.logo{font:italic 600 34px/1 var(--serif);letter-spacing:-.01em}
.logo span{color:var(--laranja)}
.tese{margin:0;font:500 19px/1.3 var(--serif);color:var(--areia)}

/* busca: etiqueta de papel com furo e barbante */
.busca{position:relative;display:grid;grid-template-columns:auto 1fr;align-items:center;background:var(--papel);color:var(--tinta);border-radius:6px 14px 14px 6px;padding:6px 16px 6px 46px;clip-path:polygon(22px 0,100% 0,100% 100%,22px 100%,0 50%)}
.busca::before{content:"";position:absolute;left:24px;top:50%;width:12px;height:12px;margin-top:-6px;border-radius:50%;background:var(--cafe)}
.busca label{font:700 13px var(--sans);color:#6E6158;padding-right:10px;border-right:1px solid #D8CDBF;margin-right:12px;white-space:nowrap}
.busca input{min-width:0;width:100%;border:0;background:transparent;color:var(--tinta);font:700 26px/1.2 var(--versal);letter-spacing:.04em;padding:10px 0}
.busca input::placeholder{color:#A39385;font-family:var(--serif);font-style:italic;font-weight:500;letter-spacing:0;font-size:21px}
.busca input:focus{outline:none}
.busca:focus-within{box-shadow:0 0 0 3px var(--laranja)}

nav.temas{display:flex;gap:18px;overflow-x:auto;padding-bottom:4px;margin-top:-8px}
nav.temas button{flex:0 0 auto;background:none;border:0;padding:4px 0;color:var(--areia);font:500 17px var(--serif);cursor:pointer;border-bottom:1.5px solid transparent}
nav.temas button[aria-pressed="true"]{color:var(--creme);border-bottom-color:var(--laranja)}
nav.temas button:focus-visible{outline:2px solid var(--laranja);outline-offset:3px}

.arara{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px 14px}
@media (min-width:620px){.arara{grid-template-columns:repeat(3,minmax(0,1fr))}}
.item{display:flex;flex-direction:column;gap:8px;min-width:0;scroll-margin-top:24px}
.foto{position:relative;display:block;aspect-ratio:4/5;max-width:100%;background:var(--cafe-2);border-radius:3px;overflow:visible}
.foto img{width:100%;height:100%;object-fit:cover;border-radius:3px;display:block}
.tag{position:absolute;left:-6px;bottom:14px;display:flex;align-items:center;gap:8px;background:var(--laranja);color:var(--creme);padding:6px 12px 6px 22px;clip-path:polygon(12px 0,100% 0,100% 100%,12px 100%,0 50%);font:700 19px/1 var(--versal);letter-spacing:.05em;transform-origin:0 50%}
.tag::before{content:"";position:absolute;left:10px;top:50%;width:6px;height:6px;margin-top:-3px;border-radius:50%;background:var(--creme)}
.nome{margin:0;font:600 19px/1.15 var(--serif);text-wrap:balance}
.preco{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap;font-variant-numeric:tabular-nums}
.preco b{font:800 16px var(--sans)}
.preco s{font-size:13px;color:var(--areia)}
.quando{font-size:12.5px;color:var(--areia)}
.ir{align-self:flex-start;color:var(--creme);font:700 14px var(--sans);text-decoration:underline;text-decoration-color:var(--laranja);text-decoration-thickness:2px;text-underline-offset:4px}
.ir:focus-visible{outline:2px solid var(--laranja);outline-offset:3px}
.esgotado .foto img{filter:grayscale(1) brightness(.7)}
.esgotado .tag{background:#6E6158}
.sem{font-size:13.5px;color:var(--areia)}
.item.achado .foto{outline:2px solid var(--laranja);outline-offset:4px}
@media (prefers-reduced-motion:no-preference){.item.achado .tag{animation:balanca 1.1s ease-out 1}}
@keyframes balanca{0%{transform:rotate(-14deg)}35%{transform:rotate(7deg)}65%{transform:rotate(-3deg)}100%{transform:rotate(0)}}
.vazio{margin:0;font:500 19px/1.4 var(--serif);color:var(--areia)}
footer{display:flex;flex-direction:column;gap:6px;font-size:12.5px;color:var(--areia);max-width:60ch;border-top:1px solid #3A312B;padding-top:16px}
</style>
<div class="wrap">
  <header>
    <div class="logo">luva laranja<span>.</span></div>
    <p class="tese">Achados de casa e do dia a dia, com preço de verdade.</p>
  </header>
  <form class="busca" id="busca" role="search">
    <label for="q">Código</label>
    <input id="q" type="search" inputmode="search" autocomplete="off" autocapitalize="characters" spellcheck="false" placeholder="ex.: MP02">
  </form>
  <nav class="temas" id="temas" aria-label="Temas"></nav>
  <section class="arara" id="arara" aria-live="polite"></section>
  <footer>
    <span>Preço visto na data indicada; a loja pode mudar. Os links são de afiliado: a loja me paga uma comissão e você paga o mesmo preço.</span>
    <span>@luvalaranja no Instagram</span>
  </footer>
</div>
<script id="dados" type="application/json">__DADOS__</script>
<script>
const P=JSON.parse(document.getElementById("dados").textContent);
const arara=document.getElementById("arara"),q=document.getElementById("q"),nav=document.getElementById("temas");
let tema="Tudo";
const norm=s=>String(s||"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/\s+/g,"");
function el(tag,attrs,...kids){const e=document.createElement(tag);for(const[k,v]of Object.entries(attrs||{}))if(v!=null)e.setAttribute(k,v);for(const c of kids)if(c!=null)e.append(c);return e}
const temas=["Tudo"].concat([...new Set(P.map(p=>p.tema).filter(Boolean))]);
for(const t of temas){const b=el("button",{type:"button",id:"tema-"+norm(t),"aria-pressed":t===tema?"true":"false"},t);b.addEventListener("click",()=>{tema=t;for(const x of nav.children)x.setAttribute("aria-pressed",x===b?"true":"false");render()});nav.append(b)}
const lojaTxt=l=>l==="Mercado Livre"?"no Mercado Livre":l==="Shopee"?"na Shopee":l==="Amazon"?"na Amazon":"na loja";
function item(p){
  const esg=p.status==="esgotado";
  const foto=el("div",{class:"foto"},el("img",{src:p.thumb,alt:p.nome,loading:"lazy",width:"600",height:"750"}),el("span",{class:"tag"},p.codigo));
  const preco=p.preco?el("div",{class:"preco"},el("b",{},p.preco),p.de?el("s",{},p.de):null):null;
  const quando=p.preco?el("span",{class:"quando"},"visto em "+(p.data_preco||"")):el("span",{class:"quando"},"Preço no anúncio");
  const acao=esg?el("span",{class:"sem"},"Esgotado ou pausado na loja"):el("a",{class:"ir",href:p.link,target:"_blank",rel:"noopener sponsored"},"Ver "+lojaTxt(p.loja));
  return el("article",{class:"item"+(esg?" esgotado":""),id:p.codigo},foto,el("h2",{class:"nome"},p.nome),preco,quando,acao);
}
function render(){
  const t=norm(q.value);
  const r=P.filter(p=>(tema==="Tudo"||p.tema===tema)&&(!t||norm(p.codigo).includes(t)||norm(p.nome).includes(t)));
  arara.replaceChildren(...(r.length?r.map(item):[el("p",{class:"vazio"},"Nenhuma etiqueta com “"+q.value+"”. O código fica no canto da foto de cada produto no post.")]));
  const alvo=t&&r.find(p=>norm(p.codigo)===t);
  if(alvo)document.getElementById(alvo.codigo).classList.add("achado");
}
document.getElementById("busca").addEventListener("submit",e=>{e.preventDefault();q.blur()});
q.addEventListener("input",render);
function doHash(){const h=decodeURIComponent(location.hash.slice(1)).toUpperCase();if(h&&P.some(p=>p.codigo===h)){q.value=h;render();const c=document.getElementById(h);if(c)c.scrollIntoView({block:"center"})}else render()}
window.addEventListener("hashchange",doHash);doHash();
</script>
"""
open(dst, "w", encoding="utf8").write(PAGE.replace("__DADOS__", dados))
print("ok", len(itens), "itens")
