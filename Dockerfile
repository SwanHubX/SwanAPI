FROM ubuntu:22.04
RUN apt-get clean  && \ 
    apt-get update
    
RUN apt-get install -y python3 curl && \ 
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py  && \ 
    python3 get-pip.py && \ 
    pip3 install -U pip &&
    
RUN apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 

RUN pip3 install --no-cache-dir torch==1.8.1 

RUN echo "==> Clean up..."  && \ 
    rm -rf ~/.cache/pip
    
COPY . /app
WORKDIR /app
CMD ["predict.py:app"]