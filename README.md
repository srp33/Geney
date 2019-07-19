<img src="https://github.com/srp33/Geney/blob/master/site/ui/assets/geney-lamp.png" alt="Geney logo" width="40%" />

**You can find our current working prototype [here](http://piccololab.byu.edu). We are working to add more datasets and new functionality. If there is a publicly available dataset that you would like to be able to query with this tool, please let us know. Please also [let us know](https://github.com/srp33/Geney/issues) if you have feedback!**

Geney is a Web-based tool for querying large genomic datasets. You can filter data based on sample-level annotations, and you can select your specific genes of interest. Currently, Geney focuses mostly on genomic and transcriptomic data, but it is flexible enough to be able to handle other types of data, too.

## Developing Geney

If you would like to contribute to the development of Geney, please follow these instructions.

1. You need to have both python3 and node. If you're on a Mac, you can install homebrew and then type into your terminal `brew install python3 node`. If you're on Linux, consult your distribution's package manager on how to install these.

2. Go into the "site" folder and run an `npm install` in your terminal. This will install all of the javascript dependencies for the Geney website into a new folder called "node_modules".

3. Run the webpack server. While in the "site" folder, run `npm run dev:ui` in your terminal. This will build all of the javascript for the UI, including all the `.vue` files, and start a server on port 8080. It will also auto-reload whenever you make changes to any javascript files.

4. Install all python dependencies using pip. In your terminal, run `pip3 install Flask==0.12.2 fastnumbers h5py jsonschema`.

5. You will also need some datasets to work with. We currently have some stored on FSL that you can download, but you can just reach out to us get access to these files.

6. In another terminal, run the python server. While in the "server" folder run `GENEY_DATA_PATH=/path/to/datasets ./app.py` in your terminal. This will start the Flask development server on port 9998, and provide it with the environment variable required to find the datasets. By default, the webpack server will proxy any requests made to any route starting with "/api" to port 9998, so make sure this is running before you try and use the site.

7. Add your awesome changes and make a pull request!

## Deploying Geney

To deploy Geney using docker-compose, run the following, making sure to change the paths to the correct path on your machine:

```bash
export GENEY_DATA_PATH=/Applications/GeneyWishBuilder/WishBuilder-CLI/GeneyDatasets/
export DOWNLOAD_LOCATION=/Applications/Geney/server/downloads/
cd /Applications/Geney
docker-compose -f deployment.yml up -d
```
