## Run following commands to deploy app as container

'''
docker build -t {your acr address}/Dashboard:{version} . (Be Careful: there is another blank space after dot, so it will be [space].[space])

docker login {your azure container registery}

docker push

## Or follow tutorial to deploy app in Azure Web App Service
