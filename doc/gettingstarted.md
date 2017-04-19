# Getting started with INCA
## Hints for everyone who is wants to get involved in helping with the project

In this document, students and colleagues new to INCA find some useful links for getting started. In particular, it lists some ressources where you can brush up your skills regarding the tools we use. Please add anything you find useful to this doc.

## Editing this document
This document is written in Markdown. Also other files, like README or TODO files are written in Markdown. It's very simple, you can find instructions here: https://guides.github.com/features/mastering-markdown/

## git
Rather than mailing back-and-forth files or giving them names like myscript1_version22.py and myscript3535_april3.py, we use a version control system that allows us to track changes and work together on one project. It's called git, and using it can be a bit intimidating at first. But once you got used to it, you'll love it! Some links to learn more:

- http://rogerdudler.github.io/git-guide/
- https://git-scm.com/book/en/v2/Getting-Started-Git-Basics
- http://swcarpentry.github.io/git-novice/

## Common Linux tools
While in principle, INCA is platform-independent and can be run on any platform, chances are very high you will (also) work on a platform that runs Linux.

If you want to fresh up your knowledge of the Linux shell, have a look here:

- http://swcarpentry.github.io/shell-novice/

Most things you need will also be covered in this book:

- https://github.com/damian0604/bdaca/tree/master/book

To edit text files from the Linux command line, you have several editors at your disposal (ranked by ease-of-use):

- `nano' (easy to use, but no advanced functionality)
- `vim' (for the nerdy people among you)
- `emacs' (offers a lot of nice things, including syntax highlighting). You can get a nice reference card for printing out and putting on your wall here: https://www.gnu.org/software/emacs/refcards/pdf/refcard.pdf

# Workflow INCA
Generally, INCA runs on a server. However, if you want to contribute to INCA, it is convenient to have a copy of INCA on a local folder. 
In this way you can work on INCA in a local folder, before pushing the adjustments you have made to a development branch in Github.
Here, your work will be approved (or disapproved) by some of the 'senior staff' of INCA. This workflow prevents us from accidentally deleting parts of INCA code or making unfortunate changes.

Here you find the entire workflow:

-	Work in your own copy of INCA (in order to do so, you need Elasticsearch)
-	Push to Development Branch 
-	Approval by Chief members
-	Push to Master Branch

# Installing INCA on your own computer
In order to contribute to INCA, you need the complete the following steps:

-	STEP 1: Install Elasticsearch (i.e., the database where all your files are stored). 
-	STEP 2:	Install Git
-	STEP 3:	Pull (Python) code of INCA to local folder

Below, instructions are provided for the above-mentioned steps in both Ubuntu (Linux) and Mac. 

## STEP 1: Installing Elasticsearch

### Install Elastic Search on Ubuntu

-	Install Java first:

```
suo apt-get update
sudo apt-get install default-jre
sudo apt-get install default-jdk
```

-	Then, add elastic search to the list of sources apt-get knows and install Elastic Search using apt-get:

```
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo apt-get install apt-transport-https
echo "deb https://artifacts.elastic.co/packages/5.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-5.x.list
sudo apt-get update && sudo apt-get install elasticsearch
```

Elastic Search should be installed now. You can start it as follows:

```
sudo -i service elasticsearch start
```
Similarily, you can also stop it --- or check whether it is running
```
sudo -i service elasticsearch stop
sudo service elasticsearch status
```

### Install Elastic Search on MAC

-	Install JAVA. You need the JDK (find it here: http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html) 
-	Get Elasticsearch: https://www.elastic.co/downloads/elasticsearch
choose the ZIP file and download it. Unzip and copy-paste the folder to a convenient folder on your computer (preferably not in "Downloads" as you will start Elasticsearch from this folder in the future).
-	Locate the downloaded files in your terminal. You can do this using cd. For example: ```$ cd /Users/admin/surfdrive/Werk/ACA/elasticsearch-5.3.0```
-	run, in a new command line: ```$ bin/elasticsearch```. This will launch Elasticsearch. 

NOTE: To exit Elasticsearch, use CTRL C

More information you can find here:
-	https://chartio.com/resources/tutorials/how-to-install-elasticsearch-on-mac-os-x/#manual-elasticsearch-installation

## Installing GIT
Make sure you have a Github account, remember username and password :-)

## STEP 2: Install git on Ubuntu
```
sudo apt-get install git
```
### Install git on Mac
Download git here: https://git-scm.com/download/mac

## STEP 3: download INCA

### This works for both mac and ubuntu

-	Go to your terminal and check the version of git: 
```git --version``` If the installation failed somehow, you will get an error.
-	Configure your username:
```
git config --global user.email <email address>
git config --global user.name <username>
```

### Copy INCA to your local PC using GIT:
-	Make a new folder on your computer where you want to work on INCA. Go there using your terminal: ```cd /pathtoyourfolder```
-	Clone inca to your local folder, using ```git clone https://github.com/uvacw/inca.git```

## And now?

Please check the [Contributing Code Guide](https://github.com/uvacw/inca/blob/development/doc/Contributing%20Code%20Guide.md) for the next steps!


