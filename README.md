# Wattpad Backup Utility

A python script that automatically downloads and organizes all the stories an account has added to their library.

I wrote this because I have an ~~ir~~rational fear of my favorite stories being deleted forever.

A lot of stuff in this is from https://github.com/TheOnlyWayUp/WattpadDownloader

### Usage:
*Tested using Python 3.12.*

Using a virtual environment is recommended **(optional)**:
```
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```
pip install -r requirements.txt
```

Create a `.env` and fill in fields:
```
cp .env_template .env
nano .env
```

Run script:
```
python3 src/main.py
```