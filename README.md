# dojo-synthetic-api

## Run with uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 5003 --workers 4
```

## Run with docker-compose

Install docker and docker-compose

```
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
sudo mkdir -m 0755 -p /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Fill in the environment variables in `docker-compose.yml` and run `docker compose up`

```
# Go into the editor for docker-compose.yml and edit the environment variables
# CHANGE THOSE LINES THAT ARE MARKED WITH # CHANGE
vim docker-compose.yml

# Run the service
docker compose up -d
```
