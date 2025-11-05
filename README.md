# BlockBlast Bot (MVP)

This is a **quick-and-dirty bot** I wrote in just **two days** (because of a bet).  
It plays the mobile game **BlockBlast** automatically by detecting the screen, recognizing pieces, and moving them with the mouse.
(You need to connect your phone to PC with android devtools)

⚠️ **Disclaimer:**  
- This is just a **working MVP**, not a polished project.  
- There’s a **lot of hardcoded stuff** (coordinates, timings, figure positions).  
- There’s **no `requirements.txt`** (I was too lazy to make one).  
- One day I might clean it up and make it nice — but for now it just works.

---

## Features
- Captures the game field using `pyscreenshot`
- Detects current pieces and possible placements
- Finds the **best move(s)** using recursive search
- Moves pieces automatically using the `mouse` library
- Logs debug info (see `debug_logger.py`)
- Plays warning beeps when no moves are available

---

## Structure
- `main.py` — the entry point, runs the loop (read game state → find move → play move).  
- `mouse_control.py` — handles mouse dragging for placing figures.  
- `debug_logger.py` — simple file logger with rotating filenames.  
- `figures_starts.json` — hardcoded starting positions of figures (yes, really).

---

## Usage
This bot was written for **my machine, my screen size, and my setup**.  
If you want to run it:
1. Install dependencies (manually):
   - `numpy`
   - `pyscreenshot`
   - `keyboard`
   - `mouse`
   - `winsound` (Windows only, built-in)
2. Run:
   ```bash
   python main.py
   ```
   
3. Keep BlockBlast open and let the bot do its thing.
(You may need to adjust hardcoded coordinates in mouse_control.py and main.py for your screen.)

## Limitations

- Hardcoded screen coordinates everywhere.
- Works only on Windows (because of winsound + my setup).
- No configuration, no error handling, no cross-platform support.
- Definitely not production-ready.

## Status

- ✅ Works on my machine
- 🚧 Needs cleanup, refactoring, and general improvements

## License

Do whatever you want with this. Just know it’s messy MVP code.

