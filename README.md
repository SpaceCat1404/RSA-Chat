# RSA-Chat
A one-one chat using RSA encryption
---
- the rsa.py contains the math as functions needed to perform rsa encryption with size 1024 bits
- On running the client_integrated and server_integrated files, they create the two nodes which communicate with one another. Running the server_integrated file twice will not work, but the two files ultimately carry the same functionality.
- The _integrated files ask for a login, which can be created by running the register_new file, the redirect hasn't been created yet so the file needs to be run manually
- to update and delete users, run the createupdatedelete file
- chat_app.db stores usernames and passwords using sql with basic encryption, not RSA
- This is the first version with several possible improvements, mentioned above.
