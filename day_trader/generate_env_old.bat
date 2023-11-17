echo install virtualenv
call pip install virtualenv

echo Create new virtual environment
call virtualenv venv

echo activate current environment
call .\venv\Scripts\activate

echo Install all modules from requirements file
call pip install -r requirements.txt

echo Install Bloomberg lib
call python -m pip install --index-url=https://bloomberg.bintray.com/pip/simple blpapi==3.14.0