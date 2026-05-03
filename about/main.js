// Typewriter effect for the terminal hero
const lines = [
  '$ python agent.py "build me a todo app"',
  '',
  '● Read   AGENT.md',
  '● Bash   mkdir todo-app',
  '● Write  todo-app/index.html',
  '● Write  todo-app/style.css',
  '',
  '✔ Done — opened in your browser.',
];

const el = document.getElementById('typewriter');
let lineIdx = 0, charIdx = 0;
let cursor;

function addCursor() {
  cursor = document.createElement('span');
  cursor.className = 'cursor';
  cursor.textContent = ' ';
  el.appendChild(cursor);
}

function removeCursor() {
  if (cursor && cursor.parentNode) cursor.parentNode.removeChild(cursor);
}

function type() {
  if (lineIdx >= lines.length) {
    addCursor(); // blinking cursor at end
    return;
  }

  const line = lines[lineIdx];

  if (charIdx < line.length) {
    removeCursor();
    el.textContent += line[charIdx];
    charIdx++;
    addCursor();
    setTimeout(type, charIdx === 1 && line.startsWith('$') ? 120 : 28);
  } else {
    // end of line — move to next
    removeCursor();
    el.textContent += '\n';
    lineIdx++;
    charIdx = 0;
    // pause between lines
    setTimeout(type, lineIdx < lines.length && lines[lineIdx] === '' ? 60 : 180);
  }
}

// Start after a short delay
window.addEventListener('DOMContentLoaded', () => {
  setTimeout(type, 600);
});
