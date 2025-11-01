# MySQL Server Installation Guide

This guide covers how to install MySQL Server for the ALX_prodev project on different operating systems.

## Windows Installation

### Method 1: MySQL Installer (Recommended)

1. **Download MySQL Installer:**
   - Visit: https://dev.mysql.com/downloads/installer/
   - Download "MySQL Installer for Windows" (choose the web or full installer)
   - Select the "mysql-installer-community" version

2. **Run the Installer:**
   - Run the downloaded `.msi` file
   - Choose "Developer Default" or "Server only" setup type
   - Follow the installation wizard

3. **Configure MySQL Server:**
   - During setup, choose "Standalone MySQL Server"
   - Select "Development Computer" as the config type
   - Set root password (or leave empty for development)
   - Make sure "MySQL Server" service is set to start automatically
   - Note the port (default is 3306)

4. **Verify Installation:**
   ```cmd
   mysql --version
   ```

### Method 2: Using Chocolatey (If you have Chocolatey installed)

```cmd
choco install mysql
```

### Method 3: Using Docker (Alternative - No system installation)

If you prefer not to install MySQL directly on your system:

1. **Install Docker Desktop for Windows:**
   - Download from: https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop

2. **Run MySQL Container:**
   ```cmd
   docker run --name mysql-alx-prodev -e MYSQL_ROOT_PASSWORD= -e MYSQL_ALLOW_EMPTY_PASSWORD=yes -p 3306:3306 -d mysql:8.0
   ```

3. **Connect to MySQL:**
   - Use `localhost:3306` as your connection host
   - Update `seed.py` connection settings if needed

## Linux (Ubuntu/Debian) Installation

### Using APT Package Manager

```bash
# Update package list
sudo apt update

# Install MySQL Server
sudo apt install mysql-server -y

# Secure MySQL installation (optional but recommended)
sudo mysql_secure_installation

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql

# Verify installation
mysql --version
```

### Ubuntu Specific: Set root password (if needed)

```bash
sudo mysql -u root
```

Then in MySQL prompt:
```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password';
FLUSH PRIVILEGES;
EXIT;
```

## macOS Installation

### Method 1: Using Homebrew (Recommended)

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install MySQL
brew install mysql

# Start MySQL service
brew services start mysql

# Verify installation
mysql --version
```

### Method 2: Using MySQL Installer

1. Download MySQL DMG from: https://dev.mysql.com/downloads/mysql/
2. Run the installer package
3. Follow the installation wizard
4. Remember the root password you set (if any)

## Post-Installation Setup

### 1. Verify MySQL is Running

**Windows:**
```cmd
# Check if MySQL service is running
sc query MySQL80
```

**Linux/macOS:**
```bash
# Check MySQL service status
sudo systemctl status mysql  # Linux
brew services list           # macOS (if using Homebrew)
```

### 2. Test MySQL Connection

**Windows (Command Prompt or PowerShell):**
```cmd
mysql -u root -p
# Press Enter if no password, or enter your password
```

**Linux/macOS:**
```bash
sudo mysql -u root -p
```

### 3. Configure Connection in seed.py

Edit `python-generators-0x00/seed.py` and update these connection parameters if needed:

```python
connection = mysql.connector.connect(
    host='localhost',      # Change if MySQL is on different host
    user='root',           # Change if using different user
    password='',           # Add your password if you set one
    port=3306              # Change if using different port
)
```

If you set a root password during installation, update the `password` field:
```python
password='your_password_here',
```

### 4. Common Issues and Solutions

#### Issue: "Access denied for user 'root'@'localhost'"
**Solution:**
```sql
# Connect as root
sudo mysql -u root  # Linux/macOS
# Or: mysql -u root -p  # Windows (with password)

# Reset root password
ALTER USER 'root'@'localhost' IDENTIFIED BY '';
# Or set a password:
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

#### Issue: "Can't connect to MySQL server"
**Solutions:**
1. Check if MySQL service is running:
   - Windows: Services app → find MySQL service → Start
   - Linux: `sudo systemctl start mysql`
   - macOS: `brew services start mysql`

2. Verify port 3306 is not blocked by firewall

3. Check if MySQL is listening on the correct interface:
   ```bash
   # Linux/macOS
   sudo netstat -tlnp | grep 3306
   ```

#### Issue: "ModuleNotFoundError: No module named 'mysql'"
**Solution:**
```bash
# Install Python MySQL connector
pip install mysql-connector-python
# Or
pip install -r requirements.txt
```

### 5. Quick Start After Installation

1. **Start MySQL** (if not running automatically):
   ```bash
   # Windows: Use Services app or:
   net start MySQL80
   
   # Linux:
   sudo systemctl start mysql
   
   # macOS (Homebrew):
   brew services start mysql
   ```

2. **Verify connection works:**
   ```bash
   mysql -u root -p
   # Enter password (or press Enter if none)
   ```

3. **Test the project:**
   ```bash
   cd python-generators-0x00
   python 0-main.py
   ```

## Docker Alternative (Recommended for Development)

If you want to avoid installing MySQL directly on your system:

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: mysql-alx-prodev
    environment:
      MYSQL_ROOT_PASSWORD: ""
      MYSQL_ALLOW_EMPTY_PASSWORD: "yes"
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    command: --default-authentication-plugin=mysql_native_password

volumes:
  mysql_data:
```

### Run with Docker Compose

```bash
# Start MySQL
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs mysql

# Stop MySQL
docker-compose down
```

Then update `seed.py` to connect to `localhost:3306` (same as local installation).

## Verification Checklist

After installation, verify:

- [ ] MySQL server is installed (`mysql --version` works)
- [ ] MySQL service is running
- [ ] Can connect to MySQL (`mysql -u root` works)
- [ ] Port 3306 is accessible
- [ ] Python MySQL connector is installed (`pip list | grep mysql`)
- [ ] `seed.py` connection settings match your MySQL setup
- [ ] Can run `python 0-main.py` successfully

## Additional Resources

- MySQL Official Documentation: https://dev.mysql.com/doc/
- MySQL Download Page: https://dev.mysql.com/downloads/mysql/
- MySQL Connector/Python: https://dev.mysql.com/doc/connector-python/en/

