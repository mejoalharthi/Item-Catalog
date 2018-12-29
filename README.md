# Item Catalog Project

This project is an application that provides a list of items within a variety of categories as well as
provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

## Getting Started with Requires Software Installation

1. Install Vagrant: [Vagrant](https://www.vagrantup.com/downloads.html)
2. Install Virtual Machine: [VM](https://www.virtualbox.org/wiki/Downloads)
3. Download a FSND virtual machine: [FDNS-VM](https://github.com/udacity/fullstack-nanodegree-vm)
4. Download Git Bash: [GitBash](https://git-for-windows.github.io/) for windows, On Mac or Linux systems, you can use the
built-in
6. Download or Clone this project
7. Run application with python catalog_setup.py from within its directory
8. Run application with python seeder.py from within its directory
9. Run application with python application.py from within its directory
10. Visit http://localhost:8000/CoffeeCatalog to access the application


Open Git bash or Terminal navigate to the project folders by following this instructions:
  ```
  cd vagrant
  vagrant up
  vagrant ssh
  cd /vagrant
  cd catalog
  ```


## JSON Endpoints

- http://localhost:8000/CoffeeCatalog.json : All categories along with their items
- http://localhost:8000/CoffeeCatalog/category_id.json : All items in a specific category
- http://localhost:8000/category_id/Items/Item_id.json : Specific item in a specific category
