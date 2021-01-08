FROM continuumio/anaconda3

ADD . / /usr/local/lib/seir_4dvar/

RUN cd /usr/local/lib/seir_4dvar/ && pip3 install -r requirements.txt

EXPOSE 8888

CMD [ "opt/conda/bin/jupyter", "notebook", "--notebook-dir=/usr/local/lib/seir_4dvar/", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root" ]
