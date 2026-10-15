// Resumaker · clean
// 单栏、ATS 友好、中英文混排。内容全部来自同目录下的 resume.yaml。
// 可以针对某次投递直接改这个文件（它是从模板复制过来的副本）。

#let data = yaml("resume.yaml")
#let meta = data.at("meta", default: (:))
#let basics = data.at("basics", default: (:))

#let accent = rgb(meta.at("accent", default: "#1F4E79"))
#let ink = rgb("#1F2328")
#let muted = rgb("#57606A")
#let rule-color = rgb("#D0D7DE")

#let density = meta.at("density", default: "normal")
#let (base-size, leading, gap) = if density == "compact" {
  (9.6pt, 0.55em, 0.55em)
} else if density == "airy" {
  (10.6pt, 0.72em, 0.9em)
} else {
  (10.1pt, 0.62em, 0.72em)
}

#let lang = meta.at("lang", default: "zh")
#let fonts = meta.at("fonts", default: (
  "Inter", "Helvetica Neue", "Arial",
  "Noto Sans CJK SC", "Source Han Sans SC", "Noto Sans SC",
  "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Heiti SC",
))

#set document(title: basics.at("name", default: "Resume"), author: basics.at("name", default: ""))
#let margins = (x: 15mm, top: 13mm, bottom: 12mm)
#set page(paper: meta.at("paper", default: "a4"), margin: margins)
#set text(
  font: fonts,
  size: base-size,
  fill: ink,
  lang: lang,
  region: if lang == "zh" { "cn" } else { none },
)
#set par(leading: leading, spacing: leading, justify: false)
#set list(indent: 0.2em, body-indent: 0.55em, spacing: leading, marker: text(fill: accent, size: 0.8em, baseline: -0.08em)[•])

// `**加粗**` → strong；其余原样输出，避免把用户文本当成 Typst 标记解释。
#let rich(s) = {
  if s == none { return [] }
  let parts = str(s).split("**")
  for (i, p) in parts.enumerate() {
    if calc.odd(i) { strong(p) } else { p }
  }
}

#let link-or-text(item) = {
  let label = item.at("text", default: item.at("url", default: ""))
  let url = item.at("url", default: none)
  if url != none { link(url, label) } else { label }
}

// ── Header ─────────────────────────────────────────────
#block(below: gap * 1.4)[
  #text(size: 2.05em, weight: "bold", tracking: 0.02em, basics.at("name", default: ""))
  #if basics.at("headline", default: none) != none {
    h(0.6em)
    text(size: 1.05em, fill: muted, basics.headline)
  }
  #v(0.15em)
  #let contacts = basics.at("contacts", default: ())
  #text(size: 0.92em, fill: muted, contacts.map(link-or-text).join(h(0.5em) + text(fill: rule-color)[|] + h(0.5em)))
]

#if data.at("summary", default: none) != none {
  block(below: gap * 1.2, text(fill: ink, rich(data.summary)))
}

// ── Building blocks ────────────────────────────────────
#let section-title(title) = block(above: gap * 1.5, below: gap * 0.9, sticky: true)[
  #text(size: 1.08em, weight: "bold", fill: accent, tracking: 0.04em, title)
  #v(-0.6em)
  #line(length: 100%, stroke: 0.6pt + rule-color)
]

#let entry(item) = block(above: gap * 1.35, below: 0pt, breakable: true)[
  #grid(
    columns: (1fr, auto),
    column-gutter: 1em,
    [
      #text(weight: "bold", item.at("title", default: ""))
      #if item.at("subtitle", default: none) != none {
        h(0.5em); text(fill: ink, item.subtitle)
      }
      #if item.at("meta", default: none) != none {
        h(0.5em); text(fill: muted, size: 0.92em, item.meta)
      }
    ],
    text(fill: muted, size: 0.92em, item.at("period", default: "")),
  )
  #if item.at("summary", default: none) != none {
    v(-0.2em)
    text(fill: muted, size: 0.95em, rich(item.summary))
  }
  #let bullets = item.at("bullets", default: ())
  #if bullets.len() > 0 {
    v(-0.25em)
    list(..bullets.map(b => rich(if type(b) == dictionary { b.text } else { b })))
  }
]

#let skills(items) = grid(
  columns: (auto, 1fr),
  column-gutter: 1em,
  row-gutter: leading,
  ..items.map(it => (
    text(weight: "bold", it.at("label", default: "")),
    rich(it.at("value", default: "")),
  )).flatten()
)

// ── Sections ───────────────────────────────────────────
#for section in data.at("sections", default: ()) {
  section-title(section.at("title", default: ""))
  let kind = section.at("kind", default: "entries")
  if kind == "entries" {
    for item in section.at("items", default: ()) { entry(item) }
  } else if kind == "skills" {
    skills(section.at("items", default: ()))
  } else if kind == "list" {
    list(..section.at("items", default: ()).map(b => rich(if type(b) == dictionary { b.text } else { b })))
  } else {
    rich(section.at("text", default: ""))
  }
}

// 供 render.py 读取：内容结束于第几页、页面的什么高度。
#context [#metadata((
  page: here().page(),
  y: here().position().y.pt(),
  height: page.height.pt(),
  top: margins.top.to-absolute().pt(),
  bottom: margins.bottom.to-absolute().pt(),
)) <resume-end>]
