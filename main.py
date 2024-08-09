from dotenv import load_dotenv
load_dotenv()

import globals

from app import MtSendApplication

def main():
    app = MtSendApplication()
    app.run()


if __name__ == '__main__':
    globals.DEV_MODE = True
    main()