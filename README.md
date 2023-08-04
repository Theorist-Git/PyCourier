# PyCourier: 
### A simple, reliable and fast email package for python

* See `test.py` for a quick overview of the package's working.

## Getting Started

### Installation:


* Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the python modules required.

```bash
$ pip install PyCourier
```


### Usage:

* See the test.py

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## Author(s)

Contributor names and contact info
* Mayank vats : [Theorist-git](https://github.com/Theorist-Git)
  * Email: dev-theorist.e5xna@simplelogin.com

## Version History
See [commit history](https://github.com/Theorist-Git/PyCourier/commits/master)
* **1.1.0**
  * Switched to pathlib for managing paths.
  * Split send_courier method into 2 to reduce nesting and improve readability.
  * Multiple directories can now be created by PyCourier if specified file paths contain more than one non-existent
  directory.

* **1.0.0**
  * Added support for custom smtp servers and ports.
  * Added project to PYPI.
  * Users can now give their own path for encrypted files.
* **0.0.9a**
  * Updated `__str__` method and test.py file 
* **0.0.8a**
  * Encrypted zips now avoid directory structure using arcname in write().
* **0.0.7a**
  * All files are now encrypted.
* **0.0.6a**
  * Made paths os independent.
  * encrypted files are now stored separately in a folder.
* **0.0.5a**
  * Added support for multiple recipients.
  * Fixed typo in class name.
  * Updated test.py.
* **0.0.4a**
  * Users can now enter their own password.
  * Moved file attachment to a different function for cleaner and efficient code.
  * Other minor improvements.
* **0.0.3a**
  * Added support for encrypting pdfs.
* **0.0.2a**
  * Added support for multiple attachments.
  * Added a tutorial file.
  * `__str__` method included.
  * Added check for msg_type.
* **0.0.1a**
    * Initial Release

* **P.S: 0.1a means version 0.1 alpha**

## Documentation
#### TBD

## License

This project is licensed under the [GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/#) License - see LICENSE.txt file for more details.

Copyright (C) 2022 Mayank Vats
