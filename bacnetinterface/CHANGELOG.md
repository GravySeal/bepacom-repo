<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->


# 0.1.0

10/1/2022
- API now has more datatypes
- objectIdentifier, statusFlags became list.
- notificationClass added as object as well as a property to access through API.
- Multi State stateText and numberOfStates have been added.
- Attempting to get min and max presentValue's from objects now.
- Altered webUI page to be a little functional. It has 3 buttons you can press to call a service like I Am or Who Is.
- Formatting of code now uses Black and Isort.
- Removed unused packages from Dockerfile: 'nmap' and 'iproute2'.
- Added a read all command, so all devices can be read again on command.
- Bumped version to '0.1.0' as the add-on ready to be used.


## 0.0.5

02/01/2023
- Added write functionality through API
- Added multiple API points. You can find them through going to /docs
- Who Is and I Am can be received and sent through host network. This is possible through Home Assistant Supervised
- Add-on is now matching requirements for this project. Error handling etc. will be improved later, as will code optimisations.


## 0.0.4

21/12/2022
- Zeroconf removed, not functional for add-on. If this was a core add-on, would be using DHCP.
- FastAPI running on a separate thread
- Created BACnetIOHandler class to serve as BACnet application
- BACnet devices will automatically be subscribed to
- FastAPI program converts the BACnet dictionary it gets from BACnetIOHandler to a bite sized dictionary containing only the essentials for Home Assistant
- API can do get request on /apiv1/json
- Can connect to websocket on ws://ip:port/ws
- Websocket will automatically push updates on Change Of Value
- Changed icon to Bepacom logo


## 0.0.3

07/11/2022
- Added FastAPI to function as API in the future
- Changed webserver to Uvicorn
- Changed program to split into multiple files
- BACnet device can be detected
- WebUI can be loaded, it's just an example page now
- API and web UI are split into different paths, /apiv1/ and /webapp/
- Zeroconf added, unsure if functioning


## 0.0.2

31/10/2022
- WhoIsIAmProgram Running
- Nginx set up to work correctly with Flask webserver
- Flask and BACpypes happily working together <3


## 0.0.1

 21/10/2022
- Getting started...
