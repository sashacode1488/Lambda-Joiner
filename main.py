import sys
from PyQt5.QtWidgets import QApplication
from colorama import init, Fore, Style
from ui import LambdaJoinerApp

# Initialize colorama for colored console output
init()

# ASCII art to display on startup
ascii_art_string = """
    /\\_____/\\
   /  o   o  \\
  ( ==  Y  == )
   )         (
  (           )
 ( ( )   ( ) )
(__(__)___(__)__)
Lambda Joiner v1.0
created by catdev btw
My Github: bit.ly/catdev_github
thanks for using my software :)

plz support me
Bitcoin: bc1qctxclq8eqpp6prgx07eymw34ma4v5t69dkpdw5
Ethereum: 0x666195090354F0D6DDc3c8F7169CEC2427039332
"""
print(Fore.YELLOW + ascii_art_string + Style.RESET_ALL)

if __name__ == '__main__':
    # Create the application instance
    app = QApplication(sys.argv)
    
    # Create and show the main window from the UI module
    ex = LambdaJoinerApp()
    ex.show()
    
    # Start the application's event loop
    sys.exit(app.exec_())
