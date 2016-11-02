# Portfolio Management RESTful API

This was developed for the DevOps course of New York University (CSCI-GA.3033-014).

It can be run with Vagrant or Bluemix (IBM), and uses a redis database.

Access the [live Bluemix API](https://portfoliomgmt.mybluemix.net)

You can access the root URL for Bluemix [here](https://portfoliomgmt.mybluemix.net) or on your local Vagrant [here](localhost:5000) to see a **Swagger** list of available RESTful calls such as `POST`, `DELETE`, `PUT` and `GET` at different URIs.

## Run it on your machine

- Install Vagrant from this [page](https://www.vagrantup.com/downloads.html)
- Git clone the repository or download the ZIP file and extract it.
- Open a terminal (`cmd.exe` for Windows)
- cd to the Devops_RESTFUL directory you just cloned
- Enter `vagrant up && vagrant ssh` (this will install the box, docker etc.)
- Enter `python /vagrant/server.py`
- Access it with your browser at [localhost:5000](localhost:5000), for example at [localhost:5000/api/v1/portfolios](localhost:5000/api/v1/portfolios).
- You can use the Chrome extension `Postman` for example to send RESTful requests other than `GET`. Download it [here](https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop?hl=en).
