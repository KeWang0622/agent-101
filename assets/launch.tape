# agent-101 launch demo · 1200x700 · Catppuccin Mocha · JetBrains Mono
# Run: vhs assets/launch.tape  →  assets/launch.gif
#
# Captures: prompt → tool calls render with ● → diff → bash result → done
# Targets ~12 seconds, optimized for autoplay on Twitter/X.

Output assets/launch.gif

Set Shell        "bash"
Set FontFamily   "JetBrains Mono"
Set FontSize     16
Set Width        1200
Set Height       700
Set Theme        "Catppuccin Mocha"
Set TypingSpeed  35ms
Set PlaybackSpeed 1.0
Set Padding      24
Set BorderRadius 8
Set WindowBar    Colorful
Set CursorBlink  true

# clear before recording
Hide
Type "clear" Enter
Type "cd ~/agent-101" Enter
Show

Sleep 600ms
Type "python agent.py" Enter
Sleep 1500ms

Type "add a hello() function to src/main.py and run it"
Sleep 600ms
Enter
Sleep 2s

# wait for the agent's output to land. Wait+Line tracks real model latency.
Wait+Line /●\s*Read/  Timeout 25s
Sleep 800ms

Wait+Line /●\s*Edit/  Timeout 25s
Sleep 1000ms

Wait+Line /allow Bash/  Timeout 15s
Sleep 600ms
Type "y" Enter

Wait+Line /hello/  Timeout 15s
Sleep 1500ms

# graceful exit so the GIF ends cleanly
Ctrl+D
Sleep 800ms
