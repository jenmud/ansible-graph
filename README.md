# ansible-graph
A script that will scrape a ansible inventory or playbook and build a dependency graph representation.

This is still a work in progress!

## TO DO

* Resolve the includes and variables.
* Link hosts and groups to a role
* Get roles variables
* Get template files for a role
* Get files for a role
* Add in tests!!


# Installing and Developing

## Clone the project
```bash
$ git clone https://github.com/jenmud/ansible-graph.git
```

## Clone ansible examples
```bash
$ git clone https://github.com/ansible/ansible-examples
```

## Get it installed using a python virtualenv
```bash
$ virtualenv ansible-graph-ve
$ ansible-graph-ve/bin/pip install -U pip setuptools wheel
$ ansible-graph-ve/bin/pip install ansible-graph  # use -e to do a develop install.
```

## Running a scrape and starting a webserver
```bash
$ ansible-graph-ve/bin/ansible-graph --runserver -i ansible-examples/*/hosts -p ansible-examples/*/playbooks/*.yml
INFO:root:Updated ansible loader basedir to '/Volumes/Data/Programming/Repos'
INFO:root:Starting server 0.0.0.0:8000
INFO:ruruki_eye.server:Setting up db to <ruruki.graphs.Graph object at 0x10df1b150>
INFO:werkzeug: * Running on http://0.0.0.0:8000/ (Press CTRL+C to quit)
```

Open a web browser and navigate to the running address provided in the output above.
```
http://0.0.0.0:8080
```

Example of interesting output (assuming that vertice with name=mongo1 has the id *19*)
```
http://localhost:8000/vertices/19?levels=1
```

![Screenshot](/ansible-graph.png)




