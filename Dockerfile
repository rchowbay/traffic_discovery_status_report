FROM python:3

LABEL author="Thomas.Miller@fidelissecurity.com"

ENV HALO_API_HOSTNAME='https://api.cloudpassage.com'
ENV HALO_API_PORT='443'
ENV HALO_API_VERSION='v1'
ENV OUTPUT_DIRECTORY='/tmp'

ARG HALO_API_KEY
ARG HALO_API_SECRET_KEY
ARG OUTPUT_DIRECTORY
ARG HALO_GROUP_ID

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./app.py"]