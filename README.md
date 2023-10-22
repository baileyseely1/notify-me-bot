# notify-me-bot
## A discord bot made in python that has commands that allow you to track a users messages or voice channel activity.
### It was made for personal use so there would be problems with scalability if it had a large user base (the tracked user data is stored in a pickle file and not an external DB)
### I currently have it running in a AWS EC2 Ubuntu instance.

# Requirements
## pip3 install discord.py is the only external library you need.

# Setup
## You will need to create your own discord bot https://discord.com/developers/docs/intro and provide the token key at the bottom of the notifyme.py file in bot.run()

# Virtual Environment
## if you aren't familiar with python you will need a venv. 
## it can be created in the terminal with the command python -m venv venv
## activate the venv using the command venv/Scripts/activate on windows and source venv/bin/activate on mac/linux




