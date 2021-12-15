# FIFA Tournament Companion (FTC)

FIFA Tournament Companion (FTC) is a tool for all you FIFA fools. It helps you to track all kinds of relevant and irrelevant information about your tournament.

## Installation

First clone this repository
```bash
git clone git@github.com:philipph77/fifa_tournament_companion.git
```

Everything you need is located the `app` folder. Navigate to the folder with your terminal.

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install FTC.

```bash
pip install .
```

Now everything should be installed and ready to set up. You will have to set two variables using
```bash
export FLASK_APP=ftc
export FLASK_ENV=development
```
<i>NOTE: Only use the option `development` for development purposes!</i>

Navigate your terminal into the `app` folder an try to initialize the database by running the command
```bash
flask init-db
```

## Usage
If everything is set up properly you can run the application with

```bash
flask run
```

You should see an ouput like:
```bash
* Serving Flask app "ftc"
* Environment: development
* Debug mode: on
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: 855-212-761
```

If you now navigate to http://127.0.0.1:5000/, you should see the login page

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Credits
- [Windmill Template](https://github.com/estevanmaito/windmill-dashboard)
- [Generate Season Algorithm](https://gist.github.com/ih84ds/be485a92f334c293ce4f1c84bfba54c9)

## License
[CCO](https://choosealicense.com/licenses/cc0-1.0/)