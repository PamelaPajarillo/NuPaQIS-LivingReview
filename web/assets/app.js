/* NuPaQIS Living Review — rendering layer, three-page variant.

   One script serves all three pages; body[data-page] says which is which:
     overview  index.html     matrix, growth chart, topic index, recent papers
     nupa      by-nupa.html   listing grouped by NuPa topic
     qis       by-qis.html    listing grouped by QIS topic
*/

(function () {
  'use strict';

  var LINKS = window.__NUPAQIS_LINKS__ ||
    { overview: 'index.html', nupa: 'by-nupa.html', qis: 'by-qis.html',
      descriptions: 'descriptions.html', contribute: 'contribute.html' };
  var ROUTED = !!window.__NUPAQIS_LINKS__;   // preview build: no URL state

  var PAGE, state, data = null, index = { nupaGroup: {}, qisGroup: {}, nupaInfo: {}, qisInfo: {} };
  var el = {};

  function blankState() {
    return {
      query: '', nupa: new Set(), qis: new Set(),
      years: new Set(), types: new Set(), cell: null
    };
  }

  // ---------- helpers ----------

  function slug(text) {
    return String(text).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  }

  function node(tag, attrs, children) {
    var element = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (key) {
      if (key === 'class') element.className = attrs[key];
      else if (key === 'text') element.textContent = attrs[key];
      else if (key === 'html') element.innerHTML = attrs[key];
      else if (attrs[key] !== null && attrs[key] !== undefined) {
        element.setAttribute(key, attrs[key]);
      }
    });
    (children || []).forEach(function (child) { element.appendChild(child); });
    return element;
  }

  function link(page, hash) {
    return LINKS[page] + (hash ? (ROUTED ? '' : hash) : '');
  }

  function toast(message) {
    if (!el.toast) return;
    el.toast.textContent = message;
    el.toast.classList.add('is-visible');
    clearTimeout(toast.timer);
    toast.timer = setTimeout(function () { el.toast.classList.remove('is-visible'); }, 1800);
  }

  function copy(text, message) {
    navigator.clipboard.writeText(text).then(
      function () { toast(message); },
      function () { toast('Copying failed — your browser blocked it'); });
  }

  function download(filename, text) {
    var url = URL.createObjectURL(new Blob([text], { type: 'text/plain' }));
    var anchor = node('a', { href: url, download: filename });
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  }

  /* Cross-page navigation. In the real build these are separate documents, so
     we set the location; in the single-file preview a router handles it. */
  function go(page, hash, patch) {
    if (ROUTED) {
      window.__NUPAQIS_GO__(page, hash, patch);
    } else {
      location.href = LINKS[page] + (hash || '');
    }
  }

  // ---------- filtering ----------

  function searchable(paper) {
    if (!paper._haystack) {
      paper._haystack = [
        paper.title, paper.key, paper.journal || '',
        paper.authors.map(function (a) { return a.name; }).join(' '),
        paper.nupa.join(' '), paper.qis.join(' ')
      ].join(' ').toLowerCase();
    }
    return paper._haystack;
  }

  function matches(paper) {
    if (state.nupa.size && !paper.nupa.some(function (c) { return state.nupa.has(c); })) return false;
    if (state.qis.size && !paper.qis.some(function (c) { return state.qis.has(c); })) return false;
    if (state.years.size && !state.years.has(String(paper.year))) return false;
    if (state.types.size && !(paper.types || []).some(function (t) { return state.types.has(t); })) return false;
    if (state.cell) {
      if (index.nupaGroup[paper.nupa_primary] !== state.cell.nupa) return false;
      if (index.qisGroup[paper.qis_primary] !== state.cell.qis) return false;
    }
    if (state.query && searchable(paper).indexOf(state.query) === -1) return false;
    return true;
  }

  function selected() { return data.papers.filter(matches); }

  function facetCounts(kind, values) {
    var saved = state[kind], counts = {};
    values.forEach(function (value) {
      state[kind] = new Set([value]);
      counts[value] = data.papers.filter(matches).length;
    });
    state[kind] = saved;
    return counts;
  }

  function byGroup(categories) {
    var groups = [];
    categories.forEach(function (c) {
      if (groups.indexOf(c.group) === -1) groups.push(c.group);
    });
    return groups.reduce(function (names, group) {
      return names.concat(categories
        .filter(function (c) { return c.group === group; })
        .map(function (c) { return c.name; }));
    }, []);
  }

  // ---------- Google Forms ----------

  /* Form links live in config.json so they can be changed without touching
     code. An empty url means "not set up yet", and the GitHub links already
     in the HTML are left alone. */

  function formConfig(name) {
    var forms = (data.config && data.config.forms) || {};
    var form = forms[name];
    return (form && form.url) ? form : null;
  }

  function formUrl(form, options) {
    /* A pasted link often carries ?usp=send_form or an embedded=true left
       over from the Embed HTML tab. Strip the query and rebuild it, so the
       same URL works whether it was copied from Send or from Embed. */
    var url = form.url.split('#')[0].split('?')[0];
    var params = [];
    if (options && options.embedded) params.push('embedded=true');
    if (options && options.topic && form.topicField) {
      params.push('usp=pp_url');
      params.push(encodeURIComponent(form.topicField) + '=' +
        encodeURIComponent(options.topic));
    }
    return params.length ? url + '?' + params.join('&') : url;
  }

  /* Footer links marked data-form="…" become form links once configured. */
  function applyFormLinks() {
    document.querySelectorAll('[data-form]').forEach(function (anchor) {
      var form = formConfig(anchor.dataset.form);
      if (!form) return;
      anchor.href = formUrl(form);
      anchor.textContent = form.label || anchor.textContent;
      anchor.target = '_blank';
      anchor.rel = 'noopener';
    });
  }

  function formBlock(name, fallbackText, fallbackHref) {
    var form = formConfig(name);
    var section = node('section', { class: 'form-block' });

    if (!form) {
      section.appendChild(node('h3', { class: 'block-title', text: fallbackText }));
      section.appendChild(node('p', { class: 'form-blurb', text:
        'No form is set up for this yet, so this goes through GitHub for now.' }));
      section.appendChild(node('a', { class: 'form-open', href: fallbackHref,
        target: '_blank', rel: 'noopener', text: 'Open a GitHub issue' }));
      return section;
    }

    section.appendChild(node('h3', { class: 'block-title', text: form.label || fallbackText }));
    if (form.blurb) section.appendChild(node('p', { class: 'form-blurb', text: form.blurb }));

    /* The form is embedded, but the direct link stays: privacy extensions,
       strict browser settings and sandboxed previews all block third-party
       frames, and a blocked frame with no way out is a dead end. */
    section.appendChild(node('a', { class: 'form-open', href: formUrl(form),
      target: '_blank', rel: 'noopener',
      text: 'Open this form in a new tab' }));

    // Somewhere that cannot frame Google at all: say so instead of showing
    // the browser's own blocked-content box.
    if (!canFrameForms()) {
      section.appendChild(node('p', { class: 'form-blocked', text:
        'The form cannot be shown inside this page here, so use the link ' +
        'above. It opens in a new tab and works normally.' }));
      return section;
    }

    var frame = node('iframe', {
      class: 'form-frame',
      src: formUrl(form, { embedded: true }),
      title: form.label || fallbackText,
      loading: 'lazy'
    });
    section.appendChild(node('div', { class: 'form-frame-wrap' }, [frame]));
    return section;
  }

  /* A sandboxed preview blocks frames outright; nothing to detect, we know. */
  function canFrameForms() {
    return !ROUTED;
  }

  /* If the browser or an extension refuses the frame, the page hears about it
     through a policy violation. Swap the dead frame for the link. */
  function watchForBlockedFrames() {
    document.addEventListener('securitypolicyviolation', function (event) {
      if (String(event.blockedURI || '').indexOf('docs.google.com') === -1) return;
      document.querySelectorAll('.form-frame-wrap').forEach(function (wrap) {
        var section = wrap.parentNode;
        wrap.remove();
        if (section && !section.querySelector('.form-blocked')) {
          section.appendChild(node('p', { class: 'form-blocked', text:
            'Your browser blocked the embedded form. Use the link above; it ' +
            'opens in a new tab and works normally.' }));
        }
      });
    });
  }

  function renderForms() {
    watchForBlockedFrames();
    if (!el.forms) return;
    var issues = 'https://github.com/PamelaPajarillo/NuPaQIS-LivingReview/issues/new';
    el.forms.innerHTML = '';
    el.forms.appendChild(formBlock('suggest', 'Suggest a paper', issues));
    el.forms.appendChild(formBlock('feedback', 'Send feedback', issues));
  }

  // ---------- theme ----------

  /* No stored choice means follow the reader's system setting, which the CSS
     does on its own. A choice is remembered per browser; storage can be
     unavailable, and that must not break the page. */
  function storedTheme() {
    try {
      return localStorage.getItem('nupaqis-theme');
    } catch (error) {
      return null;
    }
  }

  function applyTheme(theme) {
    if (theme) document.documentElement.dataset.theme = theme;
    else delete document.documentElement.dataset.theme;
  }

  /* Dark is the default: only an explicit choice of light moves off it. */
  function currentlyDark() {
    return storedTheme() !== 'light';
  }

  function setupTheme() {
    applyTheme(storedTheme());

    var masthead = document.querySelector('.masthead');
    if (!masthead || document.querySelector('.theme-switch')) return;

    /* Two labelled states rather than one button whose text describes what
       will happen: at a glance you can see which mode you are in, not just
       what pressing it would do. */
    var options = [
      { mode: 'light', label: 'Light', glyph: '☀' },
      { mode: 'dark', label: 'Dark', glyph: '☾' }
    ];

    var group = node('div', {
      class: 'theme-switch', role: 'group', 'aria-label': 'Colour theme'
    });

    var buttons = {};
    function paint() {
      var dark = currentlyDark();
      options.forEach(function (option) {
        var on = (option.mode === 'dark') === dark;
        buttons[option.mode].classList.toggle('is-on', on);
        buttons[option.mode].setAttribute('aria-pressed', on ? 'true' : 'false');
      });
    }

    options.forEach(function (option) {
      var button = node('button', {
        type: 'button',
        class: 'theme-opt',
        title: option.label + ' theme'
      }, [
        node('span', { class: 'theme-glyph', 'aria-hidden': 'true', text: option.glyph }),
        node('span', { text: option.label })
      ]);
      button.addEventListener('click', function () {
        applyTheme(option.mode);
        try {
          localStorage.setItem('nupaqis-theme', option.mode);
        } catch (error) {
          // Storage can be switched off; the theme still applies to this page.
        }
        paint();
      });
      buttons[option.mode] = button;
      group.appendChild(button);
    });

    paint();
    masthead.appendChild(group);
  }

  // ---------- shared chrome ----------

  function renderNav() {
    if (!el.sitenav) return;
    var items = [
      { page: 'overview', label: 'Homepage' },
      { page: 'nupa', label: 'By NuPa topic' },
      { page: 'qis', label: 'By QIS topic' },
      { page: 'descriptions', label: 'Topic descriptions' },
      { page: 'contribute', label: 'Contribute' }
    ];
    el.sitenav.innerHTML = '';
    items.forEach(function (item) {
      var anchor = node('a', {
        href: link(item.page),
        class: item.page === PAGE ? 'is-current' : '',
        'aria-current': item.page === PAGE ? 'page' : null,
        text: item.label
      });
      if (ROUTED) {
        anchor.addEventListener('click', function (event) {
          event.preventDefault();
          go(item.page);
        });
      }
      el.sitenav.appendChild(anchor);
    });
  }

  // ---------- overview page ----------

  function renderMatrix() {
    var nupaGroups = [], qisGroups = [];
    data.categories.nupa.forEach(function (c) {
      if (nupaGroups.indexOf(c.group) === -1) nupaGroups.push(c.group);
    });
    data.categories.qis.forEach(function (c) {
      if (qisGroups.indexOf(c.group) === -1) qisGroups.push(c.group);
    });

    var tally = {}, max = 0;
    data.papers.forEach(function (paper) {
      var key = index.nupaGroup[paper.nupa_primary] + '|' + index.qisGroup[paper.qis_primary];
      tally[key] = (tally[key] || 0) + 1;
      if (tally[key] > max) max = tally[key];
    });

    var head = node('tr', {}, [node('th', { text: '' })]);
    qisGroups.forEach(function (group) {
      head.appendChild(node('th', { scope: 'col', text: group }));
    });

    var body = node('tbody');
    nupaGroups.forEach(function (rowGroup) {
      var tr = node('tr', {}, [node('th', { scope: 'row', text: rowGroup })]);
      qisGroups.forEach(function (colGroup) {
        var count = tally[rowGroup + '|' + colGroup] || 0;
        var button = node('button', {
          type: 'button', 'data-count': count,
          'aria-label': count + ' papers in ' + rowGroup + ' and ' + colGroup,
          text: count ? String(count) : '·'
        });
        if (count) {
          /* Only the strength is set here; the colour itself lives in CSS, so
             it can invert with the theme while the page is open. A cell is a
             crossing of both axes, so it is neutral: blue and green name the
             axes through the row and column headings instead. */
          var weight = 0.12 + 0.88 * Math.sqrt(count / max);
          button.style.setProperty('--weight', weight.toFixed(3));
          if (weight > 0.6) button.classList.add('is-strong');
          button.addEventListener('click', function () {
            go('nupa', '#cell=' + encodeURIComponent(rowGroup) + '|' +
               encodeURIComponent(colGroup), { cell: { nupa: rowGroup, qis: colGroup } });
          });
        } else {
          button.disabled = true;
        }
        tr.appendChild(node('td', {}, [button]));
      });
      body.appendChild(tr);
    });

    el.matrix.innerHTML = '';
    el.matrix.appendChild(node('thead', {}, [head]));
    el.matrix.appendChild(body);
  }

  function renderYearChart() {
    var counts = {};
    data.papers.forEach(function (paper) {
      if (paper.year) counts[paper.year] = (counts[paper.year] || 0) + 1;
    });
    var years = Object.keys(counts).sort();
    var max = Math.max.apply(null, years.map(function (y) { return counts[y]; }));

    var chart = node('div', { class: 'bars' });
    years.forEach(function (year) {
      // The count rides on top of its own bar, so it is inside the fill and
      // sits just above it rather than in a row along the top of the chart.
      var fill = node('span', { class: 'bar-fill' }, [
        node('span', { class: 'bar-count', text: counts[year] })
      ]);
      fill.style.height = Math.max(2, Math.round(100 * counts[year] / max)) + '%';
      var button = node('button', {
        type: 'button', class: 'bar',
        'aria-label': counts[year] + ' papers first posted in ' + year
      }, [
        node('span', { class: 'bar-track' }, [fill]),
        node('span', { class: 'bar-label', text: year })
      ]);
      button.addEventListener('click', function () {
        go('nupa', '#years=' + year, { years: new Set([year]) });
      });
      chart.appendChild(button);
    });
    el.yearChart.innerHTML = '';
    el.yearChart.appendChild(chart);
    fitYearLabels(chart);
  }

  /* Thirty-odd four-digit years will not fit on a narrow chart, and a fixed
     breakpoint guesses wrong at most widths. Measure the space each bar
     actually has and thin the labels to suit, always keeping the first and
     the last so the range stays readable. */
  function fitYearLabels(chart) {
    var bars = Array.prototype.slice.call(chart.querySelectorAll('.bar'));
    if (!bars.length) return;

    function apply() {
      // Turn the labels on their side rather than dropping any: a four-digit
      // year needs about 34px lying down but only about 10px standing up.
      var each = chart.getBoundingClientRect().width / bars.length;
      chart.classList.toggle('is-tight', each < 34);
      bars.forEach(function (bar) {
        var label = bar.querySelector('.bar-label');
        if (label) label.style.visibility = '';
      });
    }

    apply();
    if (window.ResizeObserver) {
      new ResizeObserver(apply).observe(chart);
    } else {
      window.addEventListener('resize', apply);
    }
  }

  function renderEntryGrid() {
    function column(axis, heading, blurb) {
      var counts = {};
      data.papers.forEach(function (paper) {
        paper[axis].forEach(function (name) {
          counts[name] = (counts[name] || 0) + 1;
        });
      });
      var info = axis === 'nupa' ? index.nupaInfo : index.qisInfo;
      var list = node('ul', { class: 'topic-list' });
      byGroup(data.categories[axis]).forEach(function (name) {
        var anchor = node('a', {
          href: link(axis === 'nupa' ? 'nupa' : 'qis', '#' + slug(name)),
          text: name
        });
        if (ROUTED) {
          anchor.addEventListener('click', function (event) {
            event.preventDefault();
            go(axis === 'nupa' ? 'nupa' : 'qis', '#' + slug(name), { scrollTo: slug(name) });
          });
        }

        var row = node('li', {}, [anchor]);

        /* A definition marker, not a second link: it appears only on the 34
           topics that have a description written, sits tight against the name,
           and stays muted so the row still reads as one thing. */
        if (info[name] && info[name].status === 'written') {
          var define = node('a', {
            class: 'topic-define',
            href: link('descriptions', '#' + slug(name)),
            target: '_blank', rel: 'noopener',
            title: 'Read the description of ' + name,
            'aria-label': 'Read the description of ' + name,
            text: 'Description'
          });
          if (ROUTED) {
            define.addEventListener('click', function (event) {
              event.preventDefault();
              go('descriptions', '', { scrollTo: slug(name) });
            });
          }
          row.appendChild(define);
        }

        var topicTotal = counts[name] || 0;
        row.appendChild(node('span', { class: 'topic-count',
          text: topicTotal + (topicTotal === 1 ? ' paper' : ' papers') }));
        list.appendChild(row);
      });

      var page = link(axis === 'nupa' ? 'nupa' : 'qis');
      var define = node('a', {
        class: 'entry-open entry-define',
        href: link('descriptions', '#axis-' + axis),
        text: 'Go to Topic descriptions →'
      });
      if (ROUTED) {
        define.addEventListener('click', function (event) {
          event.preventDefault();
          go('descriptions', '', { scrollTo: 'axis-' + axis });
        });
      }

      /* An arrow alone says "somewhere". The tag names the destination in the
         exact words the sidebar uses for that page, so the connection between
         this column and that nav item is explicit rather than inferred. */
      var destination = axis === 'nupa' ? 'By NuPa topic' : 'By QIS topic';
      var headingLink = node('a', {
        class: 'entry-heading-link', href: page,
        'aria-label': heading + ' — go to ' + destination
      }, [
        node('span', { text: heading }),
        node('span', { class: 'entry-dest' }, [
          node('span', { text: destination }),
          node('span', { class: 'entry-arrow', 'aria-hidden': 'true', text: '→' })
        ])
      ]);
      if (ROUTED) {
        headingLink.addEventListener('click', function (event) {
          event.preventDefault();
          go(axis === 'nupa' ? 'nupa' : 'qis');
        });
      }

      return node('section', { class: 'entry entry-' + axis }, [
        node('h4', {}, [headingLink]),
        list,
        node('div', { class: 'entry-links' }, [define])
      ]);

    }

    el.entryGrid.innerHTML = '';
    el.entryGrid.appendChild(column('nupa', 'Nuclear and Particle Physics'));
    el.entryGrid.appendChild(column('qis', 'Quantum Information Science'));
  }

  /* The PDF is a sibling of the site, not a copy of it: same YAML, typeset
     as one continuous document. Linked rather than embedded — a 371-page,
     1.3 MB file inside an iframe would download in full on every visit and
     scrolls badly on phones. */
  function renderPdfCard() {
    if (!el.pdfCard) return;
    var pdf = data.meta.pdf;
    el.pdfCard.innerHTML = '';
    if (!pdf) {
      el.pdfCard.appendChild(node('p', { class: 'hero-note', text:
        'The PDF has not been built yet. Run make to compile it.' }));
      return;
    }

    var facts = [];
    if (pdf.pages) facts.push(pdf.pages + ' pages');
    facts.push((pdf.bytes / 1e6).toFixed(1) + ' MB');
    if (pdf.compiled) facts.push('compiled ' + pdf.compiled);

    el.pdfCard.appendChild(node('div', { class: 'pdf-card' }, [
      node('div', { class: 'pdf-body' }, [
        node('h4', { text: 'NuPaQIS Living Review (PDF)' }),
        node('p', { class: 'pdf-blurb', text:
          'The whole review as one typeset document: every topic description ' +
          'and every reference, with the bibliography at the end. Useful for ' +
          'reading end to end, printing, or citing a fixed version.' }),
        node('p', { class: 'pdf-facts', text: facts.join(' · ') })
      ]),
      node('div', { class: 'pdf-actions' }, [
        node('a', { class: 'pdf-open', href: 'NUPAQIS.pdf', target: '_blank',
          rel: 'noopener', text: 'Open the PDF' }),
        node('a', { class: 'pdf-get', href: 'NUPAQIS.pdf',
          download: 'NUPAQIS.pdf', text: 'Download' })
      ])
    ]));
  }

  function renderRecent() {
    var recent = data.papers.slice().sort(function (a, b) {
      return (b.year || 0) - (a.year || 0);
    }).slice(0, 6);

    el.recent.innerHTML = '';
    recent.forEach(function (paper) {
      var card = paperCard(paper);
      // Open by default: six papers is a short list, and the point of the
      // block is to show what has arrived, not to make you click six times.
      card.open = true;
      el.recent.appendChild(card);
    });

    var toggle = document.getElementById('recent-toggle');
    if (!toggle) return;

    function anyClosed() {
      return Array.prototype.some.call(el.recent.querySelectorAll('details'),
        function (card) { return !card.open; });
    }
    function label() {
      toggle.textContent = anyClosed() ? 'Expand all' : 'Collapse all';
    }

    toggle.onclick = function () {
      var open = anyClosed();
      el.recent.querySelectorAll('details').forEach(function (card) {
        card.open = open;
      });
      label();
    };
    // Opening or closing a single card changes what the button should offer.
    el.recent.addEventListener('toggle', label, true);
    label();
  }


  // ---------- prose ----------

  /* The category descriptions are hand-written prose: paragraphs, indented
     bullet lists, bare URLs under a "References:" line, and inline $math$.
     This turns that into HTML. Math is left in place for MathJax. */

  function escapeHTML(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  /* Autolink bare URLs, but never inside a math span — a URL cannot appear
     there and $...$ often contains characters that look like punctuation. */
  function autolink(text) {
    return text.replace(/(https?:\/\/[^\s<>)]+[^\s<>).,;:])/g, function (url) {
      var label = url.replace(/^https?:\/\//, '').replace(/\/$/, '');
      if (label.length > 46) label = label.slice(0, 44) + '…';
      return '<a href="' + url + '" rel="noopener">' + label + '</a>';
    });
  }

  /* The descriptions are written for LaTeX as well as the web, so they carry
     escapes like 85\\% that mean nothing in a browser. Strip them outside
     maths, where a backslash is meaningful and MathJax needs it intact. */
  function unescapeTex(text) {
    return text.split(/(\$[^$]*\$)/).map(function (part) {
      return part.charAt(0) === '$' ? part : part.replace(/\\([%&_#])/g, '$1');
    }).join('');
  }

  function inline(text) {
    return autolink(escapeHTML(unescapeTex(text)));
  }

  function renderProse(source) {
    var wrapper = node('div', { class: 'prose' });
    if (!source) return wrapper;

    /* Work line by line rather than splitting on blank lines. A folded YAML
       scalar may separate paragraphs with a single newline or with a blank
       one, and both must read the same. A newline never falls mid-sentence
       here, because folding turns those into spaces. */
    var lines = source.split('\n');
    var list = null;

    function closeList() {
      if (list) { wrapper.appendChild(list); list = null; }
    }

    lines.forEach(function (raw) {
      var line = raw.trim();
      if (!line) return;

      if (/^[-*+]\s+/.test(line)) {
        if (!list) list = node('ul', { class: 'prose-list' });
        list.appendChild(node('li', { html: inline(line.replace(/^[-*+]\s+/, '')) }));
        return;
      }

      closeList();

      // Only a line that is nothing but "References:" is the heading.
      if (/^references:?$/i.test(line)) {
        wrapper.appendChild(node('p', { class: 'prose-refs-label', text: line }));
        return;
      }

      wrapper.appendChild(node('p', { html: inline(line) }));
    });

    closeList();
    return wrapper;
  }

  /* MathJax is loaded lazily: only pages that actually contain $...$ pay for
     it, and the script tag is added once per page load. */
  var mathPending = false;
  function typesetMath(root) {
    var hasTex = /\$[^$]+\$/.test(root.textContent || '');
    var hasMathML = !!root.querySelector('math');
    if (!hasTex && !hasMathML) return;
    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([root]).catch(function () {});
      return;
    }
    if (mathPending) return;
    mathPending = true;
    /* SVG output rather than CHTML: it draws glyphs as paths, so the math
       needs no font files of its own and cannot fall out of sync with the
       Computer Modern text around it. */
    window.MathJax = {
      tex: { inlineMath: [['$', '$']], processEscapes: true },
      svg: { fontCache: 'global', scale: 1.05 },
      options: { skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre'] },
      startup: {
        pageReady: function () {
          return window.MathJax.startup.defaultPageReady();
        }
      }
    };
    var script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-svg.js';
    script.async = true;
    document.head.appendChild(script);
  }

  // ---------- descriptions page ----------

  function renderDescriptions() {
    var written = 0, stubs = 0, words = 0;
    var query = state.query;

    el.descriptions.innerHTML = '';
    el.contents.innerHTML = '';

    [['nupa', 'Nuclear and Particle Physics'],
     ['qis', 'Quantum Information Science']].forEach(function (pair) {
      var axis = pair[0];
      var categories = byGroup(data.categories[axis]).map(function (name) {
        return (axis === 'nupa' ? index.nupaInfo : index.qisInfo)[name];
      });

      var shown = categories.filter(function (category) {
        if (!query) return true;
        return (category.name + ' ' + category.description).toLowerCase()
          .indexOf(query) !== -1;
      });
      if (!shown.length) return;

      el.descriptions.appendChild(node('h3', {
        class: 'axis-heading axis-' + axis, id: 'axis-' + axis, text: pair[1]
      }));

      var contentsGroup = node('div', { class: 'contents-group' }, [
        node('p', { class: 'contents-axis', text: pair[1] })
      ]);

      var lastGroup = null;

      shown.forEach(function (category) {
        if (category.status === 'written') { written += 1; words += category.words; }
        else { stubs += 1; }

        /* The heatmap group is the layer between an axis and its topics, the
           same grouping the sidebar filters use. */
        if (category.group !== lastGroup) {
          lastGroup = category.group;
          el.descriptions.appendChild(node('h4', {
            class: 'group-heading axis-' + axis, text: category.group
          }));
          contentsGroup.appendChild(node('p', {
            class: 'contents-group-name', text: category.group
          }));
        }

        var id = slug(category.name);
        var count = data.papers.filter(function (paper) {
          return paper[axis].indexOf(category.name) !== -1;
        }).length;

        var head = node('div', { class: 'desc-head' }, [
          node('h4', { text: category.name }),
          node('span', { class: 'desc-count',
            text: count + ' paper' + (count === 1 ? '' : 's') })
        ]);
        if (category.status === 'stub') {
          head.appendChild(node('span', { class: 'badge badge-stub', text: 'not yet written' }));
        }

        var papersLink = node('a', {
          class: 'desc-link',
          href: link(axis, '#' + axis + '=' + encodeURIComponent(category.name)),
          text: 'See the ' + count + ' paper' + (count === 1 ? '' : 's') + ' →'
        });
        if (ROUTED) {
          papersLink.addEventListener('click', function (event) {
            event.preventDefault();
            var patch = { cell: null };
            patch[axis] = new Set([category.name]);
            go(axis, '', patch);
          });
        }

        var article = node('details', { class: 'desc axis-' + axis, id: id }, [
          node('summary', { class: 'desc-summary' }, [head])
        ]);

        if (category.status === 'written') {
          article.appendChild(renderProse(category.description));
        } else {
          article.appendChild(node('p', { class: 'desc-todo', text:
            'This description has not been written yet. The papers are still ' +
            'categorised and listed.' }));
        }
        article.appendChild(papersLink);
        el.descriptions.appendChild(article);

        if (query) article.open = true;

        var jump = node('a', { href: '#' + id, text: category.name });
        jump.addEventListener('click', function () {
          var target = document.getElementById(id);
          if (target) target.open = true;
        });
        if (category.status === 'stub') jump.classList.add('is-stub');
        contentsGroup.appendChild(jump);
      });

      el.contents.appendChild(contentsGroup);
    });

    if (!el.descriptions.children.length) {
      el.descriptions.appendChild(node('p', { class: 'empty',
        text: 'No topic descriptions match that search.' }));
    }

    typesetMath(el.descriptions);
  }

  // ---------- listing pages ----------

  function facetBlock(title, kind, values, counts, groups, openByDefault) {
    var rows = [], lastGroup = null;
    values.forEach(function (value) {
      if (groups && groups[value] && groups[value] !== lastGroup) {
        lastGroup = groups[value];

        /* A checkbox for the whole area: ticked when every topic in it is
           selected, indeterminate when only some are, and it clears the area
           when you untick it. */
        var groupName = lastGroup;
        var members = values.filter(function (v) { return groups[v] === groupName; });
        var chosenHere = members.filter(function (m) { return state[kind].has(m); });

        var groupBox = node('input', {
          type: 'checkbox',
          id: kind + '-group-' + slug(groupName),
          checked: (chosenHere.length === members.length) ? 'checked' : null,
          'aria-label': 'Select all ' + members.length + ' topics in ' + groupName
        });
        groupBox.indeterminate = chosenHere.length > 0 &&
          chosenHere.length < members.length;

        groupBox.addEventListener('change', function () {
          members.forEach(function (member) {
            if (groupBox.checked) state[kind].add(member);
            else state[kind].delete(member);
          });
          render();
        });

        /* The group's own total, in the same column as the topic counts.
           Papers carrying two topics from one area are counted once. */
        var savedForGroup = state[kind];
        state[kind] = new Set(members);
        var groupTotal = data.papers.filter(matches).length;
        state[kind] = savedForGroup;

        rows.push(node('p', { class: 'facet-legend' }, [
          node('span', { text: 'Category' }),
          node('span', { class: 'facet-count', text: 'Number of papers' })
        ]));

        rows.push(node('p', { class: 'facet-group-name' }, [
          groupBox,
          node('label', { for: groupBox.id, text: groupName }),
          node('span', { class: 'facet-count', text: groupTotal })
        ]));
      }

      var id = kind + '-' + slug(value);
      var box = node('input', {
        type: 'checkbox', id: id, value: value,
        checked: state[kind].has(value) ? 'checked' : null
      });
      box.addEventListener('change', function () {
        if (box.checked) state[kind].add(value); else state[kind].delete(value);
        render();
      });
      rows.push(node('div', { class: 'facet-row' + (counts[value] ? '' : ' is-empty') }, [
        box, node('label', { for: id, text: value }),
        node('span', { class: 'facet-count', text: counts[value] })
      ]));
    });

    var clear = node('button', { class: 'facet-clear', type: 'button', text: 'clear' });
    clear.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopPropagation();
      state[kind] = new Set();
      render();
    });

    var chosen = state[kind].size;
    var summary = node('summary', { class: 'facet-head' }, [
      node('h2', { text: title }),
      node('span', { class: 'facet-chosen', text: chosen ? chosen + ' selected' : '' })
    ]);
    if (chosen) summary.appendChild(clear);

    /* Grouped facets label their columns above each area; an ungrouped one
       such as paper type needs a single legend at the top instead. */
    var head = groups ? [] : [node('p', { class: 'facet-legend' }, [
      node('span', { text: 'Type' }),
      node('span', { class: 'facet-count', text: 'Number of Papers' })
    ])];

    /* A group stays open while it has a selection, so a filter is never
       hidden inside a collapsed panel. */
    return node('details', {
      class: 'facet', open: (openByDefault || chosen) ? 'open' : null
    }, [summary, node('div', { class: 'facet-body' + (groups ? '' : ' is-flat') },
      head.concat(rows))]);
  }

  /* The year filter is a small bar chart rather than 17 checkboxes: the shape
     of the field over time is useful, and it costs a tenth of the height. */
  function yearBlock() {
    /* String(null) is "null", which is truthy, so a paper with no year used
       to slip through and became the last entry: "1988 to null". */
    var years = Array.from(new Set(data.papers.map(function (p) {
      return p.year ? String(p.year) : null;
    }))).filter(Boolean).sort();
    var counts = facetCounts('years', years);
    var max = Math.max.apply(null, years.map(function (y) { return counts[y] || 0; })) || 1;

    var bars = node('div', { class: 'year-facet' });
    years.forEach(function (year) {
      var on = state.years.has(year);
      var fill = node('span', { class: 'yf-fill' });
      fill.style.height = Math.max(3, Math.round(100 * (counts[year] || 0) / max)) + '%';
      var button = node('button', {
        type: 'button', class: 'yf' + (on ? ' is-on' : ''),
        'data-year': year, 'data-count': counts[year] || 0,
        title: year + ': ' + (counts[year] || 0) + ' papers',
        'aria-pressed': on ? 'true' : 'false',
        'aria-label': year + ', ' + (counts[year] || 0) + ' papers'
      }, [fill]);
      button.addEventListener('click', function () {
        if (on) state.years.delete(year); else state.years.add(year);
        render();
      });
      bars.appendChild(button);
    });

    var clear = node('button', { class: 'facet-clear', type: 'button', text: 'clear' });
    clear.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopPropagation();
      state.years = new Set();
      render();
    });

    var summary = node('summary', { class: 'facet-head' }, [
      node('h2', { text: 'Year' }),
      node('span', { class: 'facet-chosen',
        text: state.years.size ? state.years.size + ' selected' : '' })
    ]);
    if (state.years.size) summary.appendChild(clear);

    var range = years[0] + ' to ' + years[years.length - 1];
    var note = node('p', { class: 'facet-note', text: range });

    /* One readout under the chart beats 32 illegible ticks: point at a bar
       and it names that year and its count. */
    bars.addEventListener('mouseover', function (event) {
      var bar = event.target.closest('.yf');
      if (bar) note.textContent = bar.dataset.year + ' · ' + bar.dataset.count + ' papers';
    });
    bars.addEventListener('mouseleave', function () { note.textContent = range; });

    return node('details', { class: 'facet', open: 'open' }, [summary, bars, note]);
  }


  function renderFacets() {
    var nupaNames = byGroup(data.categories.nupa);
    var qisNames = byGroup(data.categories.qis);
    var types = Array.from(new Set(data.papers.reduce(function (all, paper) {
      return all.concat(paper.types || []);
    }, []))).sort();

    var blocks = {
      nupa: ['Nuclear and Particle Physics', 'nupa', nupaNames, index.nupaGroup],
      qis: ['Quantum Information Science', 'qis', qisNames, index.qisGroup]
    };
    // The page's own axis comes first; all four open, each capped in height.
    var order = PAGE === 'qis' ? ['qis', 'nupa'] : ['nupa', 'qis'];

    el.facets.innerHTML = '';
    order.forEach(function (key) {
      var block = blocks[key];
      el.facets.appendChild(facetBlock(block[0], block[1], block[2],
        facetCounts(block[1], block[2]), block[3], true));
    });
    el.facets.appendChild(yearBlock());
    el.facets.appendChild(facetBlock('Paper type', 'types', types,
      facetCounts('types', types), null, true));
  }

  /* A running summary of what is narrowing the list, each piece removable.
     Without it the only way back is Reset, which throws away everything. */
  function renderActiveFilters() {
    if (!el.active) return;
    el.active.innerHTML = '';
    var pieces = [];

    function add(label, value, undo) {
      pieces.push({ label: label, value: value, undo: undo });
    }
    if (state.query) {
      add('search', '“' + state.query + '”', function () {
        state.query = '';
        if (el.search) el.search.value = '';
      });
    }
    [['nupa', 'physics'], ['qis', 'quantum'], ['types', 'type']].forEach(function (pair) {
      state[pair[0]].forEach(function (value) {
        add(pair[1], value, function () { state[pair[0]].delete(value); });
      });
    });
    if (state.years.size) {
      var years = Array.from(state.years).sort();
      add('year', years.join(', '), function () { state.years = new Set(); });
    }
    if (state.cell) {
      add('crossing', state.cell.nupa + ' × ' + state.cell.qis,
        function () { state.cell = null; });
    }

    if (!pieces.length) { el.active.hidden = true; return; }
    el.active.hidden = false;
    el.active.appendChild(node('span', { class: 'active-label', text: 'Filtered by' }));
    pieces.forEach(function (piece) {
      var chip = node('button', { class: 'active-chip', type: 'button',
        'aria-label': 'Remove filter ' + piece.value }, [
        node('span', { class: 'active-kind', text: piece.label }),
        node('span', { text: piece.value }),
        node('span', { class: 'active-x', text: '×' })
      ]);
      chip.addEventListener('click', function () { piece.undo(); render(); });
      el.active.appendChild(chip);
    });
    var all = node('button', { class: 'active-clear', type: 'button', text: 'clear all' });
    all.addEventListener('click', resetAll);
    el.active.appendChild(all);
  }


  function byline(paper) {
    if (!paper.authors.length) return '';
    var first = paper.authors[0].name;
    if (paper.authors.length === 2) return first + ' and ' + paper.authors[1].name;
    if (paper.authors.length > 2) return first + ' et al.';
    return first;
  }

  function paperCard(paper) {
    var links = [];
    if (paper.arxiv_url) links.push(node('a', { href: paper.arxiv_url, text: 'arXiv:' + paper.arxiv }));
    if (paper.doi_url) links.push(node('a', { href: paper.doi_url, text: 'DOI' }));
    links.push(node('a', { href: paper.inspire_url, text: 'INSPIRE' }));
    var bib = node('button', { type: 'button', text: 'Copy BibTeX' });
    bib.addEventListener('click', function () { copy(paper.bibtex, 'BibTeX copied'); });
    links.push(bib);

    var authors = node('p', { class: 'paper-authors' });
    paper.authors.forEach(function (author, position) {
      if (position) authors.appendChild(document.createTextNode(', '));
      authors.appendChild(author.url
        ? node('a', { href: author.url, text: author.name })
        : document.createTextNode(author.name));
    });

    var facts = [];
    if (paper.posted) facts.push('Posted ' + paper.posted);
    if (paper.journal) {
      facts.push('Published in ' + paper.journal + (paper.published ? ', ' + paper.published : ''));
    }
    facts.push('Cite as ' + paper.key);

    /* Categories are labelled by axis, not only coloured: "Reviews" exists on
       both axes, so two identical chips side by side would be unreadable. */
    function chipRow(axis, label) {
      var row = node('div', { class: 'chip-row' }, [
        node('span', { class: 'chip-label', text: label })
      ]);
      paper[axis].forEach(function (name) {
        var chip = node('button', { class: 'chip ' + axis, type: 'button', text: name });
        chip.addEventListener('click', function () {
          if (PAGE === 'overview') {
            var patch = { cell: null };
            patch[axis] = new Set([name]);
            go(axis, '#' + axis + '=' + encodeURIComponent(name), patch);
          } else {
            state[axis] = new Set([name]);
            state.cell = null;
            render();
          }
        });
        row.appendChild(chip);
      });
      return row;
    }

    // Enough on the closed row to recognise a paper without opening it.
    var meta = [byline(paper), paper.journal || (paper.arxiv ? 'preprint' : '')]
      .filter(Boolean).join(' · ');

    return node('details', { class: 'paper', id: 'p-' + paper.id }, [
      node('summary', {}, [
        node('span', { class: 'paper-year', text: paper.year || '—' }),
        node('span', { class: 'paper-main' }, [
          node('span', paper.title_html
            ? { class: 'paper-title', html: paper.title_html }
            : { class: 'paper-title', text: paper.title }),
          node('span', { class: 'paper-meta', text: meta })
        ])
      ]),
      node('div', { class: 'paper-body' }, [
        authors,
        node('p', { class: 'paper-facts', text: facts.join(' · ') }),
        chipRow('nupa', 'NuPa'),
        chipRow('qis', 'QIS'),
        node('div', { class: 'paper-links' }, links)
      ])
    ]);
  }


  /* The jump bar used to be five lines of links. A select holds the same
     targets in one row and groups them by area. */
  function renderJumpbar(papers) {
    if (!el.jumpbar) return;
    var present = {};
    papers.forEach(function (paper) { present[paper[PAGE + '_primary']] = true; });

    var picker = node('select', { class: 'jump-select', 'aria-label': 'Jump to a topic' });
    picker.appendChild(node('option', { value: '', text: 'Jump to a topic…' }));

    var groups = {};
    data.categories[PAGE].forEach(function (category) {
      if (!present[category.name]) return;
      (groups[category.group] = groups[category.group] || []).push(category.name);
    });
    Object.keys(groups).forEach(function (group) {
      var optgroup = node('optgroup', { label: group });
      groups[group].forEach(function (name) {
        optgroup.appendChild(node('option', { value: slug(name), text: name }));
      });
      picker.appendChild(optgroup);
    });

    picker.addEventListener('change', function () {
      if (!picker.value) return;
      var section = document.getElementById(picker.value);
      if (section) {
        section.open = true;
        section.scrollIntoView();
      }
      picker.value = '';
    });

    el.jumpbar.innerHTML = '';
    el.jumpbar.appendChild(picker);
  }

  function renderListing() {
    var papers = selected();
    el.listing.innerHTML = '';

    el.tally.innerHTML = '';
    el.tally.appendChild(document.createTextNode('Showing '));
    el.tally.appendChild(node('strong', { text: papers.length }));
    el.tally.appendChild(document.createTextNode(
      (papers.length === data.papers.length ? '' : ' of ' + data.papers.length) +
      (papers.length === 1 ? ' paper' : ' papers')));

    renderJumpbar(papers);
    renderActiveFilters();

    if (!papers.length) {
      var reset = node('button', { type: 'button', text: 'Clear the filters' });
      reset.addEventListener('click', resetAll);
      el.listing.appendChild(node('p', { class: 'empty' }, [
        document.createTextNode('No papers match. '), reset,
        document.createTextNode(' to start again.')
      ]));
      return;
    }

    var axis = PAGE, other = axis === 'nupa' ? 'qis' : 'nupa';
    var order = byGroup(data.categories[axis]);
    var subOrder = byGroup(data.categories[other]);
    var info = axis === 'nupa' ? index.nupaInfo : index.qisInfo;

    /* A paper appears under every category it carries, as it does in the
       README: under its primary category in the body of the section, and
       under each further category as a cross-list. Without this a section's
       count disagreed with the same category's count in the sidebar. */
    var buckets = {};
    function bucket(name) {
      if (!buckets[name]) buckets[name] = { primary: [], cross: [] };
      return buckets[name];
    }
    papers.forEach(function (paper) {
      bucket(paper[axis + '_primary']).primary.push(paper);
      paper[axis].slice(1).forEach(function (name) { bucket(name).cross.push(paper); });
    });

    /* Sections are closed by default: 458 papers open at once is a 31,000px
       page. Once the list is small enough to read, they open themselves. */
    var sectionCount = Object.keys(buckets).length;
    var filtering = !!(state.query || state.cell || state.nupa.size ||
      state.qis.size || state.years.size || state.types.size);
    // Closed is for browsing the whole review; once you have narrowed it,
    // seeing 22 shut headings instead of your results is no help.
    var openAll = filtering || papers.length <= 40 || sectionCount === 1;

    order.forEach(function (name) {
      var entry = buckets[name];
      if (!entry) return;
      var group = entry.primary;
      var total = entry.primary.length + entry.cross.length;

      var about = node('a', {
        class: 'section-about', href: link('descriptions', '#' + slug(name)),
        target: '_blank', rel: 'noopener',
        text: (info[name] && info[name].status === 'written') ? 'Description' : null
      });
      if (about.textContent) {
        about.addEventListener('click', function (event) {
          event.stopPropagation();
          if (ROUTED) {
            event.preventDefault();
            go('descriptions', '', { scrollTo: slug(name) });
          }
        });
      }

      var permalink = node('a', {
        class: 'section-link', href: '#' + slug(name), text: 'Permalink'
      });
      permalink.addEventListener('click', function (event) { event.stopPropagation(); });

      // With a topicField configured, each topic gets its own feedback link,
      // arriving at the form with the topic already filled in.
      var feedback = formConfig('feedback');
      var feedbackLink = null;
      if (feedback && feedback.topicField) {
        feedbackLink = node('a', {
          class: 'section-link',
          href: formUrl(feedback, { topic: name }),
          target: '_blank', rel: 'noopener', text: 'feedback'
        });
        feedbackLink.addEventListener('click', function (event) { event.stopPropagation(); });
      }

      var section = node('details', {
        class: 'section axis-' + axis, id: slug(name), open: openAll ? 'open' : null
      }, [
        node('summary', { class: 'section-head' }, [
          node('h2', { text: name }),
          node('span', { class: 'section-count',
            text: total + (total === 1 ? ' paper' : ' papers') }),
          node('span', { class: 'section-tools' },
            feedbackLink ? [about, feedbackLink, permalink] : [about, permalink])
        ])
      ]);

      var subBuckets = {};
      group.forEach(function (paper) {
        var key = paper[other + '_primary'];
        (subBuckets[key] = subBuckets[key] || []).push(paper);
      });
      var subNames = subOrder.filter(function (n) { return subBuckets[n]; });

      subNames.forEach(function (subName) {
        // A lone subheading, or one repeating the section's own name, is noise.
        if ((subNames.length > 1 || entry.cross.length) && subName !== name) {
          section.appendChild(node('h3', { class: 'subsection', text: subName }));
        }
        subBuckets[subName].forEach(function (paper) {
          section.appendChild(paperCard(paper));
        });
      });

      if (entry.cross.length) {
        section.appendChild(node('h3', { class: 'subsection is-cross',
          text: 'Cross-listed (' + entry.cross.length + ')' }));
        entry.cross.forEach(function (paper) {
          section.appendChild(paperCard(paper));
        });
      }

      el.listing.appendChild(section);
    });

    typesetMath(el.listing);
  }


  // ---------- state in the URL ----------

  function writeHash() {
    if (ROUTED) return;
    var parts = [];
    if (state.query) parts.push('q=' + encodeURIComponent(state.query));
    ['nupa', 'qis', 'years', 'types'].forEach(function (axis) {
      if (state[axis].size) {
        parts.push(axis + '=' + Array.from(state[axis]).map(encodeURIComponent).join('|'));
      }
    });
    if (state.cell) {
      parts.push('cell=' + encodeURIComponent(state.cell.nupa) + '|' +
        encodeURIComponent(state.cell.qis));
    }
    history.replaceState(null, '', parts.length ? '#' + parts.join('&') : location.pathname);
  }

  function readHash() {
    var hash = location.hash.replace(/^#/, '');
    if (!hash || hash.indexOf('=') === -1) return;
    hash.split('&').forEach(function (part) {
      var split = part.indexOf('=');
      var key = part.slice(0, split), value = part.slice(split + 1);
      if (key === 'q') state.query = decodeURIComponent(value).toLowerCase();
      else if (key === 'cell') {
        var halves = value.split('|');
        state.cell = { nupa: decodeURIComponent(halves[0]), qis: decodeURIComponent(halves[1]) };
      } else if (state[key] instanceof Set) {
        state[key] = new Set(value.split('|').map(decodeURIComponent));
      }
    });
  }

  function resetAll() {
    state = blankState();
    if (el.search) el.search.value = '';
    render();
  }

  function render() {
    if (PAGE === 'contribute') {
      renderForms();
      return;
    }
    if (PAGE === 'descriptions') {
      renderDescriptions();
      return;
    }
    if (PAGE === 'overview') {
      renderMatrix();
      renderYearChart();
      renderEntryGrid();
      renderPdfCard();
      renderRecent();
      return;
    }
    renderFacets();
    renderListing();
    writeHash();
  }

  // ---------- boot ----------

  function cacheElements() {
    el = {
      sitenav: document.getElementById('sitenav'),
      facets: document.getElementById('facets'),
      listing: document.getElementById('listing'),
      tally: document.getElementById('tally'),
      search: document.getElementById('search'),
      matrix: document.getElementById('matrix'),
      yearChart: document.getElementById('year-chart'),
      entryGrid: document.getElementById('entry-grid'),
      recent: document.getElementById('recent'),
      pdfCard: document.getElementById('pdf-card'),
      forms: document.getElementById('forms'),
      jumpbar: document.getElementById('jumpbar'),
      active: document.getElementById('active-filters'),
      descriptions: document.getElementById('descriptions'),
      contents: document.getElementById('contents'),
      meta: document.getElementById('masthead-meta'),
      toast: document.getElementById('toast')
    };
  }

  function wire() {
    if (el.search) {
      el.search.addEventListener('input', function () {
        state.query = el.search.value.trim().toLowerCase();
        if (PAGE === 'descriptions') renderDescriptions();
        else renderListing();
        writeHash();
      });
    }
    function on(id, handler) {
      var button = document.getElementById(id);
      if (button) button.addEventListener('click', handler);
    }
    on('expand-all', function () {
      var host = el.listing || el.descriptions;
      if (host) host.querySelectorAll('.section, .desc').forEach(function (d) { d.open = true; });
    });
    on('collapse-all', function () {
      var host = el.listing || el.descriptions;
      if (host) {
        host.querySelectorAll('details').forEach(function (d) { d.open = false; });
      }
    });
    on('download-bib', function () {
      var papers = selected();
      if (!papers.length) return toast('Nothing selected to download');
      download('nupaqis-selection.bib',
        papers.map(function (p) { return p.bibtex; }).join('\n\n') + '\n');
      toast(papers.length + ' entries downloaded');
    });
    on('copy-keys', function () {
      var papers = selected();
      if (!papers.length) return toast('Nothing selected to copy');
      copy('\\cite{' + papers.map(function (p) { return p.key; }).join(',') + '}',
        papers.length + ' keys copied');
    });
    on('reset', resetAll);
    on('drawer-toggle', function () {
      var drawer = document.getElementById('drawer-toggle');
      var open = document.getElementById('sidebar').classList.toggle('is-open');
      drawer.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  function buildIndex() {
    index = { nupaGroup: {}, qisGroup: {}, nupaInfo: {}, qisInfo: {} };
    data.categories.nupa.forEach(function (c) {
      index.nupaGroup[c.name] = c.group;
      index.nupaInfo[c.name] = c;
    });
    data.categories.qis.forEach(function (c) {
      index.qisGroup[c.name] = c.group;
      index.qisInfo[c.name] = c;
    });
  }

  function start(patch) {
    PAGE = document.body.dataset.page;
    cacheElements();
    state = blankState();
    if (patch) {
      Object.keys(patch).forEach(function (key) {
        if (key !== 'scrollTo') state[key] = patch[key];
      });
    } else {
      readHash();
    }
    if (el.search) el.search.value = state.query;
    if (el.meta) {
      el.meta.textContent = data.meta.count + ' papers · updated ' + data.meta.generated;
    }
    setupTheme();
    renderNav();
    applyFormLinks();
    wire();
    render();

    var raw = location.hash.replace(/^#/, '');
    if (raw.indexOf('=') !== -1 || raw.charAt(0) === '/') raw = '';
    var target = (patch && patch.scrollTo) || raw;
    if (target) {
      var section = document.getElementById(target);
      if (section) {
        if (section.tagName === 'DETAILS') section.open = true;
        section.scrollIntoView();
      }
    } else {
      window.scrollTo(0, 0);
    }
  }

  window.__NUPAQIS_START__ = start;

  function loadData() {
    if (window.__NUPAQIS__) {
      return Promise.resolve([window.__NUPAQIS__.papers,
        window.__NUPAQIS__.categories, window.__NUPAQIS__.config || {}]);
    }
    return Promise.all([
      fetch('data/papers.json').then(function (r) { return r.json(); }),
      fetch('data/categories.json').then(function (r) { return r.json(); }),
      // A missing or broken config must not take the site down with it.
      fetch('config.json').then(function (r) { return r.json(); })
        .catch(function () { return {}; })
    ]);
  }

  loadData().then(function (results) {
    data = { papers: results[0].papers, meta: results[0], categories: results[1],
             config: results[2] || {} };
    buildIndex();
    start();
  }).catch(function (error) {
    var host = document.getElementById('listing') || document.querySelector('.canvas');
    if (host) {
      host.innerHTML = '';
      host.appendChild(node('p', { class: 'empty',
        text: 'The paper data did not load. Run make_web.py, then reload.' }));
    }
    console.error(error);
  });
})();