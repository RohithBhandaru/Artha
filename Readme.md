# Artha - Personal Finance Tool

This tool helps in giving a single point view of all your daily transactions and mutual fund transactions. Past data for daily transactions can be uploaded via an excel file and for the mutual fund transactions, a Consolidated Account Statement can be used.

The tool also provides analysis and trends in above mentioned financial transactions.

## Installation

1. Clone the repo

        https://github.com/RohithBhandaru/Artha.git

2. Create a virtual environment and install requirements

3. Initiate SQLAlchemy DB and run following commands

        flask db init
        flask db migrate -m "Initial migration"
        flask db upgrade

4. Install MongoDB Community Edition
5. Create "user-content" folder in appDir and place your historical daily transactions excel file and CAS pdf in this folder
6. Daily transactions data is to be in the following format
<img width="1334" alt="Screenshot 2021-02-27 at 12 04 02 PM" src="https://user-images.githubusercontent.com/20087190/109378147-29974700-78f6-11eb-80de-470323ae8d46.png">

7. Run the DataPop_MDB_DailyTxns.py and DataPop_MDB_MFTxns.py to populate MongoDB
8. Run the flask application and register yourself as a user
9. Voila! You'll see a screen like this 
<img width="1381" alt="Screenshot 2021-02-27 at 12 21 13 PM" src="https://user-images.githubusercontent.com/20087190/109378165-53506e00-78f6-11eb-92a8-49098b96d722.png">
