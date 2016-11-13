# To change the Swagger documentation

1. Go to the [Swagger online editor](http://editor.swagger.io/#/).
2. Paste the content of the file [`static/swagger/specification/portfolioMgmt.yaml`](https://github.com/qdm12/Devops_RESTful/edit/master/static/swagger/specification/portfolioMgmt.yaml) to the left panel.
3. Modify the code in the left panel, which is rendered on the right panel.
4. When finished, click on **File** and then **Download YAML** and **Download JSON**.
5. Rename the JSON and YAML files downloaded to *portfolioMgmt.json* and *portfolioMgmt.yaml* respectively.
6. Overwrite the JSON and YAML files present in `static/swagger/specification` with the two files previously renamed.

# Testing it
**IMPORTANT**: Your browser caches *js* files so you will have to clean the cache each time you modify Swagger.
> *You can use SHIFT+F5 to refresh and clear the browser cache (works on Google Chrome).*

## Test it locally
- Run the python server once to generate the javascript code necessary for Swagger: `python server.py`
- You can then test it simply with your browser by clicking on *static/swagger/index.html*
- *Try it out!* will not work because there is no Python server running.

## Test it on Vagrant
- Enter `vagrant up && vagrant ssh`
- Enter `python /vagrant/server.py`
- Open your browser and go to [localhost:5000](http://localhost:5000)

## Test it on Bluemix
- If not installed, please install the cf cli from [github.com/cloudfoundry/cli](https://github.com/cloudfoundry/cli)
- Login to Bluemix with `cf login https://api.ng.bluemix.net -u bluemixUserId -o bluemixOrg -s "AppName"`and enter your password.
- Enter `cf push AppName` where *AppName* is **PortfolioMgmt** in this project.
- Open your browser and go to [https://portfoliomgmt.mybluemix.net/](https://portfoliomgmt.mybluemix.net/)

## Test it on a container in Vagrant
- Similarly, you can test Swagger on a container running in Vagrant or Bluemix, please refer to the root Readme for instance.