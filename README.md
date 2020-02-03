# Open Source Image Duplicator - Python3

OSID offers a UI (in the form of a webpage) wrapper to dcfldd to assist in duplicating SD cards from a Raspberry Pi.


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### Hardware

- Raspberry Pi 2
- 32 GB SD Card
- Official Raspberry Pi Touch Display
- Monoprice powered USB hubs (7 ports) (4 total)
- Monoprice SD card readers (26 total, rpi2 will stall on any more)

### Prerequisites

What things you need to install the software and how to install them

```
dcfldd
Python3
Pip3
cherrypy (through pip)
```

### Installation and Deployment

TODO: Just run the setup script

```
sudo python3 setup.py
```

## Manual Installation

### Manual Install

Instructions is for Raspbian since this is designed to be ran on a Raspberry Pi.

Make sure you have python3 and pip3 and dcfldd.

```
sudo apt-get install python3 python3-pip dcfldd
```

and the CherryPy library.

```
sudo pip3 install cherrypy
```

Or

```
sudo pip3 install -r requirements.txt
```

To Do: Create an installation script to do it all.


### Manual Deployment

Navigate to the system folder and create the needed files from the sample files.

```
cd /path_to_folder/osid-python3/system
```

Inside there should be 3 files that we need to setup:

* server.ini
* run_app.sh
* osid.desktop

For now we'll just create those files from the samples.

```
mv server.ini.sample server.ini
mv run_app.sh.sample run_app.sh
mv osid.desktop.sample ~/Desktop/osid.desktop
```

Then proceed to modify those files to match the system paths for the items in those files.

#### server.ini

* ImagePath is the directory holding the .img files that can be used.
* Host is the hostname used for the webpage.
* SocketPort is the port you want to use to dish out the API links.
* Logs is the directory to hold all of your logs.
* SkeletonLocation is where you can find the Skeleton CSS Framework.
	* A Skeleton CSS file is included in www.
	* You can also pull a fresh copy of the [Skeleton-Framework](https://github.com/skeleton-framework/skeleton-framework) and define the location.

#### run_app.sh

* Run app will cd into the system folder, so define the installation path.
* It will then open up chromium-browser and navigate to the hostname and port.
	* So define the url that the browser will use to connect to the main page.

* Alternatively, you can decide to run OSID headless on a networked Raspberry. You can safely uncomment the chromuim line in run_app.sh. Don't forget to set local Raspbery Pi IP on server.ini

#### osid.desktop
* Just make sure the path for the run_app.sh script is defined properly.
* if you use OSID on headless Raspberry, this file is useless.

### Balena cloud deployment
change `balenaAppId` variable in system/balena.id to your `<balena_app_id>`
Deploy app to balena cloud

### Usage

#### Accepted image file
OSID will accept any image file ending with .img name. Other will silently be ignored.

#### Auto discovery of available readers
When refreshing web page (or accessing it), OSID will scan available readers, and after some seconds, will show them on the menu. A sum of all readers is also shown.

## Built With

* [Skeleton-Framework](https://github.com/skeleton-framework/skeleton-framework) - CSS framework used to structure Web UI
* [CherryPy](http://docs.cherrypy.org/en/latest/) - API Library for Python used to manage all actions
* [rockandscissor/OSID](https://github.com/rockandscissor/osid) - Base Project originally written in PHP and Bash

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Aaron Nguyen** - [aaronnguyen](https://github.com/aaronnguyen)

## License

This project is licensed under the GNU GPLv3 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks [PurpleBooth](https://gist.github.com/PurpleBooth) for the [Readme Template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
