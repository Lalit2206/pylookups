# Playground

Try pylookups **right here in your browser** — nothing to install. Edit
the code and press Run.

!!! note
    The first visit downloads the Python runtime (~10 MB), so give it a
    few seconds. After that, everything runs instantly on your machine.

<textarea id="pg-code" spellcheck="false" style="width:100%;min-height:280px;font-family:var(--md-code-font-family,monospace);font-size:0.8rem;padding:0.8em;border-radius:0.2rem;border:1px solid var(--md-default-fg-color--lightest);background:var(--md-code-bg-color);color:var(--md-code-fg-color);resize:vertical;">
from pylookup import xlookup, vlookup, filter, unique, sort

table = [
    ["id", "name", "score"],
    [1, "alice", 90],
    [2, "bob", 75],
    [3, "carol", 60],
]

print(vlookup(2, table, 2))
print(xlookup(3, [1, 2, 3], ["a", "b", "c"]))
print(filter([1, 2, 3, 4, 5], lambda x: x % 2 == 0))
print(unique([1, 1, 2, 3, 3]))
print(sort(table[1:], by=3, reverse=True))
</textarea>

<p>
<button id="pg-run" class="md-button md-button--primary">▶ Run</button>
<span id="pg-status" style="margin-left:0.8em;font-size:0.75rem;opacity:0.8;"></span>
</p>

<pre id="pg-output" style="min-height:6em;padding:0.8em;border-radius:0.2rem;background:var(--md-code-bg-color);white-space:pre-wrap;">Output will appear here.</pre>

<script src="https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js"></script>
<script src="../js/playground.js"></script>
