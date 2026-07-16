FROM --platform=linux/amd64 rapid7/insightconnect-python-3-slim-plugin:6.6.0 AS builder

WORKDIR /workspace

ADD ./plugin.spec.yaml /plugin.spec.yaml
ADD ./requirements.txt /workspace/requirements.txt
ADD . /workspace



RUN pip install .
RUN pip uninstall -y setuptools

FROM --platform=linux/amd64 rapid7/insightconnect-python-3-slim-plugin:6.6.0

LABEL organization=rapid7_custom
LABEL sdk=python

# Install PowerShell and ExchangeOnlineManagement module
RUN apt-get -y update \
  && apt-get install -y curl gnupg apt-transport-https libicu76 --no-install-recommends \
  && mkdir -p /opt/microsoft/powershell/7 \
  && curl -fsSL https://github.com/PowerShell/PowerShell/releases/download/v7.5.4/powershell-7.5.4-linux-x64.tar.gz | tar -xz -C /opt/microsoft/powershell/7 \
  && chmod 755 /opt/microsoft/powershell/7/pwsh \
  && ln -s /opt/microsoft/powershell/7/pwsh /usr/bin/pwsh \
  && rm -rf /var/lib/apt/lists/* \
  && sh -c "yes | pwsh -Command 'Install-Module -Name PSWSMan -RequiredVersion 2.3.1'" \
  && pwsh -Command 'Install-WSMan' \
  && sh -c "yes | pwsh -Command 'Install-Module -Name ExchangeOnlineManagement -RequiredVersion 3.9.2'"

WORKDIR /workspace

COPY --from=builder /workspace /workspace
COPY --from=builder /plugin.spec.yaml /plugin.spec.yaml


RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

ENV PYTHONPATH="/workspace:${PYTHONPATH}"

RUN rm -rf /root/.cache;

# User to run plugin code. The two supported users are: root, nobody
USER root

ENTRYPOINT ["python", "/workspace/bin/icon_microsoft_office365_email_security"]
