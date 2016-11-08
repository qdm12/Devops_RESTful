# To change the Swagger documentation

1. Go to the (Swagger online editor)[http://editor.swagger.io/#/]
2. Paste the content of the file (swagger_api.yaml)[https://github.com/qdm12/Devops_RESTful/edit/master/static/swagger_api.yaml] to the left panel.
3. Modify the code in the left panel
4. When finished, click on **File** and then **Download YAML** and **Download JSON**
5. Paste the content of the downloaded YAML file into *swagger_api.yaml* for future use
6. Paste the content of the downloaded JSON file into *static/swagger/js/swagger_api.js* **between** the first line and the last line
7. You can then test it with your browser by clicking on *static/swagger/index.html*
8. You then have to push it to Bluemix for the changes to take effect on Vagrant and Bluemix.