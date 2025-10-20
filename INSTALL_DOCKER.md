# How to Install Docker on Your Mac

## Quick Install (Recommended)

### Step 1: Download Docker Desktop
1. Go to: https://www.docker.com/products/docker-desktop/
2. Click "Download for Mac"
3. Choose your Mac chip:
   - **Apple Silicon (M1/M2/M3)**: Download "Mac with Apple chip"
   - **Intel**: Download "Mac with Intel chip"

### Step 2: Install
1. Open the downloaded `.dmg` file
2. Drag Docker icon to Applications folder
3. Open Docker from Applications
4. Follow the setup wizard
5. Click "Accept" on terms and conditions

### Step 3: Verify Installation
Open Terminal and run:
```bash
docker --version
docker-compose --version
```

You should see version numbers!

## After Docker is Installed

### Run RideGrid with Docker:
```bash
cd /Users/vasupatel/Desktop/RIdeGrid
./scripts/setup.sh
```

The script will now detect Docker and run everything in containers!

## Alternative: Using Homebrew

If you prefer command line:
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Docker Desktop
brew install --cask docker

# Start Docker Desktop
open /Applications/Docker.app
```

## Why Docker?

✅ **One command setup** - Everything just works  
✅ **No manual installations** - PostgreSQL, Redis, Kafka all included  
✅ **Clean environment** - Doesn't affect your system  
✅ **Easy cleanup** - Just stop Docker containers  

## After Installation

Once Docker is running:
```bash
cd /Users/vasupatel/Desktop/RIdeGrid
./scripts/setup.sh
# Now it will use Docker mode!
```

Then access:
- Frontend: http://localhost:3000
- API: http://localhost:8001
- Grafana: http://localhost:3001





