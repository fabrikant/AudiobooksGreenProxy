# AudiobooksGreenProxy

This is a self-hosted proxy to work in conjunction with the audiobook player [AudiobooksGreen](https://github.com/fabrikant/AudiobooksGreen).

# Installation and Launch Methods

## Docker compose - from a pre-built image (recommended)
Create a directory on your server. In it, create a **docker-compose.yml** file with content from the [docker-compose.yml.example](https://github.com/fabrikant/AudiobooksGreenProxy/blob/main/docker-compose.yml.example) file. Following the recommendations in the comments, set your own values.

Next to the **docker-compose.yml** file, create a **data** directory.

### Launch
```
docker compose up -d
```

### Stop
```
docker compose down
```

### Update
```
docker compose pull
docker compose down
docker compose up -d
docker image prune
```

# Building a Docker image from source

```
docker build -t audiobooks_green_proxy .
```

Launch it the same way as in the previous section. Only in the **docker-compose.yml** file, you need to replace the image name with the one you have in your system.
You can view image names using the command:
```
docker image ls -a
```

# Running Python Code

### Virtual environment setup and configuration
```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt
deactivate
```

### Launch
Activate the virtual environment
```
source .venv/bin/activate
```

Set environment variables (if required)
```
export SSL_CERT_FILE=./data/fullchain.pem
export SSL_PRIVATE_KEY_FILE=./data/privkey.pem
```

Launch proxy
```
python3 books_proxy.py
```
