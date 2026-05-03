# Database Management with pgAdmin

## 🗄️ **Visual Database Access**

pgAdmin is now available for visual database management!

### **Access pgAdmin**
- **URL**: http://localhost:5050
- **Email**: admin@toansocratic.com
- **Password**: admin

---

## 🔗 **Connect to Database**

### **Step 1: Login to pgAdmin**
1. Open http://localhost:5050 in your browser
2. Login with:
   - Email: `admin@toansocratic.com`
   - Password: `admin`

### **Step 2: Add Server Connection**
1. Click "Add New Server" (➕ icon)
2. **General Tab**:
   - Name: `Toán Socratic DB`
3. **Connection Tab**:
   - Host name/address: `postgres` (Docker service name)
   - Port: `5432`
   - Database: `toansc`
   - Username: `toan_user`
   - Password: `toan_password`
4. Click "Save"

### **Step 3: Explore Database**
- Expand `Servers` → `Toán Socratic DB` → `Databases` → `toansc`
- Browse tables: `users`, `problems`, `sessions`, `progress`
- View data, run queries, manage schema

---

## 📊 **What You Can Do**

### **View Tables & Data**
- Browse all tables in the database
- View table structure and relationships
- Query and edit data directly
- Export data to CSV/JSON

### **Run SQL Queries**
```sql
-- View all problems
SELECT * FROM problems;

-- Count sessions by status
SELECT status, COUNT(*) FROM sessions GROUP BY status;

-- View recent sessions
SELECT * FROM sessions ORDER BY started_at DESC LIMIT 10;

-- Check user progress
SELECT * FROM progress WHERE mastery_score > 0.5;
```

### **Database Management**
- Create/drop tables
- Modify table structure
- Manage indexes and constraints
- Backup and restore databases

---

## 🔧 **Alternative: Command Line Access**

### **Direct PostgreSQL Access**
```bash
# Connect to database
docker exec -it toan_socratic_db psql -U toan_user -d toansc

# Common commands
\dt                    # List tables
\d problems           # Describe table
SELECT * FROM problems; # Query data
\q                    # Quit
```

### **From pgAdmin Query Tool**
- Click "Query Tool" (🔍 icon)
- Write and execute SQL queries
- Save favorite queries
- Export results

---

## 🛠️ **Management Commands**

### **Start/Stop pgAdmin**
```bash
# Start pgAdmin
docker-compose up -d pgadmin

# Stop pgAdmin
docker-compose stop pgadmin

# Restart pgAdmin
docker-compose restart pgadmin

# View logs
docker logs -f toan_socratic_pgadmin
```

### **Reset pgAdmin**
```bash
# Stop and remove pgAdmin container
docker-compose down pgadmin

# Remove pgAdmin data volume
docker volume rm tunas-math_pgadmin_data

# Start fresh
docker-compose up -d pgadmin
```

---

## 📋 **Database Schema Overview**

### **Tables**
- **users**: User accounts and authentication
- **problems**: Math problems with geometry parameters
- **sessions**: Socratic dialogue sessions
- **progress**: User progress tracking per topic

### **Key Relationships**
- `sessions.user_id` → `users.id` (CASCADE DELETE)
- `sessions.problem_id` → `problems.id`
- `progress.user_id` → `users.id` (CASCADE DELETE)

### **Sample Data**
- 5 sample problems loaded
- pgvector extension enabled
- Vietnamese math content with LaTeX

---

## 🎯 **Quick Start**

```bash
# 1. Start all services
docker-compose up -d

# 2. Access pgAdmin
open http://localhost:5050

# 3. Login and connect to database
# Email: admin@toansocratic.com
# Password: admin

# 4. Explore your data!
```

Now you have full visual control over your Toán Socratic database!