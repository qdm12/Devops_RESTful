# Portfolio Management RESTful API

This was developed for the DevOps course of New York University (CSCI-GA.3033-014).
This is a RESTful API for a portfolio management. It uses Python, Flask, Vagrant and Swagger for now.
It can be run locally on a virtual machine with Vagrant or on Bluemix (IBM) remotely.
It also uses a redis database from Bluemix cloud foundry.

Access the root URL of the API on Bluemix [here](https://portfoliomgmt.mybluemix.net)
Otherwise, you access it with Vagrant at this address [localhost:5000](localhost:5000)
The root URL uses **Swagger** to show a descriptive list of all available RESTful calls such as `POST`, `DELETE`, `PUT` and `GET`.

## Run it on your machine

- Install Vagrant from this [page](https://www.vagrantup.com/downloads.html)
- Git clone the repository or download the ZIP file and extract it.
- Open a terminal (You will need Github desktop App to run Git Shell for Windows)
- cd to the Devops_RESTFUL directory you just cloned
- Enter `vagrant up && vagrant ssh` (this will install the box, docker etc.)
- Enter `python /vagrant/server.py`
- Access it with your browser at [localhost:5000](localhost:5000), for example at [localhost:5000/api/v1/portfolios](localhost:5000/api/v1/portfolios).
- You can use the Chrome extension `Postman` for example to send RESTful requests other than `GET`. Download it [here](https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop?hl=en).

## For ongoing work, please refer to this page:
[https://github.com/rofrano/nyu-homework-2](https://github.com/rofrano/nyu-homework-2)
PART 1: Deploy the service in Docker Containers on Bluemix (submit URL of service on Bluemix)
PART 2: BDD and TDD Automated Testing (Good testing coverage required)
PART 3: Add an automated CI/CD DevOps Pipeline
