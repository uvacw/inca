# Getting started with INCA
## Hints for everyone who is or wants to get involved in the project

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

-  	STEP 1: Local settings (For mac users only)
-	STEP 2: Install Python 
-	STEP 3: Install Elastic Search (i.e., the database where all your files are stored). 
-	STEP 4:	Install Git
-	STEP 5:	Pull (Python) code of INCA to local folder
-	STEP 6: Check whether it works
Below, instructions are provided for the above-mentioned steps in both Ubuntu (Linux) and Mac.

## STEP 1: ONLY FOR MAC USERS

The local settings of your terminal probably do not support UTF-8. That's a problem. We can easily change it. Otherwise you will run into problems later on.

Type the following in your terminal:
```
sudo nano /etc/profile
```
Scroll down with the arrow keys to the end of file in the text editor that popped up, and copy-paste the following two lines:

```
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
```

Save the file: CTRL+O, press ENTER to confirm the file name.
Exit the editor: CTRL+X

Restart the terminal (exit completely and restart). 

## STEP 2: Install Python

Please install python 3 on your computer. There are a lot of ways to install Python. There are two alternatives: Using a 'pure' python installation in which you install all necessary packages on an as-you-need basis, or downloading Anaconda, where most things you need are already in there. 

The rest of the documentation of this project assumes the pure approach (rather than the Anaconda approach). If you choose for Anaconda, you might have to figure out some problems yourself later on. 
 
### The 'pure' approach 
You can install using 

-	*Ubuntu*: check whether you have python3 on your computer. Check which python you have on your computer with the following bash command: ```python3 --version```. When you have a version higher than 3.4, you are fine. Otherwise, please install using: sudo apt-get python3 --version.

You should also install iPython3: 
```sudo pip3 install ipython ```

- *Mac*: check whether you have python3 on your computer. Even if you don't know it, chances are high you do have it as it is automatically installed on Macs. Check which python you have on your computer with the following bash command: ```python3 --version```. When you have a version higher than 3.4, you are fine. A higher version is fine, but you do not need to upgrade. 

If Python is not installed, please download the latest version from python.org. 
You can write your Python code in whatever text editor you like. We recommend, however, to use a IDE, such as PyCharm. 

You should also install iPython3: 
```sudo pip3 install ipython```

This is however a bit more tricky on a Mac compared to Ubuntu. The right folder will probably not be found. Please execute the following steps (you only have to do this one time):

go to your home folder in the terminal: ```cd ~```
type: ```sudo nano .bash_profile```

Please copy-paste the following into the Nano: 

```
PATH="/Library/Frameworks/Python.framework/Versions/3.4/bin:${PATH}"
export PATH
```

Save using: CTRL-O ENTER
Exit using: CTRL-X

Restart your terminal (close and restart). 
Now, you should be able to start both python3 and ipython3 from the terminal. 

### The Anaconda approach

Download Anaconda from https://www.continuum.io/downloads
If you want to install packages, you should use the command: ``` conda install <whatever>``` instead of pip3

## STEP 3: Installing Elastic Search

**NB: INCA only works on Elasticsearch 6 or higher, please make sure you have the right version installed**

### Install Elastic Search on Ubuntu

-	Install Java first:

```
sudo apt-get update
sudo apt-get install default-jre
sudo apt-get install default-jdk
```

-	Then, add elastic search to the list of sources apt-get knows and install Elastic Search using apt-get:

```
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo apt-get install apt-transport-https
echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-6.x.list
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
-	Locate the downloaded files in your terminal. You can do this using cd. For example: ```cd /Users/admin/surfdrive/Werk/ACA/elasticsearch-6.3.0```
-	run, in a new command line: ```bin/elasticsearch```. This will launch Elasticsearch (you can just keep it running in the background. Everytime you restart your computer or terminal, you need to relaunch Elastic Search if you want to work with inca). 

NOTE: To exit Elasticsearch, use CTRL C

More information you can find here:
-	https://chartio.com/resources/tutorials/how-to-install-elasticsearch-on-mac-os-x/#manual-elasticsearch-installation


## STEP 4: Install git

Make sure you have a Github account, remember username and password :-)

### Install git on Ubuntu
```
sudo apt-get install git
```
### Install git on Mac
Download git here: https://git-scm.com/download/mac

### This works for both mac and ubuntu

-	Go to your terminal and check the version of git: 
```git --version``` If the installation failed somehow, you will get an error.
-	Configure your username:
```
git config --global user.email <email address>
git config --global user.name <username>
```
## STEP 5: Download INCA

### Copy INCA to your local computer using GIT:
-	Make a new folder on your computer where you want to work on INCA. Go there using your terminal: ```cd /pathtoyourfolder```
-	Clone inca to your local folder, using ```git clone https://github.com/uvacw/inca.git```
-	You are now on the Master branch, which is the latest stable release of INCA. But you probably want to work on the development branch instead, which is the latest version of the code we are developing and improving. You can do so with ```git checkout development```. After that, do ```git pull``` to make sure you really downloaded the latest version.
- Finally, we have to install the Python packages INCA depends on, such as packages for machine learning, reading RSS feeds, connecting to Elastic Search and so on. You could do so by hand (installing every package as soon as you get an 'import error', but we also made a file to install all of them at once. First of all, we need one dependency (libmysqlclient-dev, in particular the mysql_config script) that a specific module (pattern needs). On Linux, you can get it as follows:

```
sudo apt-get install libmysqlclient-dev
``` 
Now, you are ready to install all required modules:


```
cd inca    # assuming you still are in inca's parent directory
sudo pip3 install -r Requirements
```

## STEP 6: Adapt the settings

INCA needs to be configured - in particular, you need to tell INCA things like how to access ElasticSearch or where to store images. 
We made a default configuration that you can just copy:
```
cd <pathtoyourincafolder> 
cp default_settings.cfg settings.cfg
```
But please have a look at settings.cfg and change things that need to be changed! You can use any text editor you like, for instance:
```
emacs settings.cfg
```


## STEP 7: Check whether everything works

go to your inca folder 	
```
cd <pathtoyourincafolder> 
python3 -c 'import inca'
```

Troubleshooting:
If you receive errors, you might have forgotten to install relevant packages (are working with Anaconda?). You did not run Elastic Search if you get the following warning: _WARNING:INCAcore.database:No database functionality available_. The _FutureWarning_ concerning re.datetools can be ignored.


Want to put some test data in your own ElasticSearch database? This is how to do it after starting ```ipython3``` (note that you have tab-completion!):

```
from inca import Inca
myinca = Inca()
myinca.rssscrapers.nu()   # run a scraper and put results in Elasticsearch
data = myinca.database.doctype_first('nu')  # retrieve one article from elasticsearch
print(data[0]['_source'].keys())
print(data[0]['_source']['text'])
```

## And now?

Please check the [Contributing Code Guide](https://github.com/uvacw/inca/blob/development/doc/contributing_code_guide.md) for the next steps!

Check out [Tips and tricks](https://github.com/uvacw/inca/blob/development/doc/tips_and_tricks.md) for more helpful commands.

## [OPTIONAL] Make INCA available as a module that can be imported from everywhere
If you are a USER of INCA (i.e., not a DEVELOPER; you do not really want to work on INCA an contribute, but just use it), you can now install Inca as a module that is available from anywhere on your system:

```
cd <pathtoyourincafolder>
sudo pip3 install .
```
If you want to work on INCA itself, you probably do NOT want to do it to avoid confusion.
