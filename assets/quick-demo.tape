# Quick demo GIF — no API key needed.
Output assets/quick-demo.gif

Set Shell        "zsh"
Set FontFamily   "JetBrains Mono"
Set FontSize     16
Set Width        1200
Set Height       620
Set Theme        "Catppuccin Mocha"
Set TypingSpeed  35ms
Set PlaybackSpeed 1.0
Set Padding      24
Set BorderRadius 8
Set WindowBar    Colorful

Sleep 1500ms

Type "cd ~/agent-101"
Sleep 200ms
Enter
Sleep 800ms

Type "# the entire agent loop, in 6 lines:"
Sleep 200ms
Enter
Sleep 600ms

Type "sed -n '102,116p' chapters/ch05_the_loop.py"
Sleep 200ms
Enter
Sleep 5000ms

Type "clear"
Sleep 100ms
Enter
Sleep 400ms

Type "# 42 tests, no API key, 0.5 seconds:"
Sleep 200ms
Enter
Sleep 500ms

Type "pytest tests/ -q 2>&1 | tail -3"
Sleep 200ms
Enter
Sleep 4000ms

Type "clear"
Sleep 100ms
Enter
Sleep 400ms

Type "# the climax — Claude-Code-shaped CLI in 839 lines:"
Sleep 200ms
Enter
Sleep 500ms

Type "wc -l agent.py | xargs printf '%s\\n'"
Sleep 200ms
Enter
Sleep 3000ms
