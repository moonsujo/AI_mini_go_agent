# artificial intelligence GO agent
minimax, alpha-beta pruning agent plays Go on a 5x5 board against another agent. It displays the result after two games.

wins >= 80% against a random player, a greedy player (tries to make a capture on every move), and an aggressive player (looks two moves ahead while trying to capture the most pieces).

evaluation function:
-placing pieces that are connected
-placing them in the center (the middle 3x3 section)
-capturing enemy stones
-acquiring two-eyes.
