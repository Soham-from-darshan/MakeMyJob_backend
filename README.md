## Serverside Code for MakeMyJob:

- run tests and check the code coverage using these commands:
```
rm ./instance/*.db;coverage erase;coverage run --include='Application/**,instance/**,tests/**/test*.py' -m pytest -vv -rA;coverage report;coverage html
```

- run in debug mode:
```
rm ./instance/*.db;python3 debug.py
```

- run in production mode:
```
rm ./instance/*.db;python3 run.py
```
