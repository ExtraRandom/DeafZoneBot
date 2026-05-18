### Run docker image

````shell
docker run -d \
    --name dz_bot \
    --restart=unless-stopped \
    -v /path_to_docker_volumes_folder/discord/logs:/app/logs \
    -v /path_to_docker_volumes_folder/discord/configs:/app/configs \
    extrarandom/dz_bot:latest
````


### Updating
Remove the old image
````shell
docker stop dz_bot
docker rm dz_bot
````
Then run the docker image using the above command


# Docker Compose 
```yaml
services:
  discord-bot:
    container_name: dz_bot
    image: extrarandom/dz_bot:latest
    restart: unless-stopped
    volumes:
      - /path_to_docker_volumes_folder/discord/logs:/app/logs
      - /path_to_docker_volumes_folder/discord/configs:/app/configs

```