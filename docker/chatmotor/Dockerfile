FROM chatmotor_base
ADD fabfile.py /content/fabfile.py
ADD chatmotor /content/chatmotor
ADD startup.sh /content/startup.sh
ADD requirements /content/requirements
RUN pip install -r /content/requirements/base.txt