# Artha - Personal Finance Tool

This tool helps in giving a single point view of all your daily transactions and mutual fund transactions. Past data for daily transactions can be uploaded via an excel file and for the mutual fund transactions, a Consolidated Account Statement can be used.

The tool also provides analysis and trends in above mentioned financial transactions.

## Installation

1. Clone the repo

        https://github.com/RohithBhandaru/Artha.git

2. Initiate SQLAlchemy DB

        flask db init
        flask db migrate -m "Initial migration"
        flask db upgrade

3. Install MongoDB Community Edition
4. Create "user-content" folder in appDir and place your historical daily transactions excel file and CAS pdf in this folder
5. Daily transactions data is to be in the following format
6. Run the DataPop_MDB_DailyTxns.py and DataPop_MDB_MFTxns.py to populate MongoDB
7. Run the flask application and register yourself as a user
8. Voila! You'll a screen like this 