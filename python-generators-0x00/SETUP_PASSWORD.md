# Setting Up MySQL Password for seed.py

## Issue
MySQL was installed with a password for the root user, but `seed.py` is configured with an empty password.

## Solution Options

### Option 1: Update seed.py with Your Password (Recommended)

1. Open `seed.py` in your editor

2. Find the `connect_db()` function (around line 22-26) and update:
   ```python
   connection = mysql.connector.connect(
       host='localhost',
       user='root',
        password='YOUR_PASSWORD_HERE',  # Add your MySQL root password
       port=3306
   )
   ```

3. Find the `connect_to_prodev()` function (around line 59-64) and update:
   ```python
   connection = mysql.connector.connect(
       host='localhost',
       user='root',
        password='YOUR_PASSWORD_HERE',  # Add your MySQL root password
       database='ALX_prodev',
       port=3306
   )
   ```

4. Save the file

### Option 2: Reset MySQL Root Password to Empty

If you want to use an empty password for development:

1. Open Command Prompt as Administrator

2. Stop MySQL service:
   ```cmd
   net stop MySQL80
   ```

3. Start MySQL in safe mode (skip grant tables):
   ```cmd
   cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
   mysqld --skip-grant-tables --skip-networking
   ```
   (Leave this window open)

4. Open a new Command Prompt window and connect:
   ```cmd
   cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
   mysql -u root
   ```

5. In MySQL prompt, run:
   ```sql
   USE mysql;
   UPDATE user SET authentication_string='' WHERE User='root';
   FLUSH PRIVILEGES;
   EXIT;
   ```

6. Stop the mysqld process (Ctrl+C in the first window)

7. Start MySQL service normally:
   ```cmd
   net start MySQL80
   ```

### Option 3: Use Environment Variables (Most Secure)

1. Create a `.env` file in `python-generators-0x00/`:
   ```
   MYSQL_PASSWORD=your_password_here
   ```

2. Install python-decouple:
   ```cmd
   pip install python-decouple
   ```

3. Update `seed.py` to read from environment:
   ```python
   from decouple import config
   
   # In connect_db():
   password = config('MYSQL_PASSWORD', default='')
   
   # In connect_to_prodev():
   password = config('MYSQL_PASSWORD', default='')
   ```

## Quick Test

Run the test script to verify your password:
```cmd
python test_connection.py
```

Enter your MySQL root password when prompted.

