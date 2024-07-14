# CS1116 CA1
This was my submission for a [CS1116 Web Development 2]() assignment focused on server-side web development
For my submission, I created a social media web application, where users can anonynously submit short messages, and other users can 'like' posts or leave a comment on it.
The server was written using Flask and Python, I used sqlite as a database, and I utilised Jinja to render HTML templates with data from my sqlite DB.

# Configure & Run
- Firstly, clone this repository
`git clone --depth=1 git@github.com:/colmmurphyxyz/cs1116-ca1`
- Install dependencies with Pip
`python3 -m pip install -r requirements.txt`
- Before launching the server, we need to create and populate the database
- The schema directory contains a script [deploy_schema](schema/deploy_schema) to do this
  - This shell script will create the database in `app.db` along with 2 sql scripts to create the schema and populate it with gibberish data
```
cd schema
./deploy_schema
cd ..
```
  - The script may take a while to run, be patient!
- and to run the application
`python3 -m flask run`
