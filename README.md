# THIS REPOSITORY HAS BEEN ARCHIVED AFTER SUCCESSFUL COMPLETION OF THS PROJECT

# Local Instance Instructions

1) Open Visual Studio Code
2) Open a new terminal, and run the following command. When prompted, open the cloned repository:
```
git clone https://github.com/MAHA-Software-Engineering/MAHA-Insurance-Calculator-Backend.git
```
3) Initialize and activate a virutal environment using the following commands appropriate to your OS:
```
# Linux
sudo apt-get install python3-venv    # If needed
python3 -m venv .venv
source .venv/bin/activate

# macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\scripts\activate
```
4) Install project dependencies using the following command:
```
pip install -r requirements.txt
```
5) Make your .env. These are the required variables:
```
db = ""
host = ""
password = ""
user = ""
```
 6) All Python code should work as needed.
