Deployment
==========

GIT repository: ivt-tests

Deployment to test VM with rsync.
---------------------------------

Example:

rsync -av --exclude '.git*' --exclude 'logs*' --exclude '*.swp' --exclude '*.pyc' --exclude '__pycache__' ./tests/ root@ivt-newinfra:/home/vziv/newinfra/bundle/ivt_tests/tests/
