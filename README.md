# GVE_DevNet_DNAspaces_in_app_help_button

This demo uses DNA Spaces detect & locate functionality to located customers that requested in-store help via an customer loyalty app. 

## Solution Components
* Cisco DNA Spaces Location Cloud API
* Cisco Webex Teams SDK
* flask
* python
* html
* css

# Business Use Case
## IT Manager’s problem to be solved with this use case:

* **Needs:** Easier way to request in-store help for customers. 
* **Challenge (WHY?):** Customers often need to search for store staff to get help, and sometimes have problems finding someone. This decreases the customer satisfaction and can lead to decreased profit for the store.
* **Solution:** A help button in the customer loyalty app allows customers to request in-store help. With each help request, the store staff is notified about the current customer location and can thereby easily find and help the customer. Furthermore, the PoV prevents multiple employees helping the same person.
* **Business Outcomes:** Customers do not need to search for store staff for help anymore. This leads to an increased customer satisfaction and competitiveness for the store.

![Overview of PoV](/static/img/high_level_design.PNG)


# High Level Design Demo

![High level design of PoV](/static/img/high_level_design2.PNG)

# Getting Started
## Pre-requisites

* Cisco DNA Spaces Detect & Locate Lab (min. one campus/floor with map and 1 active client)
* Webex Teams account
* Min. 2 Webex Teams user email addresses 
* IaaS solution to host the code or ngrok to make application reachable via internet accessible URL  
* Chrome, Firefox or Microsoft Edge


## Installation

This app requires being reachable over an internet accessible URL. Therefore, it can be deployed on different IaaS plattform like Heroku, Amazon Web Services Lambda, Google Cloud Platform (GCP) and more. Alternatively, it is possible to use the tool ngrok for this reason, but please be aware that it can be blocked in corporate networks.

The installation can differ depending on the used IaaS solution. Hereby, the following section describes helpful commands, but no one-fits-all installation instructions.

1. Make sure Python 3 and Git is installed in your environment, and if not, you may download Python 3 [here](https://www.python.org/downloads/) and Git as described [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

2. Create and activate a virtual environment for the project ([Instructions](https://docs.python.org/3/tutorial/venv.html)).

3. Access the created virtual environment folder
    ```
    cd [add name of virtual environment here] 
    ```
4. Clone this Github repository:  
  ```git clone [add github link here]```
  * For Github link: 
      In Github, click on the **Clone or download** button in the upper part of the page > click the **copy icon**  
  * Or simply download the repository as zip file using 'Download ZIP' button and extract it

5. Access the downloaded folder:  
  ```cd GVE_DevNet_DNAspaces_in_app_help_button```

6. Install all dependencies:  
  ```pip3 install -r requirements.txt```
  
7. Create a [Webex Bot](https://developer.webex.com/docs/bots) and note the Bot token and name for the next step.

8. Set the required environment variables in the .env file
* **BASE_URL:** DNA Spaces Location Cloud API base url e.g. https://dnaspaces.eu/api/location/v1
* **BEARER:** DNA Spaces Location Cloud API Bearer
* **CLIENTMAC:** Mac address of simulated customer, available in DNA Spaces detect and locate. 
* **MAPIMAGE:** Name of map image available in DNA Spaces in which the simulated customer is located
* **FLOORID:** Floor ID of the floor associated with the DNA Spaces map, in which the simulated customer is located
* **WEBEX_TEAMS_BOT_NAME:** Name of the Webex Teams bot from step 7.
* **WEBEX_TEAMS_ACCESS_TOKEN:** Webex Teams bot token from step 7.
* **EXTERNAL_WEBHOOK_URL:** Internet accessible URL of the running application. Acts as external webhook base url.
* **NOTIFICATION_RECEIVER:** List of employees to receive a Webex notification on help request in the format: ["emai1@xxx.com", "email2@xxx.de"]

 > Note: Mac OS hides the .env file in the finder by default. View the demo folder for example with your preferred IDE to make the file visible.
 
 > Note: Create the DNA Spaces Location Cloud API Bearer as described under: https://developer.cisco.com/docs/dna-spaces/#!getting-started/getting-started
 
 
## Starting the Application

Run the script by using the command:
```
python3 app.py
```

### Demo

Access the application via the internet accessible URL. This application simulates a mobile device, therefore it is recommended to activate the mobile view in your browser for demo's via the browser. 

Activate the mobile view for IPhone 6/7/8 in Chrome by opening the menu (3 dots) > More Tools > Developer Tools > click the following icon for mobile view and choose iPhone 6/7/8 in the dropdown menu:

![Mobile View Button](/static/img/mobile_view.png)

### Screenshots

![screenshot1](/static/img/screenshot1.png)
![screenshot2](/static/img/screenshot2.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
