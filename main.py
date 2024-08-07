import curses
import time
import json
from datetime import datetime

# Load highscores from file
def load_highscores(filename='highscores.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save highscores to file
def save_highscores(highscores, filename='highscores.json'):
    with open(filename, 'w') as file:
        json.dump(highscores, file, indent=4)

def update_highscores(highscores, score):
    highscores.append(score)
    highscores = sorted(highscores, key=lambda x: abs(x['difference']))
    if len(highscores) > 10:
        highscores = highscores[:10]
    save_highscores(highscores)
    return highscores

def main(stdscr):
    # Setup
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    # Highscores
    highscores = load_highscores()

    # Main loop
    mode = 0
    last_press = 0
    goal_time = 0
    start_time = 0
    is_counting = False
    goal_set = False
    times = []
    result_displayed = False
    last_result = None

    while True:
        stdscr.clear()
        
        if mode == 0:  # Main menu
            stdscr.addstr(0, 0, "Main Menu")
            stdscr.addstr(2, 0, "1 - Mode 1")
            stdscr.addstr(3, 0, "2 - Mode 2")
            stdscr.addstr(4, 0, "3 - Highscores")
            stdscr.addstr(6, 0, "Press ESC to quit")
        
        elif mode == 1:  # Mode 1
            stdscr.addstr(0, 0, "Mode 1: Press SPACE to measure time between presses")
            stdscr.addstr(2, 0, "Press ESC to return to main menu")
            if times:
                stdscr.addstr(4, 0, "Last 10 times:")
                for idx, t in enumerate(times):
                    stdscr.addstr(5 + idx, 0, f"{idx + 1}. {t:.3f} seconds")
            
        elif mode == 2:  # Mode 2
            if not goal_set:
                stdscr.addstr(0, 0, "Mode 2: Input goal time in seconds and press ENTER")
                stdscr.addstr(2, 0, "Goal time (seconds): " + str(goal_time))
            elif not is_counting:
                if last_result:
                    stdscr.addstr(0, 0, "Mode 2: Press SPACE to start again")
                    stdscr.addstr(2, 0, f"Goal time: {goal_time:.3f} seconds")
                    stdscr.addstr(4, 0, f"Stopped time: {last_result['time']:.3f} seconds")
                    stdscr.addstr(5, 0, f"Difference to goal: {last_result['difference']:.3f} seconds")
                else:
                    stdscr.addstr(0, 0, "Mode 2: Press SPACE to start")
                    stdscr.addstr(2, 0, f"Goal time: {goal_time:.3f} seconds")
            else:
                elapsed_time = time.time() - start_time
                countdown = 3 - elapsed_time
                if countdown > 0:
                    stdscr.addstr(0, 0, "Mode 2: Press SPACE to stop the timer")
                    stdscr.addstr(2, 0, f"Goal time: {goal_time:.3f} seconds")
                    stdscr.addstr(4, 0, f"Countdown: {int(countdown)}")
                else:
                    stdscr.addstr(0, 0, "Mode 2: Press SPACE to stop the timer")
                    stdscr.addstr(2, 0, f"Goal time: {goal_time:.3f} seconds")
                    stdscr.addstr(4, 0, f"Countdown: GO!")

        elif mode == 3:  # Highscores
            stdscr.addstr(0, 0, "Highscores (Mode 2)")
            if highscores:
                for idx, score in enumerate(highscores[:10]):
                    stdscr.addstr(idx+2, 0, f"{idx+1}. {score['date']} - Goal: {score['goal']:.3f}s, Time: {score['time']:.3f}s, Diff: {score['difference']:.3f}s")
                avg_diff = sum(score['difference'] for score in highscores) / len(highscores)
                stdscr.addstr(13, 0, f"Average difference: {avg_diff:.3f}s")
            else:
                stdscr.addstr(2, 0, "No scores available.")
            stdscr.addstr(15, 0, "Press ESC to return to main menu")
        
        # Get user input
        key = stdscr.getch()

        if key == 27:  # ESC key
            if mode != 0:
                mode = 0
                times.clear()  # Clear the times when returning to the main menu
                goal_set = False
                last_result = None
            else:
                break
        
        if mode == 0:
            if key == ord('1'):
                mode = 1
            elif key == ord('2'):
                mode = 2
            elif key == ord('3'):
                mode = 3
        
        elif mode == 1:
            if key == ord(' '):
                current_time = time.time()
                if last_press:
                    elapsed = current_time - last_press
                    times.append(elapsed)
                    if len(times) > 10:
                        times.pop(0)
                last_press = current_time
        
        elif mode == 2:
            if not goal_set:
                if key == ord('\n'):
                    goal_set = True
                    result_displayed = False
                elif key in range(48, 58):
                    goal_time = goal_time * 10 + (key - 48)
            else:
                if not is_counting:
                    if key == ord(' '):
                        start_time = time.time()
                        is_counting = True
                        result_displayed = False
                else:
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= 3:
                        if key == ord(' '):
                            stop_time = time.time()
                            difference = stop_time - start_time - goal_time - 3  # Adjust for countdown
                            last_result = {
                                'time': stop_time - start_time - 3,  # Adjust for countdown
                                'difference': difference
                            }
                            stdscr.addstr(6, 0, f"Stopped time: {last_result['time']:.3f} seconds")
                            stdscr.addstr(7, 0, f"Difference to goal: {last_result['difference']:.3f} seconds")
                            highscores = update_highscores(highscores, {
                                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'goal': goal_time,
                                'time': last_result['time'],
                                'difference': last_result['difference']
                            })
                            is_counting = False
                            result_displayed = True
        
        elif mode == 3:
            if key == 27:  # ESC key
                mode = 0

        stdscr.refresh()

# Run the program
curses.wrapper(main)
