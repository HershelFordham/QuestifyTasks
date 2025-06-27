# QuestifyTasks

QuestifyTasks is a simple command-line prototype of a gamified to-do list. Tasks are represented as monsters that can be defeated to collect armor pieces and earn titles.

## Features

- Weekly map with days of the week.
- Tasks assigned to monsters; completing a task "defeats" the monster.
- Armor collection system for completed tasks.
- Title progression for each monster type based on total kills.
- Weekly boss battle probability based on the percentage of completed tasks.

Run the application with:

```bash
python3 questify.py
```

All progress is stored in `game_data.json` (ignored in version control).
