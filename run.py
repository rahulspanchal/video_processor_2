from app import create_app
from dotenv import load_dotenv
import os

load_dotenv()  # This loads variables from .env

app = create_app()

if __name__ == "__main__":
    app.run(debug=True,port=os.getenv("APP_PORT"))
