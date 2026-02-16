/**
 * Minimal JSON viewer with syntax highlighting and collapse/expand.
 */
function initJsonViewer(el) {
    const raw = el.getAttribute('data-json') || el.textContent;
    try {
        const parsed = JSON.parse(raw);
        el.innerHTML = '';
        el.appendChild(renderJson(parsed));
    } catch {
        // Not valid JSON, leave as plain text
    }
}

function renderJson(value, indent) {
    indent = indent || 0;
    if (value === null) return span('null', 'json-null');
    if (typeof value === 'boolean') return span(String(value), 'json-boolean');
    if (typeof value === 'number') return span(String(value), 'json-number');
    if (typeof value === 'string') return span('"' + escapeHtml(value) + '"', 'json-string');

    if (Array.isArray(value)) {
        if (value.length === 0) return document.createTextNode('[]');
        return renderCollection(value, '[', ']', indent, function(item, i) {
            return renderJson(item, indent + 1);
        });
    }

    if (typeof value === 'object') {
        var keys = Object.keys(value);
        if (keys.length === 0) return document.createTextNode('{}');
        return renderCollection(keys, '{', '}', indent, function(key) {
            var frag = document.createDocumentFragment();
            frag.appendChild(span('"' + escapeHtml(key) + '"', 'json-key'));
            frag.appendChild(document.createTextNode(': '));
            frag.appendChild(renderJson(value[key], indent + 1));
            return frag;
        });
    }

    return document.createTextNode(String(value));
}

function renderCollection(items, open, close, indent, renderItem) {
    var container = document.createDocumentFragment();
    var toggle = document.createElement('span');
    toggle.className = 'json-toggle';
    toggle.textContent = open;
    container.appendChild(toggle);

    var content = document.createElement('span');
    content.className = 'json-collapsible';

    var pad = '  '.repeat(indent + 1);
    var closePad = '  '.repeat(indent);

    for (var i = 0; i < items.length; i++) {
        content.appendChild(document.createTextNode('\n' + pad));
        content.appendChild(renderItem(items[i], i));
        if (i < items.length - 1) content.appendChild(document.createTextNode(','));
    }

    content.appendChild(document.createTextNode('\n' + closePad));
    container.appendChild(content);
    container.appendChild(document.createTextNode(close));

    var summary = document.createTextNode(' /* ' + items.length + ' items */ ' + close);
    summary.className = 'json-summary';

    toggle.addEventListener('click', function() {
        toggle.classList.toggle('collapsed');
        content.classList.toggle('hidden');
    });

    return container;
}

function span(text, cls) {
    var el = document.createElement('span');
    el.className = cls;
    el.textContent = text;
    return el;
}

function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
