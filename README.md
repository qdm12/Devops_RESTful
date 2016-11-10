# Portfolio Management RESTful API
*The project was developed for the DevOps course of New York University (CSCI-GA.3033-014).*

## What is it?
- It is a RESTful API for a portfolio management.
- It uses many technologies: Python, Flask, Vagrant, Swagger, Redis, Docker, ...
- It can be run locally on a virtual machine with Vagrant or on Bluemix (IBM) remotely.
- The Redis database is stored on IBM Bluemix

## Access the API
- Access the root URL of the API on Bluemix at [https://portfoliomgmt.mybluemix.net](https://portfoliomgmt.mybluemix.net)
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
- Enter `vagrant up && vagrant ssh` (this will install the box, docker etc.)
- **TEMPORARY** In `server.py`, replace *redis_hostname = 'redis'* by *redis_hostname = '127.0.0.1'*
- Enter `python /vagrant/server.py` (in the virtual machine you just logged in)
- Access the Python Flask server with your browser at [localhost:5000](localhost:5000).
- You can use the Chrome extension `Postman` for example to send RESTful requests such as `POST`. Install it [here](https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop?hl=en).

## For ongoing work, please refer to this page:
[https://github.com/rofrano/nyu-homework-2](https://github.com/rofrano/nyu-homework-2)
- PART 1: Deploy the service in Docker Containers on Bluemix (submit URL of service on Bluemix)
- PART 2: BDD and TDD Automated Testing (Good testing coverage required)
- PART 3: Add an automated CI/CD DevOps Pipeline

## To contribute
- Send me an email at quentin.mcgaw @ gmail . com with your Github username and a reason.
- To update the Swagger documentation, please refer to the readme.md in the static folder [here](https://github.com/qdm12/Devops_RESTful/tree/master/static)
