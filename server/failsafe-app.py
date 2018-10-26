from flask_failsafe import failsafe
# this file is purely for development, so you can still reload the python server when it's running inside a docker container
@failsafe
def create_app():
  from app import app
  return app

if __name__ == '__main__':
    create_app().run(debug=True, host='0.0.0.0', port=8889)
