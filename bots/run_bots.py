import subprocess

bots = [
    "python bots/bot.py",
    "python bots/spamer.py",
    "python bots/anuncios.py",
    "python bots/carobot.py"
]

processes = [subprocess.Popen(bot, shell=True) for bot in bots]

for process in processes:
    process.wait()