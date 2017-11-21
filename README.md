# Geney

## Developing Geney

1. You need to have both python3 and node. If you're on a Mac, you can install homebrew and then type into your terminal `brew install python3 node`. If you're on Linux, consult your distibutions's package manager on how to install these.

2. Go into the "site" folder and run an `npm install` in your terminal. This will install all of the javascript dependencies for the Geney website into a new folder called "node_modules".

3. Run the webpack server. While in the "sire" folder, run `npm run dev:ui` in your terminal. This will build all of the javascript for the UI, including all the `.vue` files, and start a server on port 8080. It will also auto-reload whenever you make changes to any javascript files.

4. Install all python dependencies using pip. In your terminal, run `pip3 install Flask==0.12.2 fastnumbers h5py jsonschema`.

5. In another terminal, run the python server. While in the "server" folder run `./app.py` in your terminal. This will start the Flask development server on port 9998. By default, the webpack server will proxy any requests made to any route starting with "/api" to port 9998, so make sure this is running before you try and use the site.

6. Add your awesome changes and make a pull request!


