# dojo-synthetic-api

Before running the synthetic data api, you will need the following keys:

- Openrouter (from https://openrouter.ai/)
- E2B (from https://e2b.dev/)

Copy the .env.example file to a .env file and fill in the blanks, here we will use Openrouter as our LLM API provider.

```bash
cp .env.example .env

# env vars that need to be filled
REDIS_USERNAME=
REDIS_PASSWORD=
OPENROUTER_API_KEY=
E2B_API_KEY=
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
