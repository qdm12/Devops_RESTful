# NYU Homework 1
Welcome to the first homework assignment for CSCI-GA.3033-014 DevOps. This homework assignment is due November 2nd 2016. That should give you 4 weeks to work on it. Note: that 4 weeks is two Sprints to most Agile teams.

## Scenario

You have been asked to develop a RESTful service for a client. Since this is a fictional client, you are free to create a service that manipulates any resource you like. The only requirement is that it must be RESTful according to the guidelines that we learned in class!

The service must support the complete CRUD lifecycle calls plus List, Query, and at least one Action:
- List Resources
- Read a Resource
- Create a Resource
- Update a Resource
- Delete a Resource
- Query Resources by some attribute of the Resource
- Perform some Action on the Resource

This assignment is in three parts and will bring together everything you have learned in the first half of the semester. Since this is a course on DevOps and one of the fundamental tenants of DevOps is _Collaboration_, this will be a **group project**.

## Form an Agile Development Team
The first thing you will need to do is form a team of 4 people. There are 16 students in the class so there should be 4 teams of 4 students each. You will maintain this team though both homework assignments becasue they build on each other.

Each team will produce 1 RESTful service as a team (i.e., 4 people = 1 service)

The 3 parts of the assignment breaks down as follows:

## Part 1: Agile Development and Planning
We want to simulate what a real Agile development team would do to plan out their sprints. To this end, you need to create a Backlog of Stories and a Milestone to plan your sprint. You will need to:

- Create a repository on GitHub to store your project
- Invite others members of the team to your GitHub repository
- Write Stories (as Github `Issues`) to plan the work needed to create the service. You will need at least 4 Stories but you can write as many more as you'd like.
- Ensure that the Stories follow the template that we studied in class.
- Be certain to think MVP (Minimal Viable Product). Make your stories small. Get basic functionality working first, then add more features.
- Order your Backlog of Stories from most important to least important
- Create a Milestone that is the due date for the assignment and add Stories to the Milestone
- (optional) Since you have 4 weeks to complete the assignment, you might want to plan two 2 week Sprints (which would result in 2 Milestones)
- Using ZenHub, each member of your 4 person team should assign a Story to themselves, move to _In Process_ and begin working on it.

What I am looking for is an understanding of how an self-directed Agile team works. You won't be telling me who did what. I should be able to look at the Kanban board from ZenHub and determine exactly what was done, and who completed which story. This should also help you understand where you are in the assignment and if you will reach your sprint goal of submitting your homework on time!

Please submit the URL of your group's GitHub repository to complete Part 1 of this homework.

## Part 2: Develop the service locally
In Part 2 you will develop the service based on the Stories you wrote in Part 1. You can use the starter code supplied by the code template from this GitHub project as a skeleton. You should be able to cut and paste code from previous labs that we have done in class to complete this homework. Even if you don't know Python, it shouldn't be too hard to assemble the code needed from what I have provided.

You will need to:
- Create a `Vagrantfile` so that members of the team can quickly get a development environment running
- The Vagrantfile should install all of the needed software to run the service so that the all a team member needs to do is `vagrant up && vagrant ssh` and be able to start developing.
- Use Docker inside of Vagrant for any 3rd part services you want to use. e.g., if you use a Redis, PostgreSQL, MySQL database, etc. it should be installed using Docker.
- Develop the code as per the Stories you created in Part 1

Think about what you need to do in this part and make sure that there is a Story to cover the work. (hint: there should be a Story for someone to create the Vagrantfile for everyone else to use and it should be pretty high up in the Backlog.)

## Part 3: Deploy the service to the cloud
In Part 3 you will deploy your application to the cloud. In particular the Cloud Foundry cloud in IBM Bluemix. If you used 3rd party services like a database (e.g., Redis, MySQL, etc.) you will need to bind the equivalent Bluemix services to your application.

You will need to:
- Create a Cloud Foundry application in Bluemix
- Download and install the Cloud Foundry CLI (_hint: this should be added to the Vagrantfile you created earlier_)
- Create the necessary `manifest.yml`, `Procfile`, `runtime.txt` file so that Bluemix will know how to deploy your application. (_hint: you might want to create the sample Cloud Foundry app that I created in class and borrow these files as a template_)
- Use `cf push` to push your application to Bluemix
- Hit the URL of your service and make sure that it works

What I am looking for here is a working service that is running on Bluemix.

Please submit the URL of your group's service running in Bluemix to complete Part 3 of this homework.
