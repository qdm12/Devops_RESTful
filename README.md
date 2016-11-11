# Portfolio Management RESTful API
*The project was developed for the DevOps course of New York University (CSCI-GA.3033-014).*

## I - What is it?
- It is a RESTful API for a portfolio management.
- It uses many technologies: Python, Flask, Vagrant, Swagger, Redis, Docker, ...
- It can be run locally on a virtual machine with Vagrant or on Bluemix (IBM) remotely.
- The Redis database is stored on IBM Bluemix

## II - Access the API
- Access the root URL of the API on Bluemix at [https://portfoliomgmt.mybluemix.net](https://portfoliomgmt.mybluemix.net)
<<<<<<< HEAD
- Access the root URL of the API on the Bluemix container at [http://portfoliocontainer.mybluemix.net/](http://portfoliocontainer.mybluemix.net/)
=======
- Access the root URL of the API on the Bluemix container [http://portfoliocontainer.mybluemix.net/](http://portfoliocontainer.mybluemix.net/)
>>>>>>> 96560c3e9809d651ef0711a8236367334ee91351
- Access it on your virtual Vagrant machine at [localhost:5000](localhost:5000)
- The root URL uses **Swagger** to show a descriptive list of all available RESTful calls such as `POST`, `DELETE`, `PUT` and `GET`.

## III - Obtain the source code and minimum requirements
1. Install Vagrant from [vagrantup.com](https://www.vagrantup.com/downloads.html)
2. Download the project
  - Without git
    - Download the ZIP file by clicking [here](https://github.com/qdm12/Devops_RESTful/archive/master.zip).
    - Extract the ZIP file.
  - With git (recommended)
    - Install git if you don't have it from [git-scm.com](https://git-scm.com/downloads) or use `apt-get install git`.
    - Open a terminal and enter `git clone https://github.com/qdm12/Devops_RESTful.git`
3. Go to the project directory with a terminal with `cd Devops_RESTFUL`

## IV - Run it on your machine with Vagrant
1. Make sure to follow the steps of **III - Obtain the source code and minimum requirements**. 
2. Enter `vagrant up && vagrant ssh` (this will install the box, docker etc.)
3. Enter `python /vagrant/server.py` (in the virtual machine you just logged in)
4. Access the Python Flask server with your browser at [localhost:5000](localhost:5000). You can then make API calls with Swagger.
5. You can also use the Chrome extension `Postman` for example to send RESTful requests such as `POST`. Install it [here](https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop?hl=en).
6. To update Swagger, refer to the information in the [Github `static` directory](https://github.com/qdm12/Devops_RESTful/tree/master/static).

## V - Run it on Bluemix
1. Make sure to follow the steps of **III - Obtain the source code and minimum requirements** although you don't need Vagrant.
2. Login to Bluemix as follows:
  - `cf login https://api.ng.bluemix.net -u username -o organization -s "Portfolio Management"`
  - Enter the API endpoint as `https://api.ng.bluemix.net`
  - Enter your password
3. Enter `cf push PortfolioMgmt`
4. You can then access it at [https://portfoliomgmt.mybluemix.net](https://portfoliomgmt.mybluemix.net)


## VI - Run it on a Docker container

### A) Build and run it on Vagrant
1. Make sure to follow the steps of **III - Obtain the source code and minimum requirements**. 
2. Enter `vagrant up && vagrant ssh` (this will install the box, docker etc.)
3. Enter `cd /vagrant` (in the virtual machine you just logged in)
4. Enter `docker build -t docker-portfoliomgmt .`
  - **Don't forget the '.' !**
  - This builds a Docker image `docker-portfoliomgmt` from the `Dockerfile` description file.
  - You can list your local Docker images with `docker images` to make sure it was created.
4. Run the Docker image with `docker run --rm -p 5000:5000 --link redis docker-portfoliomgmt`.
  - The `--rm` option automatically removes the container when it exits.
  - The `-p 5000:5000` option publishes the container's 5000 port to the host.
  - The `--link redis` option links the `docker-portfoliomgmt` to the `redis` container.
  - You can check the container is runnig with `docker ps -a`.
5. As for *IV*, you can access the Python Flask server with your browser at [localhost:5000](localhost:5000). You can then make API calls with Swagger.

### B) Push and run it on Bluemix
1. Make sure you had followed the steps of *A) Build and run it on Vagrant*.
2. In Vagrant (`vagrant up && vagrant ssh`), login in the bluemix server as follows:
  - `cf login https://api.ng.bluemix.net -u username -o organization -s "Portfolio Management"`
  - Enter the API endpoint as `https://api.ng.bluemix.net`
  - Enter your password
  - **TEMPORARY**: Enter `echo Y | cf install-plugin https://static-ice.ng.bluemix.net/ibm-containers-linux_x64` to install *cf ic*.
  - `cf ic login`
4. If not done already, create your namespace with `cf ic namespace set portfoliocontainer`
5. Tag the Docker image with the remote container name `registry.ng.bluemix.net/portfoliocontainer/docker-portfoliomgmt` with the following command: `docker tag docker-portfoliomgmt registry.ng.bluemix.net/mynamespace/docker-portfoliomgmt`
6. Push it with `docker push registry.ng.bluemix.net/portfoliocontainer/docker-portfoliomgmt` or with `docker push` **DOES NOT WORK FOR NOW**
7. The Docker image should be on the Bluemix webpage. Click on it to create a container.
8. Access the URL showing as *Routes* under *Group details* to access the running container. YOu can access it at [http://portfoliocontainer.mybluemix.net/](http://portfoliocontainer.mybluemix.net/)

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
