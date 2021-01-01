# Stock Trading Bot

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FDMinghao%2FStock_Trading_Bot&count_bg=%23F81C1C&title_bg=%231E2330&icon=skyliner.svg&icon_color=%23F81C1C&title=Repo+View+Count&edge_flat=false)](https://hits.seeyoufarm.com)

## **WORK IN PROGRESS...**

## Getting Started 

1. Initiate virtual environment 
   - create virtual env
      ```bash 
      $ python -m venv venv
      ```
   - run virtual env
     - Windows
       ```bash
       $ venv\Scripts\activate.bat
       ```
     - Mac / Linux
       ```bash
       $ source venv/bin/activate
       ```
   - exit virtual env
       ```bash 
       $ deactivate 
       ```

2. Install Requirements 
    ```bash
    $ pip install -r requirements.txt
    $ pip install -g .
    ```
3. Rename [`.env copy`](config/.env%20copy) in the `./config` folder to `.env` 
4. Insert `Alpaca API Key` and `Alpaca Secret Key`
5. Test run [`longshort.py`](lab/longshort.py) in the lab folder
6. Have fun


