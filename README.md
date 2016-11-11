# Portfolio Management RESTful API
*The project was developed for the DevOps course of New York University (CSCI-GA.3033-014).*

## What is it?
- It is a RESTful API for a portfolio management.
- It uses many technologies: Python, Flask, Vagrant, Swagger, Redis, Docker, ...
- It can be run locally on a virtual machine with Vagrant or on Bluemix (IBM) remotely.
- The Redis database is stored on IBM Bluemix

## Access the API
- Access the root URL of the API on Bluemix at [https://portfoliomgmt.mybluemix.net](https://portfoliomgmt.mybluemix.net)
- Access the root URL of the API on the Bluemix container [http://portfoliocontainer.mybluemix.net/](http://portfoliocontainer.mybluemix.net/)
- Access it on your virtual Vagrant machine at [localhost:5000](localhost:5000)
- The root URL uses **Swagger** to show a descriptive list of all available RESTful calls such as `POST`, `DELETE`, `PUT` and `GET`.

## Run it on your machine
- Install Vagrant from [vagrantup.com](https://www.vagrantup.com/downloads.html)
- Download the project
  - Without git
    - Download the ZIP file by clicking [here](https://github.com/qdm12/Devops_RESTful/archive/master.zip).
    - Extract the ZIP file.
  - With git (recommended)
    - Install git if you don't have it from [git-scm.com](https://git-scm.com/downloads) or use `apt-get install git`.
    - Open a terminal and enter `git clone https://github.com/qdm12/Devops_RESTful.git`
- Go to the project directory with a terminal with `cd Devops_RESTFUL`
- **TEMPORARY** In `server.py`, change `VAGRANT = False` to `VAGRANT = True`
- Enter `vagrant up && vagrant ssh` (this will install the box, docker etc.)
- Enter `python /vagrant/server.py` (in the virtual machine you just logged in)
- Access the Python Flask server with your browser at [localhost:5000](localhost:5000).
- You can use the Chrome extension `Postman` for example to send RESTful requests such as `POST`. Install it [here](https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop?hl=en).
- To user Swagger API calls, simply change the `"host":"portfolioMgmt.bluemix.net"` to `"host":"localhost:5000"` in the `static/swagger/specification/portfoliomgmt.js` file. **Don't forget to put it back before PUSHING on github!** (refer to the readme.md in `static/` for more information)

## Run it from a docker container
- Create a docker image by using a Dockerfile and then build the image using docker build -t container_name .
- Run the docker image by entering docker run --rm -p 5000:5000 --link redis image-name. Don't forget to link redis.
- You can check if your container is running by using docker ps -a
- Access the running conatiner  with your browser at [localhost:5000](localhost:5000).
- Once you are satisfied with the running container, time to push it to cloud.
- Login into the bluemix server twice. First using cf login and second using cf ic login.
- Make sure that you have cloud foundry IBM containers plugin installed in your vagrant. Vagrantfile should take care of that. If not install it manually using command echo Y | cf install-plugin https://static-ice.ng.bluemix.net/ibm-containers-linux_x64
- Create your namespace cf ic namespace set yournamespace
- Tag the docker image on vagrant that you created with the remote container name registry.ng.bluemix.net/yournamespace/container_name
- Push this tagged version of your container to bluemix using command cf ic push remote_container_name
- At this point you will have your docker image showing on the bluemix page. Click on that to create a container from it.
- Access the URL showing as Routes under group details to access the running container on cloud. [http://portfoliocontainer.mybluemix.net/](http://portfoliocontainer.mybluemix.net/)

## For ongoing work, please refer to this page:
[https://github.com/rofrano/nyu-homework-2](https://github.com/rofrano/nyu-homework-2)
- PART 1: Deploy the service in Docker Containers on Bluemix (submit URL of service on Bluemix)
- PART 2: BDD and TDD Automated Testing (Good testing coverage required)
- PART 3: Add an automated CI/CD DevOps Pipeline

## To contribute
- Send me an email at quentin.mcgaw @ gmail . com with your Github username and a reason.
- To update the Swagger documentation, please refer to the readme.md in the static folder [here](https://github.com/qdm12/Devops_RESTful/tree/master/static)
